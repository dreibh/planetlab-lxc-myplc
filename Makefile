##########
tags:
	find . -type f | egrep -v '\.git/|~$$' | xargs etags

.PHONY: tags

########## sync
# 2 forms are supported
# (*) if your plc root context has direct ssh access:
# make sync PLC=boot.planet-lab.eu
# (*) otherwise, entering through the root context
# make sync PLCHOST=testplc.onelab.eu GUEST=vplc03.inria.fr

PLCHOST ?= testplc.onelab.eu

ifdef GUEST
SSHURL:=root@$(PLCHOST):/vservers/$(GUEST)
SSHCOMMAND:=ssh root@$(PLCHOST) vserver $(GUEST)
endif
ifdef PLC
SSHURL:=root@$(PLC):/
SSHCOMMAND:=ssh root@$(PLC)
endif

LOCAL_RSYNC_EXCLUDES	:= --exclude '*.pyc' 
RSYNC_EXCLUDES		:= --exclude .svn --exclude CVS --exclude '*~' --exclude TAGS $(LOCAL_RSYNC_EXCLUDES)
RSYNC_COND_DRY_RUN	:= $(if $(findstring n,$(MAKEFLAGS)),--dry-run,)
RSYNC			:= rsync -a -v $(RSYNC_COND_DRY_RUN) $(RSYNC_EXCLUDES)

sync:
ifeq (,$(SSHURL))
	@echo "sync: You must define, either PLC, or PLCHOST & GUEST, on the command line"
	@echo "  e.g. make sync PLC=boot.planet-lab.eu"
	@echo "  or   make sync PLCHOST=testplc.onelab.eu GUEST=vplc03.inria.fr"
	@exit 1
else
	+$(RSYNC) plc.init $(SSHURL)/etc/init.d/plc
	+$(RSYNC) bin/ $(SSHURL)/usr/bin/
	+$(RSYNC) plc.d/ $(SSHURL)/etc/plc.d/
	+$(RSYNC) db-config.d/ $(SSHURL)/etc/planetlab/db-config.d/
	+$(RSYNC) plc_config.py $(SSHURL)/usr/lib/python2.\*/site-packages/plc_config.py
	+$(RSYNC) default_config.xml $(SSHURL)/etc/planetlab/default_config.xml
	@echo XXXXXXXX you might need to run ssh root@$(PLC) service plc start 
endif

#################### convenience, for debugging only
# make +foo : prints the value of $(foo)
# make ++foo : idem but verbose, i.e. foo=$(foo)
++%: varname=$(subst +,,$@)
++%:
	@echo "$(varname)=$($(varname))"
+%: varname=$(subst +,,$@)
+%:
	@echo "$($(varname))"

