import logging
from hinge_automator import HingeAutomator
import os
import time
import random
from dotenv import load_dotenv
import argparse
from PIL import Image
from io import BytesIO

# Load environment variables from .env file
load_dotenv()
openai_api_key = os.environ["OPENAI_API_KEY"]

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def chat_mode(automator):
    """Handle chat mode - analyze chat and suggest replies"""
    print("\nChat mode activated. Navigate to the chat you want to reply to.")
    print("Press Ctrl+C to exit chat mode.")
    
    try:
        while True:
            input("\nPress Enter when you're ready to analyze the chat and get reply suggestions...")
            
            # Take screenshot
            screenshot_data = automator.take_screenshot()
            if not screenshot_data:
                print("Failed to take screenshot")
                continue
            
            # Convert bytearray to PIL Image
            screenshot = Image.open(BytesIO(screenshot_data))
            
            # Analyze chat and get reply suggestions
            suggested_replies = automator.analyze_chat(screenshot)
            if not suggested_replies:
                print("Failed to analyze chat")
                continue
            
            print("\nSuggested replies:")
            for i, reply in enumerate(suggested_replies, 1):
                print(f"\n{i}. {reply}")
            
            # Ask user which reply they want to send
            while True:
                try:
                    choice = input("\nEnter the number of the reply you want to send (1-5), or 'n' to skip: ")
                    if choice.lower() == 'n':
                        break
                    
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(suggested_replies):
                        selected_reply = suggested_replies[choice_num - 1]
                        if automator.send_chat_message(selected_reply):
                            print("Message sent successfully!")
                        else:
                            print("Failed to send message")
                        break
                    else:
                        print("Please enter a number between 1 and 5")
                except ValueError:
                    print("Please enter a valid number or 'n' to skip")
            
            time.sleep(1)  # Small delay before next iteration
    
    except KeyboardInterrupt:
        print("\nExiting chat mode...")

def swipe_mode(automator):
    """Handle swipe mode - like and comment on profiles"""
    try:
        # Perform likes with comments
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

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Hinge Automation Tool')
    parser.add_argument('mode', choices=['swipe', 'chat'], help='Mode to run the tool in')
    args = parser.parse_args()
    
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
    
    # Run in selected mode
    if args.mode == 'chat':
        chat_mode(automator)
    else:
        swipe_mode(automator)

if __name__ == "__main__":
    main()
