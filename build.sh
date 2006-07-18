#!/bin/bash
#
# Builds MyPLC, either inside the MyPLC development environment in
# devel/root (if PLC_DEVEL_BOOTSTRAP is true), or in the current host
# environment (may be itself a MyPLC development environment or a
# Fedora Core 4 environment with the appropriate development packages
# installed).
#
# root.img (loopback image)
# root/ (mount point)
# data/ (various data files)
# data/etc/planetlab/ (configuration files)
#
# Mark Huang <mlhuang@cs.princeton.edu>
# Copyright (C) 2006 The Trustees of Princeton University
#
# $Id$
#

. build.functions

#
# Build myplc inside myplc-devel. Infinite recursion is avoided only
# if PLC_DEVEL_BOOTSTRAP is false in the default configuration file.
#

if [ "$PLC_DEVEL_BOOTSTRAP" = "true" ] ; then
    # So that we don't pollute the actual myplc-devel image, we use
    # the directory that was used to build the image instead of the
    # image itself, and mount everything by hand.
    mount -o bind,rw devel/data devel/root/data
    mount -t proc none devel/root/proc

    # If we used a local mirror, bind mount it into the chroot so that
    # we can use it again.
    if [ "${PLC_DEVEL_FEDORA_URL:0:7}" = "file://" ] ; then
	mkdir -p devel/root/usr/share/mirrors/fedora
	mount -o bind,ro ${PLC_DEVEL_FEDORA_URL#file://} devel/root/usr/share/mirrors/fedora
    fi

    # Clean up before exiting if anything goes wrong
    trap "umount $PWD/devel/root/data;
          umount $PWD/devel/root/proc;
          umount $PWD/devel/root/usr/share/mirrors/fedora" ERR INT

    # Build myplc inside myplc-devel. Make sure PLC_DEVEL_BOOTSTRAP is
    # false to avoid infinite recursion.
    chroot devel/root su - <<EOF
set -x
service plc start
plc-config --category=plc_devel --variable=bootstrap --value="false" --save
service plc reload
cd /
cvs -d /cvs checkout build
make -C /build myplc
EOF

    # Yoink the image that was just built
    mv devel/data/build/BUILD/myplc-*/myplc/root{,.img} devel/data/build/BUILD/myplc-*/myplc/data .

    # Clean up
    umount devel/root/data
    umount devel/root/proc
    umount devel/root/usr/share/mirrors/fedora || :
    rm -rf devel/data/build
    mkdir -p devel/data/build

    # No need to continue
    exit 0
fi

#
# Build myplc in the host environment. This section is executed if
# PLC_DEVEL_BOOTSTRAP is false.
#

echo "* myplc: Installing base filesystem"
mkdir -p root data
make_chroot root plc_config.xml

# Build schema
echo "* myplc: Building database schema"
make -C $srcdir/pl_db

# Install configuration scripts
echo "* myplc: Installing configuration scripts"
install -D -m 755 plc_config.py root/tmp/plc_config.py
chroot root sh -c 'cd /tmp; python plc_config.py build; python plc_config.py install'
install -D -m 755 plc-config root/usr/bin/plc-config
install -D -m 755 api-config root/usr/bin/api-config
install -D -m 755 db-config root/usr/bin/db-config
install -D -m 755 dns-config root/usr/bin/dns-config

# Install initscripts
echo "* myplc: Installing initscripts"
find plc.d | cpio -p -d -u root/etc/
install -D -m 755 guest.init root/etc/init.d/plc
chroot root sh -c 'chkconfig --add plc; chkconfig plc on'

# Install DB schema and API code
echo "* myplc: Installing DB schema and API code"
mkdir -p root/usr/share
rsync -a $srcdir/pl_db $srcdir/plc_api root/usr/share/

# Install web scripts
echo "* myplc: Installing web scripts"
mkdir -p root/usr/bin
install -m 755 \
    $srcdir/plc/scripts/gen-sites-xml.py \
    $srcdir/plc/scripts/gen-slices-xml-05.py \
    $srcdir/plc/scripts/gen-static-content.py \
    root/usr/bin/

# Install web pages
echo "* myplc: Installing web pages"
mkdir -p root/var/www/html
# Exclude old cruft, unrelated GENI pages, and official documents
rsync -a \
    --exclude='*2002' --exclude='*2003' \
    --exclude=geni --exclude=PDN --exclude=Talks \
    $srcdir/plc_www/ root/var/www/html/

# Install configuration file
echo "* myplc: Installing configuration file"
install -D -m 444 $config data/etc/planetlab/default_config.xml
install -D -m 444 plc_config.dtd data/etc/planetlab/plc_config.dtd

# Move "data" directories out of the installation
datadirs=(
/etc/planetlab
/var/lib/pgsql
/var/www/html/alpina-logs
/var/www/html/boot
/var/www/html/download
/var/www/html/generated
/var/www/html/install-rpms
/var/www/html/xml
)

move_datadirs root data "${datadirs[@]}"

# Initialize node RPMs directory. The PlanetLab-Bootstrap.tar.bz2
# tarball already contains all of the node RPMs pre-installed. Only
# updates or optional packages should be placed in this directory.
if [ -n "$RPM_BUILD_DIR" ] ; then
    echo "* myplc: Initializing node RPMs directory"
    RPM_RPMS_DIR=$(cd $(dirname $RPM_BUILD_DIR)/RPMS && pwd -P)
    mkdir -p data/var/www/html/install-rpms/planetlab
    if [ -f $RPM_RPMS_DIR/yumgroups.xml ] ; then
	install -D -m 644 $RPM_RPMS_DIR/yumgroups.xml \
	    data/var/www/html/install-rpms/planetlab/yumgroups.xml
    fi
    # yum-2.0.x
    if [ -x /usr/bin/yum-arch ] ; then
	yum-arch data/var/www/html/install-rpms/planetlab
    fi
    # yum-2.4.x
    if [ -x /usr/bin/createrepo ] ; then
	if [ -f data/var/www/html/install-rpms/planetlab/yumgroups.xml ] ; then
	    groupfile="-g yumgroups.xml"
	fi
	createrepo $groupfile data/var/www/html/install-rpms/planetlab
    fi
fi

# Make image out of directory
echo "* myplc: Building loopback image"
make_image root root.img

exit 0
