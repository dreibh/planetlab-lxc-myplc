#!/bin/bash
#
# Builds MyPLC, either inside the MyPLC development environment in
# devel/root (if PLC_DEVEL_BOOTSTRAP is true), or in the current host
# environment (may be itself a MyPLC development environment or a
# Fedora environment with the appropriate development packages
# installed).
#
# root.img (loopback image)
# root/ (mount point)
# data/ (various data files)
# data/etc/planetlab/ (configuration files)
# data/root (root's homedir)
#
# Mark Huang <mlhuang@cs.princeton.edu>
# Marc E. Fiuczynski <mef@cs.princeton.edu>
# Copyright (C) 2006-2007 The Trustees of Princeton University
#
# $Id: build.sh,v 1.41.2.1 2007/08/30 16:39:08 mef Exp $
#

. build.functions

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
/var/www/html/files
/var/www/html/sites
/var/www/html/generated
/var/www/html/install-rpms
/var/www/html/xml
/tmp
/usr/tmp
/var/tmp
/var/log
)

pl_fixdirs root "${datadirs[@]}"

echo "* myplc: Installing base filesystem"
mkdir -p root data
make_chroot root plc_config.xml

# Install configuration scripts
echo "* myplc: Installing configuration scripts"
install -D -m 755 plc_config.py root/tmp/plc_config.py
chroot root sh -c 'cd /tmp; python plc_config.py build; python plc_config.py install'
install -D -m 755 plc-config root/usr/bin/plc-config
install -D -m 755 plc-config-tty root/usr/bin/plc-config-tty
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
pl_move_dirs root data /data "${datadirs[@]}"

# Fix permissions on tmp directories
pl_fixtmp_permissions data

# Remove generated bootmanager script
rm -f data/var/www/html/boot/bootmanager.sh

# Initialize node RPMs directory. The PlanetLab-Bootstrap.tar.bz2
# tarball already contains all of the node RPMs pre-installed. Only
# updates or optional packages should be placed in this directory.
install -D -m 644 $pl_YUMGROUPSXML \
    data/var/www/html/install-rpms/planetlab/yumgroups.xml

# Make image out of directory
echo "* myplc: Building loopback image"
pl_make_image root root.img 100000000

exit 0
