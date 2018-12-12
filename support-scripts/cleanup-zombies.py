#!/usr/bin/env python3

# node manager has a few working assumptions, like
# if a domain d does not exist, there is no /vservers/d 

# this utility tries to detect and assess potentially
# conflictual situations, that could prevent nodemanager
# from recovering properly
#
# the logic is simply to find zombie-containers, i.e.
# VMs that do have a workdir in /vservers/<zombie>
# but that are not reported as running by virsh --list
# which suggests they have been improperly trashed
###
#
# then we trash them but for that some subdirs must be
# btrfs-subvolume-delete'd and not rm-rf'ed
# 

import subprocess
import glob
import os, os.path
from argparse import ArgumentParser

def running_domains(all_domains=False):
    command = [
        'virsh',
    	'-c',
        'lxc:///',
        'list',
        '--name',
    ]
    if all_domains:
        command.append('--all')
    names_string = subprocess.check_output(
        command,
        universal_newlines = True,
        stdin = subprocess.DEVNULL,
        )
    names = [ name for name in names_string.strip().split("\n") if name ]
    return names

def existing_vservers():
    all_dirs = glob.glob("/vservers/*")
    dirs = ( dir for dir in all_dirs if os.path.isdir(dir) )
    dirnames = ( path.replace("/vservers/", "") for path in dirs)
    return dirnames

def display_or_run_commands(commands, run):
    if commands:
        if not run:
            print("---- You should run")
            for command in commands:
                print((" ".join(command)))
        else:
            for command in commands:
                print(("Running {}".format(" ".join(command))))
                retcod = subprocess.call(command)
                if retcod != 0:
                    print(("Warning: failed with retcod = {}".format(retcod)))

def main():
    parser = ArgumentParser()
    # the default is to cowardly show commands to run
    # use --run to actually do it
    parser.add_argument("-r", "--run", action='store_true', default=False,
                        help="actually run commands, that otherwise are just displayed")
    parser.add_argument("-d", "--deep", action='store_true', default=False,
                        help="spot and destroy containers that are known to libvirt, but not running")
    parser.add_argument("-v", "--verbose",
                        help="also displays variable definitions to cut-and-paste for the shell")
    args = parser.parse_args()

    known_containers = set(running_domains(all_domains=True))
    running_containers = set(running_domains())
    not_running_containers = known_containers - running_containers
    
    if args.deep:
        commands = []
        print(("Found {} containers that are known but not running".format(len(not_running_containers))))
        for not_running_container in not_running_containers:
            commands.append(['userdel', not_running_container])
            commands.append(['virsh', '-c', 'lxc:///', 'undefine', not_running_container])
        display_or_run_commands(commands, args.run)

    existing_containers = set(existing_vservers())
    zombies_containers = existing_containers - running_containers

    # the prefix used to locate subvolumes
    flavour_prefixes = [
        'onelab-',
        'lxc-',
        'omf-',
        'planetflow-',
        ]

    # we need to call 'btrfs subvolume delete' on these remainings
    # instead of just 'rm'
    if zombies_containers:
        print(("-------- Found {} existing, but not running, containers".format(len(zombies_containers))))
        commands = []
        zombie_dirs = ["/vservers/"+z for z in zombies_containers]
        if args.verbose:
            print(("zombie_dirs='{}'".format(" ".join(zombie_dirs))))
        subvolumes = [ path
                       for z in zombies_containers
                       for prefix in flavour_prefixes
                       for path in glob.glob("/vservers/{z}/{prefix}*".format(z=z, prefix=prefix))]
        if subvolumes:
            if args.verbose:
                print(("zombie_subvolumes='{}'".format(" ".join(subvolumes))))
            for subvolume in subvolumes:
                commands.append([ 'btrfs', 'subvolume', 'delete', subvolume])
        for zombie_dir in zombie_dirs:
            commands.append([ 'btrfs', 'subvolume', 'delete', zombie_dir ])
        display_or_run_commands(commands, args.run)
        # find the containers dirs that might still exist
        zombie_dirs = [ path for path in zombie_dirs if os.path.isdir(path) ]
        commands = [ ['rm', '-rf', path] for path in zombie_dirs ]
        display_or_run_commands(commands, args.run)
        
    #### should happen much less frequently
    weirdos_containers = running_containers - existing_containers
    if weirdos_containers:
        print(("-------- Found {} running but non existing".format(len(weirdos_containers))))
        for w in weirdos_containers:
            print(("/vservers/{}".format(w)))

    print(("{} slices are currently running".format(len(running_containers))))
main()    
