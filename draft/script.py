import json

def generate_interface_config(interface_data):
    config = ""
    for interface in interface_data:
        config += f"interface {interface['name']}\n"
        config += f" ip address {interface['ip_address']} {interface['subnet_mask']}\n"
        config += f" description {interface['description']}\n"
        if "ospf" in interface:
            ospf = interface["ospf"]
            config += f" ip ospf {ospf['process_id']} area {ospf['area']}\n"
        config += " no shutdown\n"
    return config

def generate_bgp_config(bgp_data):
    config = f"router bgp {bgp_data['local_as']}\n"
    for neighbor in bgp_data['neighbors']:
        config += f" neighbor {neighbor['neighbor_ip']} remote-as {neighbor['remote_as']}\n"
    for network in bgp_data['advertised_networks']:
        config += f" network {network}\n"
    return config

def generate_config_files(intent_file):
    with open(intent_file, 'r') as file:
        data = json.load(file)
    
    for router in data['routers']:
        config = f"!\nhostname {router['name']}\n!\n"
        config += generate_interface_config(router['interfaces'])
        config += "!\n"
        if "bgp" in router:
            config += generate_bgp_config(router['bgp'])
            config += "!\n"

        # Saving the configuration to a file
        config_filename = f"{router['name']}_config.txt"
        with open(config_filename, 'w') as config_file:
            config_file.write(config)
        print(f"Configuration for {router['name']} written to {config_filename}")

# Assuming the intent file is named 'network_intent.json'
intent_file = 'C:\\Users\\alaae\\Documents\\INSA Lyon\\3 TCA\\Projet NAS\\NAS\\draft\\alaaeddine\\network_intent.json'
generate_config_files(intent_file)
