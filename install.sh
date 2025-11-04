#!/bin/bash
set -e

INSTALL_DIR="$HOME/.local/bin"
APP_DIR="$HOME/.local/share/listen"

echo "Installing listen..."

mkdir -p "$INSTALL_DIR"
mkdir -p "$APP_DIR"

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    echo "Install it from: https://www.python.org/downloads/"
    exit 1
fi

cp listen.py "$APP_DIR/"
cp requirements.txt "$APP_DIR/"

if [ ! -d "$APP_DIR/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$APP_DIR/venv"
    source "$APP_DIR/venv/bin/activate"
    pip install --quiet --upgrade pip
    pip install --quiet -r "$APP_DIR/requirements.txt"
else
    echo "Virtual environment already exists."
fi

cat > "$INSTALL_DIR/listen" << 'EOF'
#!/bin/bash
source "$HOME/.local/share/listen/venv/bin/activate"
exec python "$HOME/.local/share/listen/listen.py" "$@"
EOF

chmod +x "$INSTALL_DIR/listen"

if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo ""
    echo "Add this to your ~/.zshrc or ~/.bashrc:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
fi

echo "✓ Installed successfully!"
echo ""
echo "Usage:"
echo "  listen           # record and transcribe (english)"
echo "  listen -l es     # spanish"
echo "  listen -m medium # better model"
echo ""
echo "Press SPACE to stop recording"
