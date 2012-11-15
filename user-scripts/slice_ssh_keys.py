# This utility is designed for use with an OMF Experiment Controller
# 
import sys
import os.path
from xmlrpclib import ServerProxy
from optparse import OptionParser

default_host="www.planet-lab.eu"
def main ():
  usage="""Usage: 
  %prog [--plc plc_hostname] slicename dirname
Purpose: 
  issues a GetSliceSshKeys to the MyPLC instance at <hostname>, and
  store the keys related to slice <slicename> in <dirname> 
  in a format suitable for use with the OMF Experiment Controller"""

  parser=OptionParser(usage=usage)
  parser.add_option ("-p","--plc",action='store',dest='myplc_host',
                     default=default_host, 
                     help="the hostname where your myplc is running")
  (options,args) = parser.parse_args()
  if len(args) != 2:
    parser.print_help()
    sys.exit(1)
  (slicename, dirname) = args
  plc_hostname=options.myplc_host
  plc_url="https://%s/PLCAPI/"%plc_hostname
  ple=ServerProxy(plc_url,allow_none=True)
  auth={'AuthMethod':'anonymous'}
  public_keys=ple.GetSliceSshKeys(auth,slicename)
  if not public_keys:
    print ("Cannot find any key for slice %s, check slicename ? "%slicename)
    return 1
  for (hostname, pubkey) in public_keys.items(): 
    filename = os.path.join (dirname, hostname)
    file = open(filename, "w")
    filename.write(pubkey)
    filename.close()

if __name__ == '__main__':
  sys.exit(main())


