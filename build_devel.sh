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
#
# Mark Huang <mlhuang@cs.princeton.edu>
# Copyright (C) 2006 The Trustees of Princeton University
#
# $Id: build_devel.sh,v 1.2 2006/07/24 19:32:23 mlhuang Exp $
#

. build.functions

echo "* myplc-devel: Installing base filesystem"
mkdir -p devel/root
make_chroot devel/root plc_devel_config.xml

# Import everything (including ourself) into a private CVS tree
echo "* myplc-devel: Building CVS repository"
cvsroot=$PWD/devel/data/cvs
mkdir -p $cvsroot
cvs -d $cvsroot init

myplc=$(basename $PWD)
pushd ..
for dir in * ; do
    if [ ! -d $cvsroot/$dir ] ; then
	pushd $dir
	if [ "$dir" = "$myplc" ] ; then
	    # Ignore generated files
	    ignore="-I ! -I devel -I root -I root.img -I data" 
	else
	    ignore="-I !"
	fi
	cvs -d $cvsroot import -m "Initial import" -ko $ignore $dir planetlab $IMPORT_TAG
	popd
    fi
done
popd

# Install configuration file
echo "* myplc-devel: Installing configuration file"
install -D -m 444 plc_devel_config.xml devel/data/etc/planetlab/default_config.xml
install -D -m 444 plc_config.dtd devel/data/etc/planetlab/plc_config.dtd

# Install configuration scripts
echo "* myplc-devel: Installing configuration scripts"
install -D -m 755 plc_config.py devel/root/tmp/plc_config.py
chroot devel/root sh -c 'cd /tmp; python plc_config.py build; python plc_config.py install'
install -D -m 755 plc-config devel/root/usr/bin/plc-config

# Install initscripts
echo "* myplc-devel: Installing initscripts"
find plc.d/functions | cpio -p -d -u devel/root/etc/
install -D -m 755 guest.init devel/root/etc/init.d/plc
chroot devel/root sh -c 'chkconfig --add plc; chkconfig plc on'

# Move "data" directories out of the installation
echo "* myplc-devel: Moving data directories out of the installation"
move_datadirs devel/root devel/data \
    /etc/planetlab /build /cvs

# Make image out of directory
echo "* myplc-devel: Building loopback image"
make_image devel/root devel/root.img

exit 0
