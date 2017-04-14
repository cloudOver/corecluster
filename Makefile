all:
	echo Nothing to compile

install:
	mkdir -p $(DESTDIR)/etc/corecluster/
	mkdir -p $(DESTDIR)/etc/rsyslog.d/
	mkdir -p $(DESTDIR)/etc/avahi/services/
	mkdir -p $(DESTDIR)/etc/uwsgi/apps-enabled/
	mkdir -p $(DESTDIR)/etc/nginx/sites-enabled/
	mkdir -p $(DESTDIR)/usr/sbin/
	mkdir -p $(DESTDIR)/var/lib/cloudOver/storages
	mkdir -p $(DESTDIR)/var/lib/cloudOver/sheepdog
	python setup.py install --root=$(DESTDIR)
	cp -r config/* $(DESTDIR)/etc/corecluster/
	cp -r sbin/* $(DESTDIR)/usr/sbin/
	echo -n "version=\"" > $(DESTDIR)/etc/corecluster/version.py
	cat debian/changelog | head -n 1 | cut -d ' ' -f 2 | sed -e 's/(//g' -e 's/)//g' | tr -d '\n' >> $(DESTDIR)/etc/corecluster/version.py
	echo "\"" >> $(DESTDIR)/etc/corecluster/version.py
	cp config/rsyslog.conf $(DESTDIR)/etc/rsyslog.d/20-corecluster.conf
	cp config/avahi-services/corecluster-api.service $(DESTDIR)/etc/avahi/services/corecluster-api.service
	cp config/avahi-services/corecluster-ci.service $(DESTDIR)/etc/avahi/services/corecluster-ci.service
	ln -s /etc/corecluster/uwsgi/corecluster-api.ini $(DESTDIR)/etc/uwsgi/apps-enabled/corecluster-api.ini
	ln -s /etc/corecluster/uwsgi/corecluster-ci.ini $(DESTDIR)/etc/uwsgi/apps-enabled/corecluster-ci.ini
	ln -s /etc/corecluster/nginx/corecluster-api $(DESTDIR)/etc/nginx/sites-enabled/corecluster-api
	ln -s /etc/corecluster/nginx/corecluster-ci $(DESTDIR)/etc/nginx/sites-enabled/corecluster-ci

egg:
	python setup.py sdist bdist_egg

egg_install:
	python setup.py install

egg_upload:
	# python setup.py sdist bdist_egg upload
	python setup.py sdist upload

egg_clean:
	rm -rf build/ dist/ corecluster.egg-info/

egg_deploy:
	scp -r . $(DEPLOY_HOST):corecluster
	ssh $(DEPLOY_HOST) "pip uninstall --yes corecluster" || true
	ssh $(DEPLOY_HOST) "cd corecluster ; make egg"
	ssh $(DEPLOY_HOST) "cd corecluster ; make egg_install"
