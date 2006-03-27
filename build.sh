#!/bin/bash
#
# Builds a Fedora based PLC image. You should be able to run this
# script multiple times without a problem.
#
# Mark Huang <mlhuang@cs.princeton.edu>
# Copyright (C) 2006 The Trustees of Princeton University
#
# $Id: build.sh,v 1.1.1.1 2006/03/27 17:36:46 mlhuang Exp $
#

PATH=/sbin:/bin:/usr/sbin:/usr/bin

# In a normal CVS environment, the requisite CVS modules (including
# build/) are located at the same level we are. In a PlanetLab RPM
# build environment (see the RPM spec file), they are checked out into
# a subdirectory.
if [ -d ./build ] ; then
    PATH=$PATH:./build
    srcdir=.
elif [ -d ../build ] ; then
    PATH=$PATH:../build
    srcdir=..
else
    echo "Error: Could not find sources in either . or .."
    exit 1
fi

export PATH

# PLC configuration file
config=plc_config.xml

# Release and architecture to install
releasever=2
basearch=i386

# Data directory base
usr_share=/usr/share

# Initial size of the image
size=1000000000

usage()
{
    echo "Usage: build.sh [OPTION]..."
    echo "	-c file		PLC configuration file (default: $config)"
    echo "	-r release	Fedora release number (default: $releasever)"
    echo "	-a arch		Fedora architecture (default: $basearch)"
    echo "	-d datadir	Data directory base (default: $usr_share)"
    echo "	-s size		Approximate size of the installation (default: $size)"
    echo "	-h		This message"
    exit 1
}

# Get options
while getopts "c:r:a:d:s:h" opt ; do
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
	d)
	    usr_share=$OPTARG
	    ;;
	s)
	    size=$OPTARG
	    ;;
	h|*)
	    usage
	    ;;
    esac
done

root=fc$releasever
data=data$releasever

if [ ! -f $root.img ] ; then
    bs=4096
    count=$(($size / 4096))
    dd bs=$bs count=$count if=/dev/zero of=$root.img
    mkfs.ext3 -j -F $root.img
fi

mkdir -p $root $data
mount -o loop $root.img $root
trap "umount $root; exit 1" ERR

#
# Build
#

# Get package list
while read package ; do
    packages="$packages -p $package"
done < <(./plc-config --packages $config)

# Install base system
mkfedora -v -r $releasever -a $basearch $packages $root

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
install -D -m 755 plc_config.py $root/tmp/plc_config.py
chroot $root sh -c 'cd /tmp; python plc_config.py build; python plc_config.py install'
install -D -m 755 plc-config $root/usr/bin/plc-config
install -D -m 755 api-config $root/usr/bin/api-config

# Install init script
install -D -m 755 guest.init $root/etc/init.d/plc
chroot $root sh -c 'chkconfig --add plc; chkconfig plc on'

# Install DB schema and API code
mkdir -p $root/usr/share
rsync -a $srcdir/pl_db $srcdir/plc_api $root/usr/share/

# Install web scripts
mkdir -p $root/usr/bin
install -m 755 \
    $srcdir/plc/scripts/gen-sites-xml.py \
    $srcdir/plc/scripts/gen-slices-xml-05.py \
    $srcdir/plc/scripts/gen-static-content.py \
    $root/usr/bin/

# Install web pages
mkdir -p $root/var/www/html
rsync -a $srcdir/plc_www/ $root/var/www/html/

# Install configuration file
install -D -m 644 $config $data/etc/planetlab/plc_config.xml

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
    e2fsck -f $dev_loop
    resize2fs $dev_loop ${kb}K

    # Tear down loopback association
    losetup -d $dev_loop
    trap - ERR

    # Truncate the image file
    perl -e "truncate '$root.img', $kb*1024"
fi

# Write sysconfig
cat >plc.sysconfig <<EOF
PLC_ROOT=$usr_share/plc/$root
PLC_DATA=$usr_share/plc/$data
#PLC_OPTIONS="-v"
EOF

exit $RETVAL
