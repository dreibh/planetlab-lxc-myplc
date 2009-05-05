# 
# $Id$
#

BINARIES = plc-config plc-config-tty db-config dns-config plc-map.py plc-kml.py clean-empty-dirs.py mtail.py \
	support-scripts/renew_reminder.py support-scripts/gen_aliases.py
INIT_SCRIPTS = api bootcd bootmanager crond db dns functions gpg httpd mail network packages postgresql ssh ssl syslog

INITS=$(addprefix plc.d/,$(INIT_SCRIPTS))

########## make sync PLCHOST=hostname
ifdef PLCHOST
ifdef GUEST
PLCSSH:=root@$(PLCHOST):/vservers/$(GUEST)
endif
endif

LOCAL_RSYNC_EXCLUDES	:= --exclude '*.pyc' 
RSYNC_EXCLUDES		:= --exclude .svn --exclude CVS --exclude '*~' --exclude TAGS $(LOCAL_RSYNC_EXCLUDES)
RSYNC_COND_DRY_RUN	:= $(if $(findstring n,$(MAKEFLAGS)),--dry-run,)
RSYNC			:= rsync -a -v $(RSYNC_COND_DRY_RUN) $(RSYNC_EXCLUDES)

sync:
ifeq (,$(PLCSSH))
	echo "sync: You must define PLCHOST and GUEST on the command line"
	echo " e.g. make sync PLCHOST=private.one-lab.org GUEST=myplc01" ; exit 1
else
	+$(RSYNC) plc.init $(PLCSSH)/etc/init.d/plc
	+$(RSYNC) $(BINARIES) $(PLCSSH)/usr/bin
	+$(RSYNC) $(INITS) $(PLCSSH)/etc/plc.d
	+$(RSYNC) plc_config.py $(PLCSSH)/usr/lib/python2.4/site-packages/plc_config.py
	+$(RSYNC) default_config.xml $(PLCSSH)/etc/planetlab/default_config.xml
	@echo XXXXXXXX You might consider running the following command
	@echo ssh $(PLCHOST) service plc start 
endif


tags:
	find . -type f | egrep -v '.svn/|~$$' | xargs etags

.PHONY: tags
