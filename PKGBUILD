# Maintainer: Aaron Reichenbach <aaron@scavengers.io>
pkgname=python-ddns
pkgver=0.1.0
pkgrel=1
pkgdesc="Python DDNS updater"
arch=('any')
url="https://github.com/aaron-panic/python-ddns"
license=('AGPL-3.0-only')
depends=('python')
source=("git+https://github.com/aaron-panic/python-ddns.git")
sha256sums=('SKIP')

package() {
    # Create directories
    install -dm755 "$pkgdir/opt/python-ddns"
    install -dm755 "$pkgdir/etc/python-ddns"
    install -dm755 "$pkgdir/var/lib/ddns"
    install -dm755 "$pkgdir/var/log/ddns"

    # Install python files
    install -Dm755 "$srcdir/python-ddns/ddns.py"   "$pkgdir/opt/python-ddns/ddns.py"
    install -Dm644 "$srcdir/python-ddns/config.py"  "$pkgdir/opt/python-ddns/config.py"
    install -Dm644 "$srcdir/python-ddns/logger.py"  "$pkgdir/opt/python-ddns/logger.py"

    # Install systemd unit
    install -Dm644 "$srcdir/python-ddns/python-ddns.service" \
        "$pkgdir/etc/systemd/system/python-ddns.service"

    # Create state file with default IP
    install -dm755 "$pkgdir/var/lib/ddns"
    echo "0.0.0.0" > "$pkgdir/var/lib/ddns/ip_addr"
}