Vendor: PlanetLab
Packager: PlanetLab Central <support@planet-lab.org>
Distribution: PlanetLab 4.0
URL: http://svn.planet-lab.org/svn/MyPLC

Summary: PlanetLab Central (PLC) Development Environment
Name: MyPLC-devel-native
Version: 0.1
Release: 2%{?pldistro:.%{pldistro}}%{?date:.%{date}}
License: PlanetLab
Group: Development/Tools
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
AutoReqProv: no

# group this according to the requirements of the different packages we build
Requires: beecrypt-devel
Requires: bzip2
Requires: coreutils
Requires: cpio
Requires: createrepo
Requires: curl
Requires: curl-devel
Requires: cvs
Requires: db4-devel
Requires: dev
Requires: diffutils
Requires: dnsmasq
Requires: docbook-utils-pdf
Requires: dosfstools
Requires: doxygen
Requires: expat-devel
Requires: expect
Requires: findutils
Requires: gcc-c++
Requires: gd
Requires: glibc
Requires: glibc-common
Requires: gnupg
Requires: gperf
Requires: graphviz
Requires: gzip
Requires: httpd
%if "%{distroname}" == "Fedora" && "%{distrorelease}" >= "7"
Requires: inotify-tools-devel
%endif
Requires: iptables
Requires: less
Requires: libpcap
%if "%{distroname}" == "Fedora" && "%{distrorelease}" >= "6"
Requires: libpcap-devel
%endif
%if "%{distroname}" == "CentOS" && "%{distrorelease}" >= "5"
Requires: libpcap-devel
%endif
Requires: libtool
Requires: linuxdoc-tools
Requires: mailx
Requires: make
Requires: mkisofs
Requires: mod_python
Requires: mod_ssl
Requires: mysql
Requires: mysql-devel
Requires: mysql-server
Requires: nasm
Requires: ncurses-devel
Requires: ocaml
Requires: ocaml-ocamldoc
Requires: openssh
Requires: openssl
Requires: php
Requires: php-devel
Requires: php-gd
Requires: php-pgsql
Requires: postgresql
Requires: postgresql-devel
Requires: postgresql-python
Requires: postgresql-server
Requires: python
Requires: python-devel
%if "%{distroname}" == "Fedora" && "%{distrorelease}" >= "5"
Requires: python-pycurl
Requires: python-psycopg2
%endif
%if "%{distroname}" == "CentOS" && "%{distrorelease}" >= "5"
Requires: python-pycurl
Requires: python-psycopg2
%endif
Requires: PyXML
Requires: readline-devel
Requires: redhat-rpm-config
Requires: rpm
Requires: rpm-build
Requires: rpm-devel
Requires: rsync
Requires: sendmail
Requires: sendmail-cf
Requires: sharutils
Requires: SOAPpy
Requires: sudo
Requires: subversion
Requires: tar
Requires: tetex-latex
Requires: time
Requires: vconfig
Requires: vixie-cron
Requires: wget
Requires: xmlsec1
Requires: xmlsec1-openssl
Requires: yum

%define debug_package %{nil}

%description
This package installs a complete PlanetLab development
environment. The default installation consists of all the packages
necessary to compile MyPLC.

%prep
%setup -q

%build

rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/etc

%install

touch $RPM_BUILD_ROOT/etc/myplc-devel-native

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

%post

if [ -h "/sbin/new-kernel-pkg" ] ; then
	filename=$(readlink -f /sbin/new-kernel-pkg)
	if [ "$filename" == "/sbin/true"] ; then
		echo "WARNING: /sbin/new-kernel-pkg symlinked to /sbin/true"
		echo "\tmost likely /etc/rpm/macros has /sbin/new-kernel-pkg declared in _netsharedpath."
		echo "\tPlease remove /sbin/new-kernel-pkg from _netsharedpath and reintall mkinitrd."
		exit 1
	fi
fi

uid=2000
gid=2000

# add a "build" user to the system
builduser=$(grep "^build" /etc/passwd | wc -l)
if [ $builduser -eq 0 ] ; then
	groupadd -o -g $gid build;
	useradd -o -c 'Automated Build' -u $uid -g $gid -n -M -s /bin/bash build;
fi

# myplc-devel on a shared box requires that we set up max loop devices
for i in $(seq 0 255) ; do
	mknod -m 640 /dev/loop$i b 7 $i
done

# Allow build user to build certain RPMs as root
buildsudo=$(grep "^build.*ALL=(ALL).*NOPASSWD:.*ALL"  /etc/sudoers | wc -l)
if [ $buildsudo -eq 0 ] ; then
	echo "build   ALL=(ALL)       NOPASSWD: ALL" >> /etc/sudoers
fi

# Don't requiretty for sudo. Needed to build myplc from cron job
ttysudo=$(grep "^Defaults.*requiretty" /etc/sudoers | wc -l)
if [ $ttysudo -eq 1 ] ; then
	sed -i 's,^Defaults.*requiretty,#Defaults requiretty,' /etc/sudoers
fi

%preun
# 0 = erase, 1 = upgrade
if [ $1 -eq 0 ] ; then
	echo "NOTE: should remove build user from /etc/sudoers"
fi

%files
%defattr(-,root,root,-)
/etc/myplc-devel-native

%changelog
* Fri Oct 05 2007 Marc E. Fiuczynski <mef@cs.princeton.edu>
- Initial build.
