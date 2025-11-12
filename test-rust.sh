#!/bin/bash
set -e

echo "🦀 Testing Rust implementation of listen"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

BINARY="./target/release/listen"
MODEL_DIR="$HOME/.cache/whisper"
MODEL_FILE="$MODEL_DIR/ggml-base.bin"
TEST_WAV="test_audio.wav"

# Step 1: Check binary exists
echo -e "${BLUE}[1/4]${NC} Checking if binary is compiled..."
if [ ! -f "$BINARY" ]; then
    echo "  Building release binary..."
    cargo build --release
fi
echo -e "  ${GREEN}✓${NC} Binary ready: $BINARY ($(ls -lh $BINARY | awk '{print $5}'))"
echo ""

# Step 2: Download whisper model if needed
echo -e "${BLUE}[2/4]${NC} Checking whisper model..."
if [ ! -f "$MODEL_FILE" ]; then
    echo "  Model not found. Downloading ggml-base.bin (~140MB)..."
    mkdir -p "$MODEL_DIR"
    wget -q --show-progress \
        https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin \
        -O "$MODEL_FILE"
    echo -e "  ${GREEN}✓${NC} Model downloaded to $MODEL_FILE"
else
    echo -e "  ${GREEN}✓${NC} Model already exists: $MODEL_FILE"
fi
echo ""

# Step 3: Create test audio file (1 second of silence at 16kHz)
echo -e "${BLUE}[3/4]${NC} Creating test audio file..."
if [ ! -f "$TEST_WAV" ]; then
    # Create 1 second of silence at 16kHz mono
    ffmpeg -f lavfi -i anullsrc=r=16000:cl=mono -t 1 -q:a 9 -acodec pcm_s16le "$TEST_WAV" -y 2>/dev/null
    echo -e "  ${GREEN}✓${NC} Test file created: $TEST_WAV"
else
    echo -e "  ${GREEN}✓${NC} Test file exists: $TEST_WAV"
fi
echo ""

# Step 4: Run tests
echo -e "${BLUE}[4/4]${NC} Running tests..."
echo ""

# Test 1: Help
echo -e "${YELLOW}Test 1: --help${NC}"
$BINARY --help | head -5
echo ""

# Test 2: Version
echo -e "${YELLOW}Test 2: --version${NC}"
$BINARY --version
echo ""

# Test 3: Transcribe test file
echo -e "${YELLOW}Test 3: Transcribe test file (silent)${NC}"
$BINARY -f "$TEST_WAV" --model base --quiet
echo -e "${GREEN}✓${NC} Transcription completed (silence produces empty or minimal output)"
echo ""

# Test 4: JSON output
echo -e "${YELLOW}Test 4: JSON output${NC}"
$BINARY -f "$TEST_WAV" --json --quiet | head -5
echo ""

echo -e "${GREEN}✅ All tests passed!${NC}"
echo ""
echo "Next steps:"
echo "  1. Record real audio:  $BINARY --model base"
echo "  2. Transcribe file:    $BINARY -f your_audio.wav"
echo "  3. Spanish:            $BINARY -l es"
echo "  4. With VAD:           $BINARY --vad 2.0"
echo ""
