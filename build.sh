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
# data/root (root's homedir)
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
	mkdir -p devel/root/data/fedora
	mount -o bind,ro ${PLC_DEVEL_FEDORA_URL#file://} devel/root/data/fedora
    fi

    # Clean up before exiting if anything goes wrong
    trap "umount $PWD/devel/root/data/fedora;
          umount $PWD/devel/root/data;
          umount $PWD/devel/root/proc" ERR INT

    # Build myplc inside myplc-devel. Make sure PLC_DEVEL_BOOTSTRAP is
    # false to avoid infinite recursion.
    chroot devel/root su - <<EOF
set -x
service plc start
plc-config --category=plc_devel --variable=bootstrap --value="false" --save
service plc reload
cd /
cvs -d /cvs checkout -r $BUILD_TAG build
make TAG=$BUILD_TAG -C /build myplc
EOF

    # Yoink the image that was just built
    mv devel/data/build/BUILD/myplc-*/myplc/root{,.img} devel/data/build/BUILD/myplc-*/myplc/data .

    # Clean up
    umount devel/root/data/fedora || :
    umount devel/root/data
    umount devel/root/proc
    rm -rf devel/data/build
    mkdir -p devel/data/build

    # No need to continue
    exit 0
fi

#
# Build myplc in the host environment. This section is executed if
# PLC_DEVEL_BOOTSTRAP is false.
#

# These directories are allowed to grow to unspecified size, so they
# are stored as symlinks to the /data partition. mkfedora and yum
# expect some of them to be real directories, however.
datadirs=(
/etc/planetlab
/root
/var/lib/pgsql
/var/www/html/alpina-logs
/var/www/html/boot
/var/www/html/download
/var/www/html/generated
/var/www/html/install-rpms
/var/www/html/xml
/tmp
/usr/tmp
/var/tmp
/var/log
)
for datadir in "${datadirs[@]}" ; do
    # If we are being re-run, it may be a symlink
    if [ -h root/$datadir ] ; then
	rm -f root/$datadir
	mkdir -p root/$datadir
    fi
done

echo "* myplc: Installing base filesystem"
mkdir -p root data
make_chroot root plc_config.xml

# Install configuration scripts
echo "* myplc: Installing configuration scripts"
install -D -m 755 plc_config.py root/tmp/plc_config.py
chroot root sh -c 'cd /tmp; python plc_config.py build; python plc_config.py install'
install -D -m 755 plc-config root/usr/bin/plc-config
install -D -m 755 plc-config-tty root/usr/bin/plc-config-tty
install -D -m 755 api-config root/usr/bin/api-config
install -D -m 755 db-config root/usr/bin/db-config
install -D -m 755 dns-config root/usr/bin/dns-config

# Install initscripts
echo "* myplc: Installing initscripts"
find plc.d | cpio -p -d -u root/etc/
install -D -m 755 guest.init root/etc/init.d/plc
chroot root sh -c 'chkconfig --add plc; chkconfig plc on'

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
rsync -a $srcdir/new_plc_www/ root/var/www/html/

# Install Drupal rewrite rules
install -D -m 644 $srcdir/new_plc_www/drupal.conf root/etc/httpd/conf.d/drupal.conf

# Install configuration file
echo "* myplc: Installing configuration file"
install -D -m 444 $config data/etc/planetlab/default_config.xml
install -D -m 444 plc_config.dtd data/etc/planetlab/plc_config.dtd

# handle root's homedir and tweak root prompt
echo "* myplc: root's homedir and prompt"
roothome=data/root
mkdir -p $roothome
cat << EOF > $roothome/.profile
export PS1="<plc> \$PS1"
EOF
chmod 644 $roothome/.profile

# Move "data" directories out of the installation
echo "* myplc: Moving data directories out of the installation"
move_datadirs root data "${datadirs[@]}"

# Fix permissions on tmp directories
chmod 1777 data/tmp data/usr/tmp data/var/tmp

# Remove generated bootmanager script
rm -f data/var/www/html/boot/bootmanager.sh

# Initialize node RPMs directory. The PlanetLab-Bootstrap.tar.bz2
# tarball already contains all of the node RPMs pre-installed. Only
# updates or optional packages should be placed in this directory.
install -D -m 644 ../build/groups/v3_yumgroups.xml \
    data/var/www/html/install-rpms/planetlab/yumgroups.xml

# Make image out of directory
echo "* myplc: Building loopback image"
make_image root root.img

exit 0
