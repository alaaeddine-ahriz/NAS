import telnetlib
import time

# The hostname or IP address of the device to connect to
HOST = "localhost"
# The telnet port
PORT = 5004
# Timeout in seconds
TIMEOUT = 25

# List of commands to send
commands = [
    "enable\n",
    "conf t\n",
    "hostname TOZ1\n",
    "end\n",
    "exit\n",
]

def read_until_prompt(tn, prompts=[b'>', b'#'], timeout=10):
    """Reads until one of the specified prompts is found."""
    read_data = b''
    while not any(prompt in read_data for prompt in prompts):
        read_data += tn.read_some()
    return read_data

# Function to connect via telnet and execute commands
def telnet_execute_commands(host, port, commands, timeout=10):
    try:
        # Establishing a telnet connection
        with telnetlib.Telnet(host, port, timeout) as tn:
            # Reading initial output (welcome message, etc.)
            print(read_until_prompt(tn, timeout=timeout).decode('ascii'))
            
            # Looping through each command
            for command in commands:
                # Sending the command
                tn.write(command.encode('ascii'))
                
                # Reading output until the prompt appears to ensure the command has been executed
                print(read_until_prompt(tn, timeout=timeout).decode('ascii'))
                
                # Small delay to ensure the router has time to process the command
                # This might be adjusted depending on the router's response time
                time.sleep(1)
    except Exception as e:
        print(f"An error occurred: {e}")

# Executing the function
telnet_execute_commands(HOST, PORT, commands, TIMEOUT)
