# -*-sh-*-
# this file defines a few convenience bash shorthands for managing myplc nodes
# it is installed in /usr/share/myplc/aliases
# you might wish to use it in your own bash startup files (.profile/.bashrc)

ssh_options="-o BatchMode=yes -o StrictHostKeyChecking=no"

function node_key () {
    key="$1"; shift
    hostname="$1"; shift
    echo Running "$@" on root@"$hostname"
    ssh $ssh_options -i "$key" "root@$hostname" "$@"
}

function nodes_key () {
    key="$1"; shift
    filename="$1"; shift
    for hostname in $(grep -v '#' $filename); do
	node_boot "$hostname" "$key" "$@"
    done
}

function node_dbg () {
    [[ -z "$@" ]] && { echo "Usage: $0 hostname [command]" ; return 1; }
    node_key /etc/planetlab/debug_ssh_key.rsa "$@"
}
function node_boot () {
    [[ -z "$@" ]] && { echo "Usage: $0 hostname [command]" ; return 1; }
    node_key /etc/planetlab/root_ssh_key.rsa "$@"
}

function nodes_dbg () {
    [[ -z "$@" ]] && { echo "Usage: $0 hosts_file [command]" ; return 1; }
    node_keys /etc/planetlab/debug_ssh_key.rsa "$@"
}
function nodes_boot () {
    [[ -z "$@" ]] && { echo "Usage: $0 hosts_file [command]" ; return 1; }
    nodes_key /etc/planetlab/root_ssh_key.rsa "$@"
}

function clear_keys () {
    for hostname in "$@"; do	
        sed -i "/$hostname/d" ~/.ssh/known_hosts
    done
}
	