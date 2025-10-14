#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "Installing listen for Termux..."
echo ""

# Check if running in Termux
if [ -z "$PREFIX" ]; then
    echo "Error: This script must be run in Termux"
    exit 1
fi

# Update package list
echo "Updating package list..."
pkg update -y

# Install system dependencies
echo "Installing system dependencies..."
pkg install -y python portaudio ffmpeg

# Setup storage permissions
echo ""
echo "Setting up storage permissions..."
termux-setup-storage
echo "Please allow storage access when prompted"
sleep 2

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install openai-whisper sounddevice numpy scipy

# Download listen.py
echo ""
echo "Downloading listen..."
curl -sSL https://raw.githubusercontent.com/gmoqa/listen/main/listen.py -o "$PREFIX/bin/listen"
chmod +x "$PREFIX/bin/listen"

# Test microphone access
echo ""
echo "Testing microphone access..."
if command -v termux-microphone-record &> /dev/null; then
    echo "Microphone API available"
else
    echo "Installing termux-api..."
    pkg install -y termux-api
fi

echo ""
echo "✓ Installation complete!"
echo ""
echo "Usage:"
echo "  listen           # record and transcribe"
echo "  listen -l es     # spanish"
echo "  listen -m tiny   # faster model (recommended for mobile)"
echo ""
echo "Note: Use 'tiny' or 'base' models on mobile devices"
echo "      Larger models may crash due to memory limits"
echo ""
echo "First run: Please allow microphone access when prompted"
