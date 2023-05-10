SUMMARY = "small test sample for qtwebkit, hello qt"
SECTION = "multimedia"
LICENSE = "GPLv2+"
PACKAGE_ARCH := "${MACHINE_ARCH}"

require conf/license/license-gplv2.inc

DEPENDS  = "qtwebkit"

PR = "r0"

SRC_URI = "file://helloqt.zip"

S = "${WORKDIR}/helloqt"

inherit qmake5

FILES:${PN} = "${bindir}/helloqt"

do_install(){
    install -d ${D}${bindir}
    install -m 0755 ../build/bin/helloqt ${D}${bindir}/helloqt
}

do_package_qa() {
}

pkg_postinst_ontarget:${PN}(){
#!/bin/sh
ln -sf /usr/share/fonts /usr/lib/fonts
exit 0
}
