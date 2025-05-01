from ppadb.client import Client as AdbClient
import os
from PIL import Image

class AndroidDeviceConnector:
    def __init__(self, host="127.0.0.1", port=5037):
        self.client = AdbClient(host=host, port=port)
        self.device = None
        self.connected = False
        self.screenshot_count = 0

    def list_devices(self):
        """List all connected Android devices"""
        try:
            devices = self.client.devices()
            return [device.serial for device in devices]
        except Exception as e:
            print(f"Error listing devices: {e}")
            return []

    def connect_device(self, device_serial=None):
        """Connect to an Android device"""
        try:
            if device_serial:
                self.device = self.client.device(device_serial)
            else:
                devices = self.client.devices()
                if not devices:
                    print("No devices found")
                    return False
                self.device = devices[0]
            
            self.connected = True
            print(f"Connected to device: {self.device.serial}")
            return True
        except Exception as e:
            print(f"Error connecting to device: {e}")
            return False

    def get_device_info(self):
        """Get basic information about the connected device"""
        if not self.connected:
            print("No device connected")
            return None

        try:
            # Get device model
            model = self.device.shell('getprop ro.product.model').strip()
            
            # Get Android version
            android_version = self.device.shell('getprop ro.build.version.release').strip()
            
            return {
                'model': model,
                'android_version': android_version,
                'serial': self.device.serial
            }
        except Exception as e:
            print(f"Error getting device info: {e}")
            return None

    def execute_command(self, command):
        """Execute a shell command on the device"""
        if not self.connected:
            print("No device connected")
            return None

        try:
            return self.device.shell(command)
        except Exception as e:
            print(f"Error executing command: {e}")
            return None

    def take_screenshot(self):
        """Take a screenshot and return the image data."""
        if not self.connected:
            print("No device connected")
            return None

        try:
            result = self.device.screencap()
            print("Screenshot taken successfully")
            return result
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return None

    def push_file(self, local_path, remote_path):
        """Push a file to the device"""
        if not self.connected:
            print("No device connected")
            return False

        try:
            self.device.push(local_path, remote_path)
            print(f"File pushed to {remote_path}")
            return True
        except Exception as e:
            print(f"Error pushing file: {e}")
            return False

    def pull_file(self, remote_path, local_path):
        """Pull a file from the device"""
        if not self.connected:
            print("No device connected")
            return False

        try:
            self.device.pull(remote_path, local_path)
            print(f"File pulled to {local_path}")
            return True
        except Exception as e:
            print(f"Error pulling file: {e}")
            return False

def main():
    connector = AndroidDeviceConnector()
    
    # List available devices
    devices = connector.list_devices()
    if not devices:
        print("No devices found. Please connect an Android device and try again.")
        return

    print("Available devices:")
    for i, device in enumerate(devices, 1):
        print(f"{i}. {device}")

    # Connect to the first available device
    if connector.connect_device():
        device_info = connector.get_device_info()
        if device_info:
            print("\nDevice Information:")
            print(f"Model: {device_info['model']}")
            print(f"Android Version: {device_info['android_version']}")
            print(f"Serial Number: {device_info['serial']}")
            
            # Example: List files in root directory
            print("\nRoot directory contents:")
            print(connector.execute_command('ls /'))
            
            # Example: Take a screenshot
            connector.take_screenshot()
    else:
        print("Failed to connect to device")

if __name__ == "__main__":
    main() 