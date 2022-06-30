#!/usr/bin/env python3

# Program: Network Sweep (A ping sweep variant in Python)
# Author: Maxwell Nana Forson <nanaforsonjnr@gmail.com>
# </>theLazyProgrammer^_^
# Date: Mon Jun 27, 2022

import argparse
import ipaddress
import subprocess
import sys
import netifaces

# CLI arguments, more to come...
net_parser = argparse.ArgumentParser(prog='netswp',
                                     description="Description: mini IPv4 and IPv6 ping sweep utility",
                                     allow_abbrev=True,
                                     prefix_chars='/-',
                                     )
net_parser.add_argument('--network', '-n',
                        help='target network address (required)',
                        metavar='<network_address>',
                        required=True,

                        )
# the interface paramter is not available if system is Windows-based
if not sys.platform.startswith('win'):    
    net_parser.add_argument('--interface', '-i', '/i',
                            help='specify interface to listen on (default: best interface)',
                            metavar='<interface>'
                            )

ping_sweep = net_parser.parse_args()

total_ip_addresses = 0
active_ip_addresses = 0
inactive_ip_addresses = 0


def linux_os_ping_sweep(network_address):
    """
    *nix systems ping sweep
    """
    output = None
    for ip_address in network_address:
        # skip network address and broadcast addresses
        if (ip_address == network.broadcast_address) or \
                (ip_address == network.network_address):
            continue
        try:
            # use user specified interface if received on the CLI
            output = None
            if ping_sweep.interface:
                output = subprocess.Popen(
                    f'/bin/ping -c 1 {ip_address} -I {ping_sweep.interface} -w 1'.split(),
                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
                ).communicate()[0]

            # default ping sweep, uses the best interface available
            output = subprocess.Popen(
                f'/bin/ping -c 1 {ip_address} -w 1'.split(),
                stdout=subprocess.PIPE, encoding='utf-8',
                stderr=subprocess.DEVNULL
            ).communicate()[0]

        except KeyboardInterrupt:
            print('\n[~_~] Ping sweep aborted...')
            quit()

        connection_info(output)

    ping_summary_report()


def win_os_ping_sweep(network_address):
    """
    Windows systems ping sweep.
    The 'interface' parameter is not yet implemented... I was having a hard figuring
    that out. So the normal ping behavior will be used.
    The parameter won't even show in the help menu
    """
    output = None
    for ip_address in network_address:
        # skip network address and broadcast addresses
        if (ip_address == network.broadcast_address) or \
                (ip_address == network.network_address):
            continue
        try:
            # use user specified interface if received on the CLI
            output = None
            if ping_sweep.interface:
                output = subprocess.Popen(
                    f'ping /n 1 {ip_address} -I {ping_sweep.interface} /w 1'.split(),
                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
                ).communicate()[0]

        except KeyboardInterrupt:
            print('\n[~_~] Ping sweep aborted...')
            quit()

        connection_info(output)

    ping_summary_report()


def connection_info(output):
    """
    Verbose information on the state of the connection
    """
    global total_ip_addresses
    global active_ip_addresses
    global inactive_ip_addresses
    try:
        if sys.platform.startswith('linux'):    
            ip_address = output.split()[1]
        elif sys.platform.startswith('win'):
            ip_address = output.split()[2].replace(':', '')
    except IndexError:
        # the only time the output is empty is when an IPv6 network in unreachable
        # therefore, no elements are available in the list
        print('[!] Network is unreachable')
        quit()
    else:
        total_ip_addresses += 1
        if "1 received" in output or "Lost = 0" in output:
            print(f"[+] {ip_address} is up")
            active_ip_addresses += 1
        elif "0 received" in output or 'Request timeout':
            print(f'[!] {ip_address} is unreachable')
            inactive_ip_addresses += 1


def ping_summary_report():
    """
    Prints a summary report on the Ping Sweep activity
    """
    print(f'\n[*_*] Ping Sweep Summary [Total Host Addresses: {total_ip_addresses}]')
    print(f'\t[***] {active_ip_addresses} IP address(es) are reachable')
    print(f'\t[*!*] {inactive_ip_addresses} IP address(es) are unreachable')


# convert command-line string argument into an IPv4 or IPv6 network
try:
    network = ipaddress.ip_network(ping_sweep.network, strict=False)

except ipaddress.NetmaskValueError as netmask_err:
    print(netmask_err)

except ValueError as v_err:
    print(f'[!*] {v_err}\n[!*] Specify a valid network address')
    print('[**] e.g. 172.30.16.0/20 or fd00:face:cafe:fade::/64')
    quit()
    
# proceed if no errors were raised
else:
    if network:
        print('[*_*] Starting Ping Sweep...')
        try:
            if ping_sweep.interface is None:
                pass

            elif ping_sweep.interface and (ping_sweep.interface in netifaces.interfaces()):
                interface = ping_sweep.interface
                print(f'[_^_] {ping_sweep.interface} interface selected\n')

            elif ping_sweep.interface not in netifaces.interfaces():
                # help when incorrect interface is given
                print('[!] Verify your interface name is correct')
                print('[!] Below are the list of available interface on this system')
                for iface in netifaces.interfaces():
                    print(f'\t[+] {iface}')
                quit(3)

        except NameError:
            interface = None

        # *nix system types
        if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            linux_os_ping_sweep(network_address=network)

        # windows systems    
        if sys.platform.startswith('win'):
            win_os_ping_sweep(network_address=network)

    # /31 and /32 addresses are not implemented...
    # I know what you're thinking, /31 is a valid network address.
    # I had some issues with it, the ping utility complains about pinging the broadcast address
    if (isinstance(network, ipaddress.IPv4Network)) and \
            ('/32' in str(network)) or ('/31' in str(network)):
        if sys.platform.startswith('linux'):
            subprocess.call('clear')
        elif sys.platform.startswith('win'):
            subprocess.call('cls')
        print(f'[-] Not accepted or implemented!')
        print('[-] Specify a valid network address to proceed')
        quit()


# TODO: *nix-based and Windows-bases Oses should be clearly defined 
        # -> *nix-based completed. (Tested on Ubuntu Linux)
        # -> Windows systems(Almost)
# TODO: use the threading module to make the program execution sleeker
        # the current operation time is relative to the range of IP addresses received
# TODO: optional -> calculate the time it takes to ping sweep the largest network (use /20)