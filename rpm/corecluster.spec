Name: corecluster
Version: 16.06.13
Release: 1%{?dist}
URL: http://www.cloudover.org/corecluster/
Packager: Marta Nabozny <marta.nabozny@cloudover.io>
Summary: Main package of CoreCluster IaaS cloud
License: GPLv3

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires: corenetwork
Requires: corosync
Requires: libvirt-bin
Requires: nfs-common
Requires: nginx-extras
Requires: ntpdate
Requires: openssh-server
Requires: python-dev
Requires: python-libvirt
Requires: python-pip
Requires: quagga
Requires: redis-server
Requires: qemu-utils
Requires: sqlite3
Requires: sudo
Requires: uwsgi
Requires: uwsgi-plugin-python

%description
Main package of CoreCluster cloud.

%install
cd corecluster
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

%post
echo "coreCluster: Installing python package CoreCluster"
pip install --upgrade corecluster==16.02.01 || /bin/true

echo "coreCluster: Changing permissions"
chown -R syslog:adm /var/log/cloudOver || chown -R syslog:cloudover /var/log/cloudOver || chown -R cloudover:cloudover /var/log/cloudOver || true
chmod -R ug+rw /var/log/cloudOver || true

echo "coreCluster: Restarting rsyslogd"
service rsyslog restart || service rsyslogd restart || true

if ! [ -f /etc/corecluster/config.py ] ; then
    echo "coreCluster: Creating default main configuration file"
    SECRET=`head -c 100 /dev/urandom | md5sum | cut -f 1 -d ' '`
    INSTALLATION_ID=`head -c 100 /dev/urandom | md5sum | cut -f 1 -d ' '`
    sed -e "s/OC_SECRET_KEY/$SECRET/"\
        -e "s/RANDOM_INSTALLATION_ID/$INSTALLATION_ID/"\
        /etc/corecluster/config.example > /etc/corecluster/config.py
fi

if ! [ -f /etc/corecluster/agent.py ] ; then
    echo "coreCluster: Creating default configuration file for agents"
    cp /etc/corecluster/agent.example /etc/corecluster/agent.py
fi

echo "coreCluster: Migrating database"
/usr/sbin/cc-admin migrate --noinput

echo "coreCluster: Changing permissions"
chown -R cloudover:cloudover /var/lib/cloudOver || true
chown -R cloudover:cloudover /usr/lib/cloudOver/storages || true
chown -R cloudover:www-data /etc/corecluster
chown -R cloudover:www-data /etc/corenetwork
chmod 660 /etc/corecluster/config.py
chmod 660 /etc/corecluster/agent.py
chmod 660 /etc/corecluster/version.py
chmod 660 /etc/corenetwork/config.py

echo "coreCluster: Collecting static files"
chown -R cloudover:www-data /var/lib/cloudOver/static/ || true
/usr/sbin/cc-admin collectstatic --noinput || true

find /etc/corecluster -name "*.pyc" -exec rm + || true
find /etc/corenetwork -name "*.pyc" -exec rm + || true
find /usr/local/lib/python2.7/dist-packages/corecluster -name "*.pyc" -exec rm + 2> /dev/null || true
find /usr/local/lib/python2.7/dist-packages/corenetwork -name "*.pyc" -exec rm + 2> /dev/null || true

echo "coreCluster: Restarting avahi service"
service avahi-daemon restart

echo "coreCluster: Restarting uwsgi"
service uwsgi restart

echo "coreCluster: Restarting nginx"
service nginx restart

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
/etc/corecluster/
/usr/local/lib/python2.7/dist-packages/
/usr/sbin/cc-manage
/usr/sbin/cc-admin
