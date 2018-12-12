#!/usr/bin/env plcsh
import sys
from optparse import OptionParser

try:
    vsys_tag_type=GetSliceTags({'tagname':'vsys'})[0]
except:
    print("Can't find tag vsys - exiting")
    sys.exit(1)

def add_value (slice, value, options):
    (slice_id, slice_name ) = (slice['slice_id'], slice['name'])
    if options.dry_run:
        print("Would add vsys=%s to slice %s (%d)"%(value,slice_name,slice_id))
        return
    if options.verbose:
        print("Adding vsys=%s to slice %s (%d)"%(value,slice_name,slice_id))
    AddSliceTag (slice_id, 'vsys', value)


def check (options):
    # retrieve applicable slices
    filter={}
    if options.pattern: filter['name']=options.pattern
    if not options.all: filter['peer_id']=None
    slices=GetSlices(filter)
    # find list of values 
    if options.tags:
        values=options.tags
    else:
        values= [ y for y in [ x.strip() for x in api.config.PLC_VSYS_DEFAULTS.split(',') ] if y ]
    # let's go
    for value in values:
        slice_tags=GetSliceTags({'tagname':'vsys','value':value})
        names_with_tag = [ st['name'] for st in slice_tags ]
        counter=0
        for slice in slices:
            if slice['name'] not in names_with_tag:
                add_value (slice,value,options)
                counter+=1
        if options.verbose:
            print("Found %d slices for which %s is missing"%(counter,value))

def main ():
    usage="""Usage: %prog
  Checks that a set of slices has a set of vsys tags set
Example:
  %prog -- -p 'inria*' -t promisc -t fd_tuntap -vn
"""
    parser = OptionParser(usage=usage)
    parser.add_option("-t","--tag",action='append',default=[],dest='tags',
                      help="ignore PLC config and provide tags on the command line - can be repeated")
    parser.add_option("-a","--all",action='store_true',default=False,
                      dest='all',help="Apply on foreign slices as well (default is local only)")
    parser.add_option("-p","--pattern",action='store',default=None,
                      dest='pattern',help="Apply on slices whose name matches pattern")
    parser.add_option("-v", "--verbose", action = "store_true", default = False, 
                      dest='verbose', help="be verbose")
    parser.add_option("-n", "--dry-run", action = "store_true", default = False, 
                      dest='dry_run', help="don't actually do it")
    (options, args) = parser.parse_args()

    if args: 
        parser.print_help()
        sys.exit(1)

    check (options)
        
if __name__ == "__main__":
    main()
