import json
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl

# Disable SSL verification
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
ssl_context.verify_mode = ssl.CERT_NONE

# Read server information from the config.json file
with open("config.json", "r") as config_file:
    esxi_servers = json.load(config_file)

def shutdown_vms(host, user, password):
    try:
        print(f"Connecting to ESXi server: {host}")
        connection = SmartConnect(host=host, user=user, pwd=password, sslContext=ssl_context)

        # Retrieve VMs and shut them down
        content = connection.RetrieveContent()
        vm_list = content.rootFolder.childEntity[0].vmFolder.childEntity

        for vm in vm_list:
            if isinstance(vm, vim.VirtualMachine):
                print(f"Checking virtual machine: {vm.name}")
                if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
                    try:
                        vm.ShutdownGuest()
                        print(f"Attempting graceful shutdown for {vm.name}")
                    except:
                        vm.PowerOffVM_Task()
                        print(f"Graceful shutdown failed; {vm.name} powered off forcefully.")
                else:
                    print(f"{vm.name} is already powered off.")
        
        Disconnect(connection)
    except Exception as e:
        print(f"Error on server {host}: {e}")

# Process all servers
for server in esxi_servers:
    shutdown_vms(server["host"], server["user"], server["password"])
