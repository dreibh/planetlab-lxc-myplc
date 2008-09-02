#
# $Id$
#
%define url $URL$

%define name myplc-native
%define version 5.0
%define taglevel 0

%define release %{taglevel}%{?pldistro:.%{pldistro}}%{?date:.%{date}}

Summary: PlanetLab Central (PLC) Portable Installation
Name: %{name}
Version: %{version}
Release: %{release}
License: PlanetLab
Group: Applications/Systems
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch: noarch

Vendor: PlanetLab
Packager: PlanetLab Central <support@planet-lab.org>
Distribution: PlanetLab %{plrelease}
URL: %(echo %{url} | cut -d ' ' -f 2)

Requires: bzip2
Requires: sendmail-cf
Requires: tar 
Requires: less
Requires: perl-GD
Requires: openssl
Requires: xmlsec1
Requires: gd
Requires: expect
Requires: php-pgsql
Requires: curl
Requires: python-pycurl
Requires: python-psycopg2
Requires: httpd
Requires: rsync
Requires: mod_python
Requires: mod_ssl
Requires: bootmanager
Requires: python-devel
Requires: SOAPpy
Requires: vixie-cron
Requires: yum
Requires: php-gd
Requires: PyXML
Requires: sendmail
Requires: python >= 2.4
Requires: createrepo
Requires: postgresql-python
Requires: cpio
Requires: postgresql-server
Requires: wget
Requires: php
Requires: xmlsec1-openssl
Requires: postgresql
Requires: openssh
Requires: bootcd-%{pldistro}-%{_arch}
Requires: dnsmasq
Requires: diffutils
Requires: gzip
Requires: vim-minimal
Requires: findutils
# planetlab stuff
Requires: PLCWWW
Requires: nodeconfig
Requires: PLCAPI
Requires: bootstrapfs-%{pldistro}-%{_arch}
Requires: myplc-docs

# argh - ugly - we might wish to use something from build/config.%{pldistro} instead
%if "%{pldistro}" == "onelab"
Requires: dummynet_image
%endif

Provides: myplc

%define debug_package %{nil}

%description
MyPLC is a complete PlanetLab Central (PLC) portable installation
contained within a chroot jail. The default installation consists of a
web server, an XML-RPC API server, a boot server, and a database
server: the core components of PLC. The installation may be customized
through a graphical interface. All PLC services are started up and
shut down through a single System V init script installed in the host
system.

%prep
%setup -q

%build
pushd MyPLC
rm -rf $RPM_BUILD_ROOT
./build-native.sh %{pldistro} $RPM_BUILD_ROOT
popd

%install


%clean
rm -rf $RPM_BUILD_ROOT

# If run under sudo
if [ -n "$SUDO_USER" ] ; then
    # Allow user to delete the build directory
    chown -h -R $SUDO_USER .
    # Some temporary cdroot files like /var/empty/sshd and
    # /usr/bin/sudo get created with non-readable permissions.
    find . -not -perm +0600 -exec chmod u+rw {} \;
    # Allow user to delete the built RPM(s)
    [ -d %{_rpmdir}/noarch ] && chown -h -R $SUDO_USER %{_rpmdir}/noarch
fi

%pre
if [ -x %{_sysconfdir}/init.d/plc ] ; then
    %{_sysconfdir}/init.d/plc stop
fi

# Old versions of myplc used to ship with a bootstrapped database and
# /etc/planetlab directory. Including generated files in the manifest
# was dangerous; if /plc/data/var/lib/pgsql/data/base/1/16676 changed
# names from one RPM build to another, it would be rpmsaved and thus
# effectively deleted. Now we do not include these files in the
# manifest. However, to avoid deleting these files in the process of
# upgrading from one of these old versions of myplc, we must back up
# the database and /etc/planetlab and restore them after the old
# version has been uninstalled in %triggerpostun (also in %post, in
# case we are force upgrading to the same version).
#
# This code can be removed once all myplc-0.4-1 installations have
# been upgraded to at least myplc-0.4-2.

# 0 = install, 1 = upgrade
if [ $1 -gt 0 ] ; then
    for dir in /var/lib/pgsql/data /etc/planetlab ; do
	if [ -d $dir ] ; then
	    echo "Preserving $dir"
	    mkdir -p $dir.rpmsave
	    tar -C $dir -cpf - . | \
	       tar -C $dir.rpmsave -xpf -

	    # Except for the default configuration file and DTD, which
	    # really should be considered for upgrade.
	    rm -f $dir.rpmsave/{default_config.xml,plc_config.dtd}
	fi
    done
fi

%post
if [ -x /sbin/chkconfig ] ; then
    /sbin/chkconfig --add plc
    /sbin/chkconfig plc on
fi
pushd /usr/share/myplc &> /dev/null
python plc_config.py build
python plc_config.py install
popd &> /dev/null

%triggerpostun -- %{name}
# 0 = erase, 1 = upgrade
if [ $1 -gt 0 ] ; then
    for dir in /var/lib/pgsql/data /etc/planetlab ; do
	if [ -d $dir.rpmsave -a -d $dir ] ; then
	    echo "Merging $dir"
	    if tar -C $dir.rpmsave -cpf - . | \
	       tar -C $dir -xpf - ; then
		rm -rf $dir.rpmsave
	    fi
	fi
    done
fi    

%preun
# 0 = erase, 1 = upgrade
if [ $1 -eq 0 ] ; then
    %{_sysconfdir}/init.d/plc stop
    if [ -x /sbin/chkconfig ] ; then
        /sbin/chkconfig plc off
	/sbin/chkconfig --del plc
    fi
fi

%files
%defattr(-,root,root,-)
# Host startup script and configuration file
/etc/myplc-release
/etc/init.d/plc
/etc/plc.d
/etc/planetlab
/etc/plc_sliceinitscripts/sirius
/etc/support-scripts/gen_aliases.py*
/etc/support-scripts/renew_reminder.py*
/usr/bin/plc-config
/usr/bin/plc-config-tty
/usr/bin/db-config
/usr/bin/dns-config
/usr/bin/plc-map.py*
/usr/bin/plc-kml.py*
/usr/bin/refresh-peer.py*
/usr/bin/clean-empty-dirs.py*
/usr/bin/mtail.py*
/usr/bin/check-ssl-peering.py*
/usr/share/myplc
/var/www/html/install-rpms/%{pldistro}-%{_arch}
/var/www/html/install-rpms/planetlab

%changelog
* Tue May 20 2008 Faiyaz Ahmed <faiyaza@cs.princeton.edu> - MyPLC-4.2-15
- Removed proper ops from planetflow slice.

* Wed May 14 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.2-14
- myplc-native requires myplc-docs
- fixed doc build by locating locally installed DTDs at build-time

* Sun May 11 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.2-13
- turn myplc-docs off for now

* Sat May 10 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.2-12
- figures in doc package

* Fri May 09 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.2-11
- no more doc packaged outside of myplc-docs - doc/ cleaned up 
- chroot packaging does not have docs anymore
- 'cvs' and 'dev' not required from myplc-native anymore
- cosmetic change in kml output

* Thu May 08 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.2-10
- defaults for *_IP conf vars now void, expect more accurate /etc/hosts
- gethostbyname uses python rather than perl (hope this shrinks deps) 
- doc: reviewed myplc doc - deprecated everything related to myplc-devel
- doc: packaging doc in myplc-native (myplc&PLCAPI) & removed target files from svn
- make sync now works towards vserver-based myplc only 

* Mon May 05 2008 Stephen Soltesz <soltesz@cs.princeton.edu> - MyPLC-4.2-9
- 
- added vsys 'pfmount' script to the default netflow slice attributes.
- 

* Thu Apr 24 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.2-8
- plc.d/bootcd step altered for handling legacy bootcd smooth migration
- to new bootcd packaging

* Wed Apr 23 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.2-7
- changes needed for bootcd 4.2 : new, possible multiple, installation locations, and new rpm name

* Tue Apr 22 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.2-6
- packaging of mplc-release in myplc-native
- sudoers.php is new to PlanetLabConf (needs nodeconfig-4.2-4)
- resolv file in /etc/resolv.conf, not plc_resolv.conf
- improved sirius script
- remove the 'driver' node-network-setting that was unused, and new 'Multihome' category
- expires more properly set 

* Mon Apr 07 2008 Stephen Soltesz <soltesz@cs.princeton.edu> - MyPLC-4.2-4 MyPLC-4.2-5
- 

* Wed Mar 26 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.2-3 MyPLC-4.2-4
- renew_reminder script moved to support-scripts/
- gen-aliases script added in support-scripts/
- sirius initscript moved to plc_sliceinitscripts (formerly inlined in db-config)
- plc-map script : no javascript for googlemap anymore, see new plc-kml script instead
- nodefamily-aware (creates legacy symlink /var/www/html/install-rpms/planetlab)
- new native slice attributes 'capabilities', 'vsys' and 'codemux'
- new setting 'Mom list address' for sending emails to a separate destination
- starts rsyslogd/syslogd as appropriate
- expects nodeconfig package (former PlanetLabConf/ dir from PLCWWW)
- convenience generation of yum.conf in resulting image based on build/mirroring

* Thu Feb 14 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-4.2-2 myplc-4.2-3
- refresh-peer.py removed (duplicate with PLCAPI)
- plc.d/ scripts cleaned up
- sirius initscript updated
- slice auto renewal fixed

* Fri Aug 31 2007 Marc E. Fiuczynski <mef@CS.Princeton.EDU>
- initial build.

%define module_current_branch 4.2
