# listen

minimal audio transcription tool

100% on-premise, no data sent to cloud

## install

```sh
curl -sSL https://raw.githubusercontent.com/gmoqa/listen/main/install.sh | bash
```

or download and run:
```sh
git clone https://github.com/gmoqa/listen.git
cd listen
./install.sh
```

## usage

```sh
listen              # record and transcribe (english)
listen -l es        # spanish
listen -m medium    # better model
```

press SPACE to stop recording

## models

- tiny
- base (default)
- small
- medium
- large

## uninstall

```sh
rm -rf ~/.local/share/listen ~/.local/bin/listen
```

all processing happens locally on your device
