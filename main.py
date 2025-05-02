import logging
from hinge_automator import HingeAutomator
import os
import time
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
openai_api_key = os.environ["OPENAI_API_KEY"]

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():    
    # Create an instance of HingeAutomator
    automator = HingeAutomator(openai_api_key=openai_api_key)
    
    # List available devices
    devices = automator.list_devices()
    if not devices:
        print("No devices found. Please connect an Android device and try again.")
        return
    
    print("Available devices:")
    for i, device in enumerate(devices, 1):
        print(f"{i}. {device}")
    
    # Connect to the first available device
    if not automator.connect_device():
        print("Failed to connect to device")
        return
    
    # Check if Hinge is installed
    if not automator.is_hinge_installed():
        print("Hinge is not installed on the device")
        return
    
    # Launch Hinge
    if not automator.launch_hinge():
        print("Failed to launch Hinge")
        return
    
    print("Hinge launched successfully")
    
    # Example: Perform some likes with comments
    try:
        # Perform 5 likes with comments
        for i in range(100):
            print(f"\nProcessing profile {i+1}...")
            
            # Check if we're still in Hinge app
            if not automator.is_in_hinge_app():
                print("No longer in Hinge app. Exiting...")
                break
            
            # Like and comment using GPT-4 Vision
            if automator.like_and_comment():
                print("Successfully liked and commented on profile")
            else:
                print("Failed to like and comment on profile")
            
            # Wait a bit before the next profile
            time.sleep(random.uniform(3, 5))
    
    except KeyboardInterrupt:
        print("\nStopping automation...")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
