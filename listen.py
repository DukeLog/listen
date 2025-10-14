#!/usr/bin/env python3
import sys, os, tempfile, wave, time, threading, queue, fcntl, termios, re, signal

# Lazy imports (loaded only when needed)
np = None
sd = None
whisper = None

# ANSI escape codes
CLR = '\033[K'
HOME = '\033[2J\033[H'
RED = '\033[91m'
YEL = '\033[93m'
RST = '\033[0m'

# Audio configuration
SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = 'float32'

# VAD configuration
VAD_THRESHOLD = 0.015      # Volume threshold for silence detection
VAD_DEFAULT_DURATION = 2.0 # Default silence duration in seconds

# Server configuration
DEFAULT_SERVER_HOST = '0.0.0.0'
DEFAULT_SERVER_PORT = 5000

# Recording state
rec = []
lvl = [0.0]
pct = [0.0]
verbose = False
first_run = True
is_tty = sys.stdout.isatty()
stdin_is_tty = sys.stdin.isatty()
signal_stop = [False]
signal_mode = False
vad_enabled = False
vad_silence_duration = VAD_DEFAULT_DURATION
vad_threshold = VAD_THRESHOLD

def log(msg):
    if verbose:
        print(f'\n[DEBUG] {msg}', file=sys.stderr)


def signal_handler(signum, frame):
    """Handle SIGUSR1 to stop recording gracefully"""
    global signal_stop
    signal_stop[0] = True
    log(f'Received signal {signum}, stopping recording')


def audio_cb(data, frames, t, status):
    global np
    rec.append(data.copy())
    lvl[0] = float(np.sqrt(np.mean(data**2)))


def kbd_listen(q):
    if not stdin_is_tty:
        return

    try:
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        flg = fcntl.fcntl(fd, fcntl.F_GETFL)
    except (termios.error, OSError):
        # Termux or environments where terminal control is not available
        log('Terminal control not available, keyboard listener disabled')
        return

    try:
        new = termios.tcgetattr(fd)
        new[3] = new[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, new)
        fcntl.fcntl(fd, fcntl.F_SETFL, flg | os.O_NONBLOCK)

        while True:
            try:
                if sys.stdin.read(1) == ' ':
                    q.put(1)
                    break
            except (IOError, OSError, BlockingIOError):
                pass
            time.sleep(0.005)

        termios.tcsetattr(fd, termios.TCSAFLUSH, old)
        fcntl.fcntl(fd, fcntl.F_SETFL, flg)
    except Exception as e:
        log(f'Keyboard listener error: {e}')
        pass


def draw(c, bars, txt='Listening'):
    # Always show UI on stderr when not TTY (piped), or stdout when TTY
    out = sys.stderr if not is_tty else sys.stdout
    out.write(f'\r{RED}●{RST} {txt}  [{c}{bars}{RST}]')
    out.flush()


def record(start_proc):
    global rec, np, sd, signal_stop

    log('Loading audio libraries')
    if not np:
        import numpy
        np = numpy
        log('NumPy loaded')
    if not sd:
        import sounddevice
        sd = sounddevice
        log('SoundDevice loaded')

    rec = []
    q = queue.Queue()

    # Only start keyboard listener if not in signal mode
    if not signal_mode:
        log('Starting keyboard listener thread')
        threading.Thread(target=kbd_listen, args=(q,), daemon=True).start()

    draw('', ' ' * 10)

    if first_run and stdin_is_tty and not signal_mode:
        time.sleep(0.3)
        print(f'\n\n  Press SPACE to stop recording', file=sys.stderr)
        # Hint for Termux/mobile users
        if os.getenv('PREFIX'):  # Termux environment
            print(f'  Tip: Use --vad 2 for auto-stop on silence\n', file=sys.stderr)
        else:
            print(f'', file=sys.stderr)
        time.sleep(1.5)
        out = sys.stderr if not is_tty else sys.stdout
        out.write(HOME)
        out.flush()
        draw('', ' ' * 10)
    elif signal_mode:
        # Print signal mode instructions
        pid = os.getpid()
        print(f'\n\n  Signal mode: Send SIGUSR1 to stop (pid: {pid})\n', file=sys.stderr)
        print(f'  Example: kill -SIGUSR1 {pid}\n', file=sys.stderr)
        time.sleep(1.5)
        out = sys.stderr if not is_tty else sys.stdout
        out.write(HOME)
        out.flush()
        draw('', ' ' * 10)
    elif vad_enabled:
        # Print VAD mode instructions
        print(f'\n\n  VAD mode: Will stop after {vad_silence_duration}s of silence\n', file=sys.stderr)
        time.sleep(1.5)
        out = sys.stderr if not is_tty else sys.stdout
        out.write(HOME)
        out.flush()
        draw('', ' ' * 10)

    log(f'Starting audio stream ({SAMPLE_RATE//1000}kHz, {"stereo" if CHANNELS == 2 else "mono"})')
    # In signal mode or VAD mode, no timeout - wait for signal/silence
    # Otherwise, use timeout when piped (not TTY)
    timeout = None if (signal_mode or vad_enabled) else (10 if not stdin_is_tty else None)

    # VAD tracking variables
    silence_start = None
    has_speech = False

    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=DTYPE, callback=audio_cb):
            t0 = time.time()
            while True:
                draw('', '=' * min(int(lvl[0] * 200), 10) + ' ' * max(10 - int(lvl[0] * 200), 0))

                # Check signal stop (for signal mode)
                if signal_mode and signal_stop[0]:
                    dur = time.time() - t0
                    log(f'Recording stopped by signal after {dur:.2f}s')
                    break

                # VAD: Check for silence
                if vad_enabled:
                    current_level = lvl[0]

                    # Detect if currently silent
                    is_silent = current_level < vad_threshold

                    if not is_silent:
                        # Speech detected
                        has_speech = True
                        silence_start = None
                        log(f'Speech detected (level: {current_level:.4f})')
                    elif has_speech:
                        # Silence after speech
                        if silence_start is None:
                            silence_start = time.time()
                            log(f'Silence started (level: {current_level:.4f})')
                        else:
                            silence_duration = time.time() - silence_start
                            if silence_duration >= vad_silence_duration:
                                dur = time.time() - t0
                                log(f'Recording stopped after {silence_duration:.2f}s of silence (total: {dur:.2f}s)')
                                break

                # Check timeout when piped
                if timeout and (time.time() - t0) >= timeout:
                    log(f'Recording stopped after timeout ({timeout}s)')
                    break

                # Check keyboard input (only if not in signal mode)
                if not signal_mode:
                    try:
                        if q.get_nowait():
                            dur = time.time() - t0
                            log(f'Recording stopped after {dur:.2f}s')
                            break
                    except queue.Empty:
                        pass

                time.sleep(0.05)
    except Exception as e:
        log(f'Error during recording: {e}')
        print(f'\n{e}', file=sys.stderr)
        return None

    for _ in range(3):
        draw('', '=' * 10)
        time.sleep(0.15)
        draw('', ' ' * 10)
        time.sleep(0.15)

    start_proc()

    if rec:
        frames = len(rec)
        log(f'Concatenating {frames} audio frames')
        data = np.concatenate(rec)
        if data.ndim > 1:
            data = data.flatten()
        return data
    else:
        log('No audio recorded')
        return None


def transcribe(path, model, lang, run=None, blink_state=None):
    global whisper, pct

    log(f'Loading Whisper model: {model}')
    if not whisper:
        import whisper as w
        whisper = w
        log('Whisper library loaded')

    try:
        t0 = time.time()
        m = whisper.load_model(model)
        log(f'Model loaded in {time.time()-t0:.2f}s')

        if blink_state:
            while (blink_state[0] // 6) % 2 != 0:
                time.sleep(0.01)
            pct[0] = 0.2

        class P:
            def write(self, txt):
                if verbose and txt.strip():
                    print(f'[WHISPER] {txt.strip()}', file=sys.__stderr__)
                if '%' in txt and (x := re.search(r'(\d+)%', txt)):
                    if blink_state:
                        pct[0] = 0.2 + int(x.group(1)) / 100.0 * 0.8
            def flush(self): pass

        old = sys.stderr
        sys.stderr = P()

        log(f'Starting transcription (language={lang})')
        t0 = time.time()
        r = m.transcribe(path, language=lang, fp16=False, verbose=False)
        log(f'Transcription completed in {time.time()-t0:.2f}s')
        log(f'Detected language: {r.get("language", "unknown")}')
        log(f'Text length: {len(r["text"])} chars')

        sys.stderr = old
        if blink_state:
            pct[0] = 1.0
            time.sleep(0.1)
    finally:
        time.sleep(0.05)

    return r


def start_server(host=DEFAULT_SERVER_HOST, port=DEFAULT_SERVER_PORT, model='base', lang='en'):
    """Start Flask server for audio transcription API"""
    global whisper, verbose

    # Lazy import - only load Flask if server mode is used
    try:
        from flask import Flask, request, jsonify
    except ImportError:
        print('Error: Flask is required for server mode', file=sys.stderr)
        print('Install: pip install flask', file=sys.stderr)
        sys.exit(1)

    app = Flask(__name__)

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok'})

    @app.route('/transcribe', methods=['POST'])
    def transcribe_audio():
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Get optional parameters
        req_lang = request.form.get('language', lang)
        req_model = request.form.get('model', model)

        # Save uploaded file to temp location
        tmp = tempfile.NamedTemporaryFile(suffix='.audio', delete=False)
        try:
            audio_file.save(tmp.name)
            tmp.close()

            log(f'Received file: {audio_file.filename} ({os.path.getsize(tmp.name)} bytes)')
            log(f'Transcribing with model={req_model}, language={req_lang}')

            # Transcribe without UI elements (no run/blink_state)
            result = transcribe(tmp.name, req_model, req_lang)

            return jsonify({
                'text': result['text'].strip(),
                'language': result.get('language', req_lang)
            })
        except Exception as e:
            log(f'Transcription error: {e}')
            return jsonify({'error': str(e)}), 500
        finally:
            try:
                os.unlink(tmp.name)
            except:
                pass

    print(f'Starting transcription API server on {host}:{port}')
    print(f'Model: {model}, Language: {lang}')
    print(f'\nEndpoints:')
    print(f'  GET  /health     - Health check')
    print(f'  POST /transcribe - Transcribe audio file')
    print(f'\nExample usage:')
    print(f'  curl -X POST -F "audio=@file.mp3" http://{host}:{port}/transcribe')
    print(f'\nPress Ctrl+C to stop the server\n')

    app.run(host=host, port=port, debug=False)


def main():
    global verbose, first_run

    marker = os.path.expanduser('~/.local/share/listen/.first_run_done')
    if os.path.exists(marker):
        first_run = False
    else:
        os.makedirs(os.path.dirname(marker), exist_ok=True)
        with open(marker, 'w') as f:
            f.write('')

    # Clear screen on the appropriate stream
    out = sys.stderr if not is_tty else sys.stdout
    out.write(HOME)
    out.flush()

    lang = 'en'
    mdl = 'base'
    use_claude = False
    server_mode = False
    server_host = DEFAULT_SERVER_HOST
    server_port = DEFAULT_SERVER_PORT

    for i, a in enumerate(sys.argv[1:]):
        if a in ['-l', '--language'] and i + 2 < len(sys.argv):
            lang = sys.argv[i + 2]
        elif a in ['-m', '--model'] and i + 2 < len(sys.argv):
            mdl = sys.argv[i + 2]
        elif a in ['-c', '--claude']:
            use_claude = True
        elif a in ['-s', '--server']:
            server_mode = True
        elif a in ['--signal-mode']:
            global signal_mode
            signal_mode = True
        elif a in ['--vad'] and i + 2 < len(sys.argv):
            global vad_enabled, vad_silence_duration
            vad_enabled = True
            vad_silence_duration = float(sys.argv[i + 2])
        elif a in ['--host'] and i + 2 < len(sys.argv):
            server_host = sys.argv[i + 2]
        elif a in ['--port'] and i + 2 < len(sys.argv):
            server_port = int(sys.argv[i + 2])
        elif a in ['-v', '--verbose']:
            verbose = True
        elif a in ['-h', '--help']:
            print("usage: listen [-l LANG] [-m MODEL] [-c] [-s] [--signal-mode] [--vad SECONDS] [-v]")
            print("\nModes:")
            print("  (default)       Record audio from microphone and transcribe")
            print("  -s, --server    Start HTTP API server for transcription")
            print("\nOptions:")
            print("  -l, --language LANG     Language code (default: en)")
            print("  -m, --model MODEL       Whisper model (default: base)")
            print("  -c, --claude            Send transcription to Claude")
            print("  --signal-mode           Use SIGUSR1 signal to stop recording")
            print("  --vad SECONDS           Auto-stop after N seconds of silence (default: 2)")
            print("  -v, --verbose           Verbose output")
            print("\nServer options:")
            print(f"  --host HOST             Server host (default: {DEFAULT_SERVER_HOST})")
            print(f"  --port PORT             Server port (default: {DEFAULT_SERVER_PORT})")
            print("\nRecording mode:")
            print("  (default) Press SPACE to stop recording")
            print("  (signal)  Send SIGUSR1 to process (kill -SIGUSR1 <pid>)")
            print("  (vad)     Auto-stop after silence duration")
            return

    # Server mode
    if server_mode:
        start_server(host=server_host, port=server_port, model=mdl, lang=lang)
        return

    # Configure signal handler if in signal mode
    if signal_mode:
        signal.signal(signal.SIGUSR1, signal_handler)
        log('Signal mode enabled: listening for SIGUSR1')

    log(f'Starting listen (language={lang}, model={mdl})')

    global pct
    run = [True]
    blink_state = [0]

    def start_proc():
        def prog():
            while run[0]:
                n = int(pct[0] * 10)
                if pct[0] < 0.15:
                    bars = ('=' if (blink_state[0] // 6) % 2 == 0 else ' ') + ' ' * 9
                else:
                    bars = '=' * max(1, n) + ' ' * (10 - max(1, n))
                blink_state[0] += 1
                draw(YEL, bars, 'Processing')
                time.sleep(0.05)
        threading.Thread(target=prog, daemon=True).start()
        pct[0] = 0.0

    data = record(start_proc)
    if data is None or len(data) == 0:
        log('No audio data to process')
        sys.exit(1)

    log(f'Audio data shape: {data.shape}, duration: {len(data)/SAMPLE_RATE:.2f}s')

    tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    log(f'Saving audio to temp file: {tmp.name}')
    with wave.open(tmp.name, 'wb') as w:
        w.setnchannels(CHANNELS)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes((data * 32767).astype(np.int16).tobytes())
    log(f'Audio file size: {os.path.getsize(tmp.name)} bytes')

    try:
        r = transcribe(tmp.name, mdl, lang, run, blink_state)
        # Clear the UI line on the appropriate stream
        out = sys.stderr if not is_tty else sys.stdout
        out.write('\r' + CLR)
        out.flush()
        log(f'Final transcription: "{r["text"].strip()}"')

        text = r['text'].strip()

        if use_claude:
            # Send transcribed text as prompt to claude
            import subprocess
            import shlex
            log(f'Sending to claude as prompt: "{text}"')

            # Try common claude paths
            claude_path = os.path.expanduser('~/.claude/local/claude')
            if not os.path.exists(claude_path):
                claude_path = 'claude'

            try:
                # Use shell=True to support aliases, properly escape text
                cmd = f'{claude_path} -p {shlex.quote(text)}'
                subprocess.run(cmd, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f'Error running claude: {e}', file=sys.stderr)
                sys.exit(1)
        else:
            print(text, flush=True)
    except Exception as e:
        log(f'Transcription error: {e}')
        sys.exit(1)
    finally:
        run[0] = False
        try:
            os.unlink(tmp.name)
            log(f'Deleted temp file: {tmp.name}')
        except:
            pass


if __name__ == '__main__':
    main()
