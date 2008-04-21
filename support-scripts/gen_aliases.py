#!/usr/bin/python
#
# Generates:
#
# 1. /etc/mail/aliasesPL, /etc/mail/virtusertable
#    <slicename>@slices.planet-lab.org: all users and PIs of a slice
#    pi-<loginbase>@sites.planet-lab.org: all PIs at a site
#    tech-<loginbase>@sites.planet-lab.org: all techs at a site
# 2. /etc/mail/local-host-names
#    Additional local e-mail FQDNs
#
# Updates:
#
# 1. announce@lists.planet-lab.org membership from the database and from
#    the membership of announce-additions@lists.planet-lab.org
# 2. {pis,techs}@lists.planet-lab.org membership from the database.
# 3. cvs@lists.planet-lab.org accept_these_nonmembers from
#    /usr/share/doc/plc/accounts.txt
#
# N.B.:
#
# 1. See plc/mail/sendmail-mail.mc for the ALIAS_FILE definition that
#    includes /etc/mail/aliasesPL.
#
# Mark Huang <mlhuang@cs.princeton.edu>
# Copyright (C) 2005 The Trustees of Princeton University
#
# $Id$
#

import os, sys
import plcapilib
import tempfile
from sets import Set

# Procmail command for aliases. See plc/mail/procmailrc for how these
# two scripts interact with each other.
procmail = "|/usr/bin/procmail -m /etc/mail/procmailrc"

# Parse additional options
shortopts = "n"
longopts = ["dryrun"]
moreusage = """
usage: %s [OPTION]... [slice|pi|tech] [slicename|sitename]

gen_aliases.py options:
        -n              Dry run, do not sync memberships or write files
""" % sys.argv[0]

# Debug
dryrun = False

(plcapi, moreopts, argv) = plcapilib.plcapi(globals(), sys.argv, shortopts, longopts, moreusage)
for opt, optval in moreopts.iteritems():
    if opt == "-n" or opt == "--dryrun":
        dryrun = True

# Parse /usr/share/doc/plc/accounts.txt (or /etc/passwd)
def passwd(path = '/etc/passwd'):
    entries = []

    required = ['account', 'password', 'uid', 'gid', 'gecos', 'directory', 'shell']
    optional = ['email', 'servers']

    for line in file(path):
        # Comment
        if line.strip() == '' or line[0] in '#':
            continue
        # princeton_mlh:x:...
        fields = line.strip().split(':')
        if len(fields) < len(required):
            continue
        # {'account': 'princeton_mlh', 'password': 'x', ...}
        entries.append(dict(zip(required + optional, fields)))

    return entries

def GetPIs(site_id_or_login_base):
    pis = []
    for site in GetSites([site_id_or_login_base], ['person_ids']):
        persons = GetPersons(site['person_ids'], ['email', 'roles', 'enabled'])
        pis += filter(lambda person: 'pi' in person['roles'] and person['enabled'], persons)
    if pis:
        return [pi['email'] for pi in pis]
    return ["NO-pi"]

def GetTechs(login_base):
    techs = []
    for site in GetSites([login_base], ['person_ids']):
        persons = GetPersons(site['person_ids'], ['email', 'roles', 'enabled'])
        techs += filter(lambda person: 'tech' in person['roles'] and person['enabled'], persons)
    if techs:
        return [tech['email'] for tech in techs]
    return ["NO-tech"]

def GetSliceUsers(name):
    # Get the users of the slice
    enabledpersons = []
    users = []
    for slice in GetSlices([name], ['site_id', 'person_ids']):
        persons = GetPersons(slice['person_ids'], ['email', 'enabled'])
        enabledpersons += filter(lambda person: person['enabled'], persons)
        users += [person['email'] for person in enabledpersons]
        # Add all the PIs for the site
        users += GetPIs(slice['site_id'])
    # Remove duplicates and sort
    users = list(Set(users))
    users.sort()
    return users

# Called every 10 minutes without arguments to sync
# {announce,pis,techs,cvs}@lists.planet-lab.org memberships and to
# regenerate /etc/mail/{aliasesPL,virtusertable,local-host-names}.
if len(argv) == 0:
    flags = ""
    if dryrun:
        flags += "-n"
        local_host_names = virtusertable = aliases = cvs_config = sys.stdout
    else:
        local_host_names = file("local-host-names", 'w')
        virtusertable = file("virtusertable", 'w')
        aliases = file("aliasesPL", 'w')
        cvs_config = tempfile.NamedTemporaryFile()

    # Parse /usr/share/doc/plc/accounts.txt. XXX Should probably make
    # CVS access a DB property.
    cvs_nonmembers = []
    for pw in passwd('/usr/share/doc/plc/accounts.txt'):
        # Only allow posts from those with implicit or explicit access to
        # all servers or explicit access to the CVS server
        if pw.has_key('servers') and pw['servers'] not in ['*', 'cvs']:
            continue

        # System users are those with UIDs greater than 2000 and less than 3000
        if int(pw['uid']) >= 2000 and int(pw['uid']) < 3000:
            continue

        cvs_nonmembers.append("'" + pw['account'] + "@planet-lab.org" + "'")

    # Update accept_these_nonmembers property of the CVS mailing
    # list. This ensures that those with access to the CVS server are
    # able to post loginfo messages when they check in files. The CVS
    # server's sendmail setup is configured to masquerade as
    # @planet-lab.org.
    cvs_config.write("accept_these_nonmembers = [" + ", ".join(cvs_nonmembers) + "]\n")
    cvs_config.flush()
    if not dryrun:
        config_list = os.popen("/var/mailman/bin/config_list -i %s cvs" % cvs_config.name)
        if config_list.close() is not None:
            raise Exception, "/var/mailman/bin/config_list cvs failed"

    # Get all emails
    announce = []
    pis = []
    techs = []
    for person in GetPersons({'enabled': True}, ['person_id', 'email', 'roles']):
        announce.append(person['email'])
        if 'pi' in person['roles']:
            pis.append(person['email'])
        if 'tech' in person['roles']:
            techs.append(person['email'])

    # Generate announce@lists.planet-lab.org membership

    # Merge in membership of announce-additions
    list_members = os.popen("/var/mailman/bin/list_members announce-additions", 'r')
    announce += map(lambda line: line.strip(), list_members.readlines())
    list_members.close()
    # Remove duplicates and sort
    announce = list(Set(announce))
    announce.sort()
    # Update membership
    sync_members = os.popen("/var/mailman/bin/sync_members %s -w=yes -g=yes -f - announce" % flags, 'w')
    sync_members.write("\n".join(announce))
    if sync_members.close() is not None:
        raise Exception, "/var/mailman/bin/sync_members announce failed"

    # Generate {pis,techs}@lists.planet-lab.org membership

    # Remove duplicates and sort
    pis = list(Set(pis))
    pis.sort()
    techs = list(Set(techs))
    techs.sort()
    # Update membership
    sync_members = os.popen("/var/mailman/bin/sync_members %s -w=no -g=no -f - pis" % flags, 'w')
    sync_members.write("\n".join(pis))
    if sync_members.close() is not None:
        raise Exception, "/var/mailman/bin/sync_members pis failed"
    sync_members = os.popen("/var/mailman/bin/sync_members %s -w=no -g=no -f - techs" % flags, 'w')
    sync_members.write("\n".join(techs))
    if sync_members.close() is not None:
        raise Exception, "/var/mailman/bin/sync_members techs failed"

    # Generate local-host-names file
    local_host_names.write("planet-lab.org\n")
    local_host_names.write("slices.planet-lab.org\n")
    local_host_names.write("sites.planet-lab.org\n")

    # Generate SLICENAME@slices.planet-lab.org mapping and
    # slice-SLICENAME alias
    for slice in GetSlices(None, ['name']):
        name = slice['name']
        virtusertable.write("%s@slices.planet-lab.org\tslice-%s\n" % \
                            (name, name))
        aliases.write("slice-%s: \"%s slice %s\"\n" % \
                      (name, procmail, name))

    # Generate {pi,tech}-LOGINBASE@sites.planet-lab.org and
    # {pi,tech}-LOGINBASE alias
    for site in GetSites(None, ['login_base']):
        for prefix in ['pi', 'tech']:
            # This is probably unnecessary since the mapping is 1-1
            virtusertable.write("%s-%s@sites.planet-lab.org\t%s-%s\n" % \
                                (prefix, site['login_base'], prefix, site['login_base']))
            aliases.write("%s-%s: \"%s %s %s\"\n" % \
                          (prefix, site['login_base'], procmail, prefix, site['login_base']))

    # Generate special cases. all-pi and all-tech used to be aliases
    # for all PIs and all techs. They are now mailing lists like
    # announce. NO-pi and NO-tech notify support that a site is
    # missing one or the other and are used by some scripts.
    aliases.write("all-pi: pis\n")
    aliases.write("all-tech: techs\n")
    aliases.write("NO-pi: support\n")
    aliases.write("NO-tech: support\n")

    if not dryrun:
        local_host_names.close()
        virtusertable.close()
        aliases.close()
        cvs_config.close()

# Otherwise, print space-separated list of aliases
elif len(argv) == 2:
    if argv[0] == "slice":
        print " ".join(GetSliceUsers(argv[1]))
    elif argv[0] == "pi":
        print " ".join(GetPIs(argv[1]))
    elif argv[0] == "tech":
        print " ".join(GetTechs(argv[1]))

else:
    plcapi.usage(moreusage)
    sys.exit(1)
