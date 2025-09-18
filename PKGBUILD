# Maintainer: Guillermo Quinteros <gu.quinteros@gmail.com>
pkgname=listen
pkgver=1.1.1
pkgrel=1
pkgdesc="Minimal audio transcription tool - 100% on-premise"
arch=('any')
url="https://github.com/gmoqa/listen"
license=('MIT')
depends=('python' 'python-numpy' 'python-sounddevice' 'portaudio' 'ffmpeg')
makedepends=('python-pip')
source=("$pkgname-$pkgver.tar.gz::https://github.com/gmoqa/listen/archive/refs/tags/v$pkgver.tar.gz")
sha256sums=('82cdb6aad00325f7d770a9aed904bdcea0056c53de44e29a5861e76e0926a182')

build() {
  cd "$pkgname-$pkgver"
  pip install --target="$srcdir/python-deps" --no-deps openai-whisper
}

package() {
  cd "$pkgname-$pkgver"

  install -Dm755 listen.py "$pkgdir/usr/bin/listen"

  python_version=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
  install -dm755 "$pkgdir/usr/lib/python$python_version/site-packages"
  cp -r "$srcdir/python-deps/"* "$pkgdir/usr/lib/python$python_version/site-packages/"

  install -Dm644 README.md "$pkgdir/usr/share/doc/$pkgname/README.md"
  install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
