#!/bin/bash
#
# Build a complete MyPLC development environment. Requires PlanetLab
# source code to be exported into directories at the same level as we
# are (i.e., ..).
#
# devel/root.img (loopback image)
# devel/root/ (mount point)
# devel/data/ (various data files)
# devel/data/cvs/ (local CVS repository)
# devel/data/build/ (build area)
# devel/data/etc/planetlab/ (configuration)
# devel/data/root (root's home dir)
#
# Mark Huang <mlhuang@cs.princeton.edu>
# Copyright (C) 2006 The Trustees of Princeton University
#
# $Id: build_devel.sh 1078 2007-11-15 13:38:27Z thierry $
#

echo "$0" not supported anymore
echo "need to figure a way to handle space in group names in .lst files"
exit 1

. build.functions

# These directories are allowed to grow to unspecified size, so they
# are stored as symlinks to the /data partition. mkfedora and yum
# expect some of them to be real directories, however.
datadirs=(
/etc/planetlab
/root
/tmp
/usr/tmp
/var/tmp
/var/log
)

pl_fixdirs devel/root "${datadirs[@]}"


echo "* myplc-devel: Installing base filesystem"
mkdir -p devel/root
# xxx need be pldistro & fcdistro dependant
make_chroot_from_lst devel/root planetlab-devel.lst

# Install configuration file
echo "* myplc-devel: Installing configuration file"
install -D -m 444 plc_devel_config.xml devel/data/etc/planetlab/default_config.xml
install -D -m 444 plc_config.dtd devel/data/etc/planetlab/plc_config.dtd

# Install configuration scripts
echo "* myplc-devel: Installing configuration scripts"
install -D -m 755 plc_config.py devel/root/tmp/plc_config.py
chroot devel/root sh -c 'cd /tmp; python plc_config.py build; python plc_config.py install'
install -D -m 755 plc-config devel/root/usr/bin/plc-config
install -D -m 755 plc-config-tty devel/root/usr/bin/plc-config-tty

# Install initscripts
echo "* myplc-devel: Installing initscripts"
find plc.d/functions | cpio -p -d -u devel/root/etc/
install -D -m 755 guest.init devel/root/etc/init.d/plc
chroot devel/root sh -c 'chkconfig --add plc; chkconfig plc on'

# Add a build user with the same ID as the current build user, who can
# then cross-mount their home directory into the image and build MyPLC
# in their home directory.
echo "* myplc-devel: Adding build user"
uid=${SUDO_UID:-2000}
gid=${SUDO_GID:-2000}
if ! grep -q "Automated Build" devel/root/etc/passwd ; then
    chroot devel/root <<EOF
groupadd -o -g $gid build
useradd -o -c 'Automated Build' -u $uid -g $gid -n -d /data/build -M -s /bin/bash build
exit 0
EOF
fi

# Copy build scripts to build home directory
mkdir -p devel/data/build
rsync -a $srcdir/build/ devel/data/build/

# Allow build user to build certain RPMs as root
cat >devel/root/etc/sudoers <<EOF
root	ALL=(ALL) ALL
#build	ALL=(root) NOPASSWD: /usr/bin/rpmbuild
build   ALL=(ALL)       NOPASSWD: ALL
EOF

# Move "data" directories out of the installation
echo "* myplc-devel: Moving data directories out of the installation"
pl_move_dirs devel/root devel/data /data "${datadirs[@]}"

# Fix permissions on tmp directories
pl_fixtmp_permissions devel/data

# Make image out of directory
echo "* myplc-devel: Building loopback image"
pl_make_image devel/root devel/root.img 100000000

exit 0
