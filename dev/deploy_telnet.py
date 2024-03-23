import telnetlib
import time
import os

def apply_config_to_router(router_ip, router_port, config_file_path):
    try:
        # Open and read the configuration file
        with open(config_file_path, 'r') as file:
            config_commands = file.readlines()

        # Connect to the router via Telnet
        tn = telnetlib.Telnet(router_ip, router_port)
        
        tn.write(b"enable\n")
        time.sleep(1)  # Adjust this based on your device's response time
        tn.write(b"\n")  # Assuming no enable password, just send a newline

        # Enter configuration mode
        tn.write(b"configure terminal\n")
        time.sleep(1)  # Adjust this based on your device's response time

        # Iterate over commands in the config file and apply them
        for cmd in config_commands:
            tn.write(cmd.encode('ascii'))
            # print(cmd.encode('ascii') + b"\n")
            # After sending a command, read the response
            time.sleep(0.25)  # Adjust as necessary

            time.sleep(0.25)  # Adjust delay as necessary

        # Exit configuration mode, save the configuration, and exit
        tn.write(b"end\n")
        tn.write(b"write memory\n")
        tn.write(b"exit\n")

        print(f"Configuration applied to router at {router_ip} from {config_file_path}")
    except Exception as e:
        print(f"Failed to apply configuration to router at {router_ip}: {e}")

# Directory containing the configuration files
config_dir = 'dev/config_files'

# List of routers with their IP addresses, Telnet ports, and corresponding config file names
routers = [
    {"ip": "localhost", "port": 5002, "config_file": "CE1_config.txt"},
    {"ip": "localhost", "port": 5003, "config_file": "PE1_config.txt"},
    # Add more router entries as needed
]

# Iterate over the routers and apply their configurations
for router in routers:
    config_file_path = os.path.join(config_dir, router["config_file"])
    apply_config_to_router(router["ip"], router["port"], config_file_path)
