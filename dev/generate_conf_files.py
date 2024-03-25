import os
import json
from datetime import datetime

# Define the directory where configuration files will be saved
config_dir = 'dev/config_files'

# Ensure the directory exists
os.makedirs(config_dir, exist_ok=True)

# Define the current UTC time
current_utc_time = datetime.utcnow()

# Format the date and time in the specified format: "HH:MM:SS UTC Day Mon Year"
formatted_time = current_utc_time.strftime('%H:%M:%S UTC %a %b %d %Y')

formatted_time


def generate_static_config_1(timestamp=formatted_time):
    return f"""
! Last configuration change at {timestamp}
!
version 15.2
service timestamps debug datetime msec
service timestamps log datetime msec
!
boot-start-marker
boot-end-marker
!
"""

def generate_static_config_2():
    return f"""
!
no aaa new-model
no ip icmp rate-limit unreachable
ip cef
!
no ip domain lookup
no ipv6 cef
!
multilink bundle-name authenticated
!
ip tcp synwait-time 5
!
"""

def generate_vrf_config(vrfs, bgp):
    config = ""
    for vrf in vrfs:
        config += f"!\n"
        config += f"vrf definition {vrf['nom_vrf']}\n"
        config += f" rd {bgp['local_as']}:{vrf['route_distinguisher_client']}\n"
        config += f" route-target export {vrf['route_target']}\n"
        config += f" route-target import {vrf['route_target']}\n"
        config += f" !\n"
        config += f" address-family ipv4\n exit-address-family\n"
        config += f"!"
    return config

def generate_interface_config(interfaces):
    config = ""
    ospf_activated = False
    ospf_process_id = ""
    for interface in interfaces:
        config += f"interface {interface['name']}\n"
        if "vrf" in interface:
            config += f"vrf forwarding {interface['vrf']}\n"
        config += f" ip address {interface['ip_address']} {interface['subnet_mask']}\n"
        config += " negotiation auto\n"
        if "ospf" in interface:
            config += f" ip ospf {interface['ospf']['process_id']} area {interface['ospf']['area']}\n"
            ospf_activated = True
            ospf_process_id = f"{interface['ospf']['process_id']}"
        if interface.get("mpls", False):
            config += " mpls ip\n"
        config += "!\n"
    if ospf_activated:
        config += f"router ospf {ospf_process_id}\n"
        config += f" redistribute connected subnets\n"
        config += "!\n"
    return config

def generate_bgp_config(bgp, router_interface_ips, vrfs=None):
    config = f"router bgp {bgp['local_as']}\n"
    config += f" bgp router-id {bgp['bgp_id']}\n"
    config += " bgp log-neighbor-changes\n"

    # Check and prepare global neighbors
    for neighbor in bgp.get('neighbors', []):
        if 'vrf' not in neighbor or not neighbor['vrf']:
            # Assuming a neighbor might not always have 'name', handle accordingly
            neighbor_ip = ''
            if 'name' in neighbor and 'interface' in neighbor:
                neighbor_name = neighbor['name']
                neighbor_interface = neighbor['interface']
                neighbor_ip = router_interface_ips.get(neighbor_name, {}).get(neighbor_interface, "")
            elif 'neighbor_ip' in neighbor:
                neighbor_ip = neighbor['neighbor_ip']
            
            if neighbor_ip:
                config += f" neighbor {neighbor_ip} remote-as {neighbor.get('remote_as', '')}\n"
                if 'update_source' in neighbor:
                    config += f" neighbor {neighbor_ip} update-source {neighbor['update_source']}\n"
    
    # Configure global address-family for ipv4
    config += " address-family ipv4\n"
    for neighbor in bgp.get('neighbors', []):
        if 'vrf' not in neighbor or not neighbor['vrf']:
            neighbor_ip = neighbor.get('neighbor_ip', '')
            if 'name' in neighbor and 'interface' in neighbor:
                neighbor_name = neighbor['name']
                neighbor_interface = neighbor['interface']
                neighbor_ip = router_interface_ips.get(neighbor_name, {}).get(neighbor_interface, "")
            if neighbor_ip:
                config += f"  neighbor {neighbor_ip} activate\n"
    config += " exit-address-family\n"

    # Configuring VRF-specific neighbors
    if vrfs:
        for vrf in vrfs:
            config += f" address-family ipv4 vrf {vrf['nom_vrf']}\n"
            for neighbor in bgp.get('neighbors', []):
                if neighbor.get('vrf') == vrf['nom_vrf']:
                    neighbor_ip = neighbor.get('neighbor_ip', '')
                    if 'name' in neighbor and 'interface' in neighbor:
                        neighbor_name = neighbor['name']
                        neighbor_interface = neighbor['interface']
                        neighbor_ip = router_interface_ips.get(neighbor_name, {}).get(neighbor_interface, "")
                    if neighbor_ip:
                        config += f"  neighbor {neighbor_ip} remote-as {neighbor.get('remote_as', '')}\n"
                        if 'update_source' in neighbor:
                            config += f"  neighbor {neighbor_ip} update-source {neighbor['update_source']}\n"
                        config += f"  neighbor {neighbor_ip} activate\n"
            config += " exit-address-family\n"
    
    config += "!\n"
    return config


def generate_line_config():

    return """
!
ip forward-protocol nd
!
no ip http server
no ip http secure-server
!
control-plane
!
line con 0
 exec-timeout 0 0
 privilege level 15
 logging synchronous
 stopbits 1
line aux 0
 exec-timeout 0 0
 privilege level 15
 logging synchronous
 stopbits 1
line vty 0 4
 login
!
end
"""

def extract_router_interface_ips(intent_data):
    """
    Extracts the IP addresses for each router's interfaces from the network intent data.

    :param intent_data: The network intent data loaded from the JSON file.
    :return: A dictionary mapping router and interface names to their IP addresses.
    """
    router_interface_ips = {}
    for router in intent_data['routers']:
        interface_ips = {}
        for interface in router['interfaces']:
            # Assuming interface names are unique per router
            interface_ips[interface['name']] = interface['ip_address']
        router_interface_ips[router['name']] = interface_ips
    return router_interface_ips

def generate_config_files(intent_file_path):
    with open(intent_file_path, 'r') as file:
        intent_data = json.load(file)
    
    # Extract router interface IPs
    router_interface_ips = extract_router_interface_ips(intent_data)

    for router in intent_data['routers']:
        config = f"hostname {router['name']}\n"

        config += generate_static_config_1()

        # Generate VRF config if needed
        if 'vrf' in router:
            config += generate_vrf_config(router['vrf'], router['bgp'])

        config += generate_static_config_2()
        
        config += generate_interface_config(router['interfaces'])
        
        # Generate BGP config if needed, now using router_interface_ips
        if 'bgp' in router:
            vrfs = router.get('vrf', None)
            config += generate_bgp_config(router['bgp'], router_interface_ips, vrfs)

        config += generate_line_config()

        # Saving the configuration to a file
        config_filename = os.path.join(config_dir, f"{router['name']}_config.txt")
        with open(config_filename, 'w') as config_file:
            config_file.write(config)
        print(f"Configuration for {router['name']} written to {config_filename}")

# To use this script, make sure you have a 'network_intent.json' file in the same directory
intent_file_path = 'C:\\Users\\nathan.lehodey\\Desktop\\NAS\\dev\\network_intent copy 2.json'
generate_config_files(intent_file_path)
