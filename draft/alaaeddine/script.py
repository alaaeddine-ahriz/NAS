import json

def generate_ospf_config(ospf_data, router_name):
    config = f"router ospf {ospf_data['process_id']}\n"
    for network in ospf_data['networks']:
        config += f" network {network['address']} {network['mask']} area {network['area']}\n"
    return config

def generate_bgp_config(bgp_data):
    config = f"router bgp {bgp_data['local_as']}\n"
    for neighbor in bgp_data['neighbors']:
        config += f" neighbor {neighbor['ip']} remote-as {neighbor['remote_as']}\n"
    for network in bgp_data['advertised_networks']:
        config += f" network {network}\n"
    return config

def generate_interface_config(interface_data):
    config = ""
    for interface in interface_data:
        config += f"interface {interface['name']}\n"
        config += f" ip address {interface['ip_address']} {interface['subnet_mask']}\n"
        config += f" description {interface['description']}\n"
        config += " no shutdown\n"
    return config

def generate_config_files(intent_file):
    with open(intent_file, 'r') as file:
        data = json.load(file)
    
    for router in data['routers']:
        config = f"!\nhostname {router['name']}\n!\n"
        config += generate_interface_config(router['interfaces'])
        config += "!\n"
        
        ospf_data = next((ospf for ospf in data['ospf'] if router['name'] in ospf['routers']), None)
        if ospf_data:
            config += generate_ospf_config(ospf_data, router['name'])

        bgp_data = next((bgp for bgp in data['bgp'] if bgp['router'] == router['name']), None)
        if bgp_data:
            config += "!\n"
            config += generate_bgp_config(bgp_data)

        # Saving the configuration to a file
        config_filename = f"{router['name']}_config.txt"
        with open(config_filename, 'w') as config_file:
            config_file.write(config)
        print(f"Configuration for {router['name']} written to {config_filename}")

# Assuming the intent file is named 'network_intent.json'
intent_file = 'network_intent.json'
generate_config_files(intent_file)
