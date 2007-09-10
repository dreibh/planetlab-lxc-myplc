Vendor: PlanetLab
Packager: PlanetLab Central <support@planet-lab.org>
Distribution: PlanetLab 4.0
URL: http://cvs.planet-lab.org/cvs/myplc

Summary: PlanetLab Central (PLC) Portable Installation
Name: myplc-native
Version: 0.5
Release: 4%{?pldistro:.%{pldistro}}%{?date:.%{date}}
License: PlanetLab
Group: Applications/Systems
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

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
Requires: PLCWWW
Requires: PLCAPI
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
Requires: cvs
Requires: dev
Requires: bootcd
Requires: dnsmasq
Requires: diffutils
Requires: gzip
Requires: findutils

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
pushd myplc
rm -rf $RPM_BUILD_ROOT
./build-native.sh $RPM_BUILD_ROOT
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
    chown -h -R $SUDO_USER %{_rpmdir}/%{_arch}
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
/etc/init.d/plc
/usr/bin/plc-config
/usr/bin/plc-config-tty
/usr/bin/db-config
/usr/bin/dns-config
/usr/bin/gen-sites-xml.py*
/usr/bin/gen-slices-xml-05.py*
/usr/bin/gen-static-content.py*
/etc/plc.d
/etc/planetlab
/var/www/html/install-rpms/planetlab

%changelog
* Fri Aug 31 2007 Marc E. Fiuczynski <mef@CS.Princeton.EDU>
- initial build.


