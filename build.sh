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

# pldistro expected as $1 - defaults to planetlab
pldistro=planetlab
[ -n "$@" ] && pldistro=$1

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

pkgsfile=$(pl_locateDistroFile ../build/ ${pldistro} myplc.pkgs)
pl_root_setup_chroot root -f $pkgsfile

# Install configuration scripts
echo "* myplc: Installing configuration scripts"
install -D -m 755 plc_config.py root/tmp/plc_config.py
chroot root sh -c 'cd /tmp; python plc_config.py build; python plc_config.py install'
install -D -m 755 plc-config root/usr/bin/plc-config
install -D -m 755 plc-config-tty root/usr/bin/plc-config-tty
install -D -m 755 db-config root/usr/bin/db-config
install -D -m 755 dns-config root/usr/bin/dns-config
install -D -m 755 plc-map.py root/usr/bin/plc-map.py
install -D -m 755 clean-empty-dirs.py root/usr/bin/clean-empty-dirs.py
install -D -m 755 mtail.py root/usr/bin/mtail.py
install -D -m 755 check-ssl-peering.py root/usr/bin/check-ssl-peering.py
mkdir root/etc/support-scripts
cp support-scripts/* root/etc/support-scripts 

# Install initscripts
echo "* myplc: Installing initscripts"
find plc.d | cpio -p -d -u root/etc/
install -D -m 755 guest.init root/etc/init.d/plc
chroot root sh -c 'chkconfig --add plc; chkconfig plc on'

# fetch the release stamp from the build if any
# I could not come up with any more sensitive scheme 
if [ -f ../../../myplc-release ] ; then
  cp ../../../myplc-release myplc-release
else
  echo "Cannot find release information." > myplc-release
  date >> myplc-release
  echo "$HeadURL$" >> myplc-release
fi
# install it in /etc/myplc-release 
install -m 444 myplc-release root/etc/myplc-release

### Thierry Parmentelat - april 16 2007
# fix the yum.conf as produced by mkfedora
# so we can use the build's fc4 mirror for various installs/upgrades
# within the chroot jail
# yum_conf_to_build_host is defined in build.functions
yum_conf_to_build_host > root/etc/yum.conf

### Thierry Parmentelat - july 20 2007
# we now build the myplc doc
# beware that making the pdf file somehow overwrites the html
make -C doc myplc.pdf 
rm -f doc/myplc.html
make -C doc myplc.html 

# install at the same place as plcapi - better ideas ?
for doc in myplc.html myplc.pdf ; do
    install -m 644 doc/$doc root/usr/share/plc_api/doc/$doc
done

# we now build the plcapi doc
# this generates a drupal php file from a docbook-generated html
# quick & dirty
docbook_html_to_drupal "${pldistro} PLCAPI Documentation" \
    root/usr/share/plc_api/doc/PLCAPI.html \
    root/var/www/html/planetlab/doc/plcapi.php
# pdf just get copied
install -m 644 root/usr/share/plc_api/doc/PLCAPI.pdf root/var/www/html/planetlab/doc/plcapi.pdf

docbook_html_to_drupal "Myplc User Guide" \
    root/usr/share/plc_api/doc/myplc.html \
    root/var/www/html/planetlab/doc/myplc.php
# pdf just get copied
install -m 644 root/usr/share/plc_api/doc/myplc.pdf root/var/www/html/planetlab/doc/myplc.pdf

# Install configuration file
echo "* myplc: Installing configuration file"
install -D -m 444 default_config.xml data/etc/planetlab/default_config.xml
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
install -D -m 644 $pl_DISTRO_YUMGROUPS \
    data/var/www/html/install-rpms/planetlab/yumgroups.xml

# Make image out of directory
echo "* myplc: Building loopback image"
pl_make_image root root.img 100000000

exit 0
