TERMUX_PKG_HOMEPAGE=https://github.com/gmoqa/listen
TERMUX_PKG_DESCRIPTION="Minimal audio transcription tool - 100% on-premise"
TERMUX_PKG_LICENSE="MIT"
TERMUX_PKG_MAINTAINER="@gmoqa"
TERMUX_PKG_VERSION=2.1.0
TERMUX_PKG_SRCURL=https://github.com/gmoqa/listen/archive/refs/tags/v${TERMUX_PKG_VERSION}.tar.gz
TERMUX_PKG_SHA256=90fdbf4aeb3db47aa8c58da34981d8ea7809faf733b1da0fb425bc8408010068
TERMUX_PKG_DEPENDS="libc++, openssl"
TERMUX_PKG_BUILD_DEPENDS="rust, cmake"
TERMUX_PKG_BUILD_IN_SRC=true

termux_step_make() {
	termux_setup_rust
	cargo build --release --locked --target $CARGO_TARGET_NAME
}

termux_step_make_install() {
	# Install the binary
	install -Dm700 target/$CARGO_TARGET_NAME/release/listen "$TERMUX_PREFIX/bin/listen"

	# Install documentation
	install -Dm600 README.md "$TERMUX_PREFIX/share/doc/listen/README.md"
}

termux_step_create_debscripts() {
	cat > ./postinst <<- EOF
	#!$TERMUX_PREFIX/bin/sh
	echo ""
	echo "listen installed successfully!"
	echo ""
	echo "Usage:"
	echo "  listen           # record and transcribe"
	echo "  listen -l es     # spanish"
	echo "  listen -m tiny   # faster model (recommended for mobile)"
	echo "  listen --vad 2   # auto-stop after 2s of silence"
	echo ""
	echo "Note: Use 'tiny' or 'base' models on mobile devices"
	echo ""
	echo "First run: Allow microphone access when prompted"
	echo ""
	EOF

	chmod 0755 postinst
}
