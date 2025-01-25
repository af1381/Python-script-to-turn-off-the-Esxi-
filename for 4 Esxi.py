from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl
import time

# Disable SSL verification (for simplicity in testing environments)
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)  # Use TLS 1.2
ssl_context.verify_mode = ssl.CERT_NONE

# ESXi server details
esxi_servers = [
    {"host": "192.168.137.141", "user": "root", "password": "password1"},
    {"host": "192.168.137.144", "user": "root", "password": "password2"},
    {"host": "192.168.137.145", "user": "root", "password": "password3"},
    {"host": "192.168.137.146", "user": "root", "password": "password4"},
]

def shutdown_esxi(host, user, password):
    try:
        # Connect to the ESXi server
        print(f"Connecting to ESXi server: {host}")
        connection = SmartConnect(host=host, user=user, pwd=password, sslContext=ssl_context)

        # Retrieve the Host System object
        content = connection.RetrieveContent()
        host_system = content.rootFolder.childEntity[0].hostFolder.childEntity[0].host[0]

        print(f"Shutting down ESXi server: {host}")
        
        # Check the server's status before shutting it down
        if host_system.runtime.powerState == vim.HostSystem.PowerState.poweredOn:
            # Perform a soft shutdown with force=True
            task = host_system.ShutdownHost_Task(force=True)  # Forced shutdown
            while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
                print(f"Checking the shutdown status of server {host}...")
                time.sleep(5)  # 5-second delay for status check

            task_info = task.info
            if task_info.state == vim.TaskInfo.State.success:
                print(f"Server {host} successfully shut down.")
            else:
                print(f"Server {host} failed to shut down. Status: {task_info.state}")
        else:
            print(f"Server {host} is already powered off.")

        Disconnect(connection)
    except Exception as e:
        print(f"Failed to shut down server {host}: {e}")

# Shut down all servers
for server in esxi_servers:
    shutdown_esxi(server["host"], server["user"], server["password"])
