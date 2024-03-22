import json

from datetime import datetime

# Define the current UTC time
current_utc_time = datetime.utcnow()

# Format the date and time in the specified format: "HH:MM:SS UTC Day Mon Year"
formatted_time = current_utc_time.strftime('%H:%M:%S UTC %a %b %d %Y')

formatted_time


def generate_static_config(timestamp=formatted_time):
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

def generate_interface_config(interfaces):
    config = ""
    for interface in interfaces:
        config += f"interface {interface['name']}\n"
        config += f" ip address {interface['ip_address']} {interface['subnet_mask']}\n"
        config += " negotiation auto\n"
        if "ospf" in interface:
            config += f" ip ospf {interface['ospf']['process_id']} area {interface['ospf']['area']}\n"
        if interface.get("mpls", False):
            config += " mpls ip\n"
        config += "!\n"
    return config

def generate_bgp_config(bgp):
    config = f"router bgp {bgp['local_as']}\n"
    config += f" bgp router-id {bgp['bgp_id']}\n" 
    config += " bgp log-neighbor-changes\n"
    for neighbor in bgp['neighbors']:
        config += f" neighbor {neighbor['neighbor_ip']} remote-as {neighbor['remote_as']}\n"
    config += " !\n address-family ipv4\n"
    for neighbor in bgp['neighbors']:
        config += f"  neighbor {neighbor['neighbor_ip']} activate\n"
    config += " exit-address-family\n!\n"
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

def generate_config_files(intent_file_path):
    with open(intent_file_path, 'r') as file:
        intent_data = json.load(file)
    
    for router in intent_data['routers']:
        config = f"hostname {router['name']}\n"
        config += generate_static_config()
        config += generate_interface_config(router['interfaces'])
        # Generate BGP config if needed
        if 'bgp' in router:
            config += generate_bgp_config(router['bgp'])
        config += generate_line_config()

        # Saving the configuration to a file
        config_filename = f"{router['name']}_config.txt"
        with open(config_filename, 'w') as config_file:
            config_file.write(config)
        print(f"Configuration for {router['name']} written to {config_filename}")

# To use this script, make sure you have a 'network_intent.json' file in the same directory
intent_file_path = 'C:\\Users\\alaae\\Documents\\INSA Lyon\\3 TCA\\Projet NAS\\NAS\\draft\\network_intent.json'
generate_config_files(intent_file_path)
