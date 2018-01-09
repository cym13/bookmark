# Maintainer: Cédric Picard <cpicard@openmailbox.org>

pkgname=bm
pkgver=1.6.3
pkgrel=1
pkgdesc="Simple command line browser independant bookmark and tagging utility"
arch=(any)
url="https://github.com/cym13/bookmark"
license=('GPL')
depends=('python>=3'
         'python-docopt'
         'python-msgpack'
         'python-requests'
         'python-setuptools')
source=("https://github.com/cym13/bookmark/archive/aa24dc0a55135e6f1d13ba8017d936cd68278264.zip")
sha512sums=('95615384bae2e9622add8eb6e59a0f4e86d4fb04231df00dd9876429e2c7e4d0a691ba19c01dcb8dff6782b90205a1478543fed3ceef3b55ce88224a5a90e9c7')

package() {
    cd "$srcdir/bookmark-aa24dc0a55135e6f1d13ba8017d936cd68278264"
    python3 setup.py install --root="$pkgdir/" --optimize=1
}
