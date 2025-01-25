from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl

# Disable SSL verification (for simplicity in testing environments)
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
ssl_context.verify_mode = ssl.CERT_NONE

# ESXi server details
esxi_servers = [
    {"host": "ip-Esxi", "user": "root", "password": "Your-password"},
    {"host": "ip-Esxi", "user": "root", "password": "Your-password"},
]

def shutdown_vms(host, user, password):
    try:
        # Connect to the ESXi server
        print(f"Connecting to ESXi server: {host}")
        connection = SmartConnect(host=host, user=user, pwd=password, sslContext=ssl_context)

        # Retrieve the content and list all VMs
        content = connection.RetrieveContent()
        vm_list = content.rootFolder.childEntity[0].vmFolder.childEntity

        for vm in vm_list:
            if isinstance(vm, vim.VirtualMachine):
                print(f"Checking VM: {vm.name}")
                # Check if the VM is powered on
                if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
                    print(f"Shutting down VM: {vm.name}")
                    try:
                        vm.ShutdownGuest()  # Gracefully shutdown the VM
                    except Exception as e:
                        print(f"Failed to gracefully shut down {vm.name}, attempting hard power off: {e}")
                        vm.PowerOffVM_Task()  # Forcefully power off the VM
                else:
                    print(f"VM {vm.name} is already powered off.")

        Disconnect(connection)
        print(f"All VMs on {host} have been processed.")
    except Exception as e:
        print(f"Failed to process VMs on server {host}: {e}")

# Shut down VMs on all ESXi servers
for server in esxi_servers:
    shutdown_vms(server["host"], server["user"], server["password"])
