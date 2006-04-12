#!/bin/bash
#
# Builds a Fedora based PLC image. You should be able to run this
# script multiple times without a problem.
#
# Mark Huang <mlhuang@cs.princeton.edu>
# Copyright (C) 2006 The Trustees of Princeton University
#
# $Id$
#

PATH=/sbin:/bin:/usr/sbin:/usr/bin

# In both a normal CVS environment and a PlanetLab RPM
# build environment, all of our dependencies are checked out into
# directories at the same level as us.
if [ -d ../build ] ; then
    PATH=$PATH:../build
    srcdir=..
else
    echo "Error: Could not find $(cd .. && pwd -P)/build/"
    exit 1
fi

export PATH

# PLC configuration file
config=plc_config.xml

# Release and architecture to install
releasever=2
basearch=i386

# Initial size of the image
size=1000000000

usage()
{
    echo "Usage: build.sh [OPTION]..."
    echo "	-c file		PLC configuration file (default: $config)"
    echo "	-r release	Fedora release number (default: $releasever)"
    echo "	-a arch		Fedora architecture (default: $basearch)"
    echo "	-s size		Approximate size of the installation (default: $size)"
    echo "	-h		This message"
    exit 1
}

# Get options
while getopts "c:r:a:s:h" opt ; do
    case $opt in
	c)
	    config=$OPTARG
	    ;;
	r)
	    releasever=$OPTARG
	    ;;
	a)
	    basearch=$OPTARG
	    ;;
	s)
	    size=$OPTARG
	    ;;
	h|*)
	    usage
	    ;;
    esac
done

# Do not tolerate errors
set -e

root=root
data=data

if [ ! -f $root.img ] ; then
    bs=4096
    count=$(($size / 4096))
    dd bs=$bs count=$count if=/dev/zero of=$root.img
    mkfs.ext3 -j -F $root.img
fi

mkdir -p $root $data
mount -o loop $root.img $root
trap "umount $root" ERR

#
# Build
#

# Get package list
while read package ; do
    packages="$packages -p $package"
done < <(./plc-config --packages $config)

# Install base system
mkfedora -v -r $releasever -a $basearch -k $packages $root

# Disable all services in reference image
chroot $root sh -c "/sbin/chkconfig --list | awk '{ print \$1 }' | xargs -i /sbin/chkconfig {} off"

# FC2 minilogd starts up during shutdown and makes unmounting
# impossible. Just get rid of it.
rm -f $root/sbin/minilogd
ln -nsf /bin/true $root/sbin/minilogd

# Build schema
make -C $srcdir/pl_db

#
# Install
#

# Install configuration scripts
echo "* Installing configuration scripts"
install -D -m 755 plc_config.py $root/tmp/plc_config.py
chroot $root sh -c 'cd /tmp; python plc_config.py build; python plc_config.py install'
install -D -m 755 plc-config $root/usr/bin/plc-config
install -D -m 755 api-config $root/usr/bin/api-config

# Install initscripts
echo "* Installing initscripts"
find plc.d | cpio -p -d -u $root/etc/
install -D -m 755 guest.init $root/etc/init.d/plc
chroot $root sh -c 'chkconfig --add plc; chkconfig plc on'

# Install DB schema and API code
echo "* Installing DB schema and API code"
mkdir -p $root/usr/share
rsync -a $srcdir/pl_db $srcdir/plc_api $root/usr/share/

# Install web scripts
echo "* Installing web scripts"
mkdir -p $root/usr/bin
install -m 755 \
    $srcdir/plc/scripts/gen-sites-xml.py \
    $srcdir/plc/scripts/gen-slices-xml-05.py \
    $srcdir/plc/scripts/gen-static-content.py \
    $root/usr/bin/

# Install web pages
echo "* Installing web pages"
mkdir -p $root/var/www/html
# Exclude old cruft, unrelated GENI pages, and official documents
rsync -a \
    --exclude='*2002' --exclude='*2003' \
    --exclude=geni --exclude=PDN --exclude=Talks \
    $srcdir/plc_www/ $root/var/www/html/

# Install configuration file
echo "* Installing configuration file"
install -D -m 444 $config $data/etc/planetlab/default_config.xml
install -D -m 444 plc_config.dtd $data/etc/planetlab/plc_config.dtd

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

echo "* Moving data directories out of the installation"
mkdir -p $root/data
for datadir in "${datadirs[@]}" ; do
    mkdir -p ${data}$datadir
    if [ -d $root/$datadir -a ! -h $root/$datadir ] ; then
	(cd $root && find ./$datadir | cpio -p -d -u ../$data/)
    fi
    rm -rf $root/$datadir
    mkdir -p $(dirname $root/$datadir)
    ln -nsf /data$datadir $root/$datadir
done

# Shrink to 100 MB free space
kb=$(python <<EOF
import os
df = os.statvfs('$root')
target = 100 * 1024 * 1024 / df.f_bsize
if df.f_bavail > target:
    print (df.f_blocks - (df.f_bavail - target)) * df.f_bsize / 1024
EOF
)

umount $root
trap - ERR

if [ -n "$kb" ] ; then
    # Setup loopback association. Newer versions of losetup have a -f
    # option which finds an unused loopback device, but we must
    # support FC2 for now.
    # dev_loop=$(losetup -f)
    for i in `seq 1 7` ; do
	if ! grep -q "^/dev/loop$i" /proc/mounts ; then
	    dev_loop="/dev/loop$i"
	    break
	fi
    done
    losetup $dev_loop $root.img
    trap "losetup -d $dev_loop" ERR

    # Resize the filesystem
    echo "* Checking filesystem"
    e2fsck -a -f $dev_loop
    echo "* Shrinking filesystem"
    resize2fs $dev_loop ${kb}K

    # Tear down loopback association
    losetup -d $dev_loop
    trap - ERR

    # Truncate the image file
    perl -e "truncate '$root.img', $kb*1024"
fi

# Write sysconfig
cat >plc.sysconfig <<EOF
PLC_ROOT=/plc/$root
PLC_DATA=/plc/$data
#PLC_OPTIONS="-v"
EOF

# Initialize node RPMs directory. The PlanetLab-Bootstrap.tar.bz2
# tarball already contains all of the node RPMs pre-installed. Only
# updates or optional packages should be placed in this directory.
if [ -n "$RPM_BUILD_DIR" ] ; then
    echo "* Initializing node RPMs directory"
    RPM_RPMS_DIR=$(cd $(dirname $RPM_BUILD_DIR)/RPMS && pwd -P)
    mkdir -p $data/var/www/html/install-rpms/planetlab
    if [ -f $RPM_RPMS_DIR/yumgroups.xml ] ; then
	install -D -m 644 $RPM_RPMS_DIR/yumgroups.xml \
	    $data/var/www/html/install-rpms/planetlab/yumgroups.xml
    fi
    # yum-2.0.x
    if [ -x /usr/bin/yum-arch ] ; then
	yum-arch $data/var/www/html/install-rpms/planetlab
    fi
    # yum-2.4.x
    if [ -x /usr/bin/createrepo ] ; then
	if [ -f $data/var/www/html/install-rpms/planetlab/yumgroups.xml ] ; then
	    groupfile="-g yumgroups.xml"
	fi
	createrepo $groupfile $data/var/www/html/install-rpms/planetlab
    fi
fi

# Bootstrap the system for quicker startup (and to populate the
# PlanetLabConf tables from PLC, which may not be accessible
# later). The bootstrap.xml configuration overlay configures the web
# server to run on an alternate port (in case the build machine itself
# is running a web server on port 80). Start everything up to
# bootstrap the database, then shut it back down again immediately.
echo "* Bootstrapping installation"

install -D -m 644 bootstrap.xml $data/etc/planetlab/configs/bootstrap.xml

# Otherwise, host.init will try to read /etc/sysconfig/plc
export PLC_ROOT=$PWD/$root
export PLC_DATA=$PWD/$data
#export PLC_OPTIONS="-v"

./host.init start
RETVAL=$?

# Remove ISO and USB images, which take up >100MB but only take a
# couple of seconds to generate at first boot.
rm -f $data/var/www/html/download/*.{iso,usb}

./host.init stop
RETVAL=$(($RETVAL+$?))

# Restore default configuration
rm -f $data/etc/planetlab/plc_config.xml $data/etc/planetlab/configs/bootstrap.xml

exit $RETVAL
