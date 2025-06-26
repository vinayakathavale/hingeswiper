from android_connector import AndroidDeviceConnector
import time
from typing import Optional, Dict
import logging
import base64
from openai import OpenAI
import os
from PIL import Image
from shape_matcher import find_shape_coordinates
import numpy as np
from io import BytesIO
import re

class HingeAutomator(AndroidDeviceConnector):
    HINGE_PACKAGE = "co.hinge.app"
    
    def __init__(self, host="127.0.0.1", port=5037, openai_api_key=None):
        super().__init__(host, port)
        self.logger = logging.getLogger(__name__)
        self.screen_width = 1080
        self.screen_height = 2400
        # self._get_screen_dimensions()
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=openai_api_key or os.getenv("OPENAI_API_KEY"))
        if not self.openai_client.api_key:
            self.logger.warning("OpenAI API key not provided. GPT-4 Vision features will not work.")
    
    def is_hinge_installed(self) -> bool:
        """Check if Hinge is installed on the device"""
        if not self.connected:
            return False
        
        try:
            output = self.execute_command(f"pm list packages {self.HINGE_PACKAGE}")
            return self.HINGE_PACKAGE in output
        except Exception as e:
            self.logger.error(f"Error checking Hinge installation: {e}")
            return False
    
    def launch_hinge(self) -> bool:
        """Launch the Hinge app"""
        if not self.connected:
            return False
        
        try:
            # Launch Hinge
            self.execute_command(f"monkey -p {self.HINGE_PACKAGE} 1")
            time.sleep(5)  # Wait for app to launch
            return True
        except Exception as e:
            self.logger.error(f"Error launching Hinge: {e}")
            return False
    
    def analyze_screenshot(self, screenshot) -> Optional[Dict]:
        """Analyze screenshot using shape matching to find the heart button and OpenAI Vision to analyze profile"""
        try:
            # Convert PIL Image to numpy array
            screenshot_np = np.array(screenshot)
            
            # Find heart button using shape matching
            heart_template_path = "data/crop_right.png"
            center = find_shape_coordinates(heart_template_path, screenshot_np)
            
            if not center:
                self.logger.warning("Heart button not found in screenshot")
                return None

            # Convert PIL Image to PNG bytes
            img_byte_arr = BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Use OpenAI Vision to analyze the profile
            base64_image = base64.b64encode(img_byte_arr).decode('utf-8')

            response = self.openai_client.chat.completions.create(
                model="gpt-4.1-mini",
                max_tokens=8,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyze this Hinge profile and suggest a short, personalized, and flirty message that would be memorable 
                                and out of the norm. Look for quirky or amusing details in their photos, prompts, and bio,
                                Make sure the message is memorable and unique, the recipient would be women in their mid-late 20s
                                Make sure you dont generate more than 20 characters. Do not use any punctuation other than ',', '.','?' """
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
            )

            suggested_comment = response.choices[0].message.content.strip()
            self.logger.info(f"Generated suggested comment: {suggested_comment}")
            
            return {
                "heart_button": {
                    "x": center[0],
                    "y": center[1]
                },
                "suggested_comment": suggested_comment
            }
                
        except Exception as e:
            self.logger.error(f"Error analyzing screenshot: {e}")
            return None
    
    def click_heart_button(self, coordinates: Dict[str, int], screenshot_path: str = "current_profile.png") -> bool:
        """Click the heart button at specified coordinates, scaling if needed"""
        if not self.connected:
            return False

        try:
            self.logger.info(f"Received coordinates: {coordinates}")
            x = coordinates.get("x")
            y = coordinates.get("y")
            if x is None or y is None:
                self.logger.error(f"Invalid coordinates for heart button: {coordinates}")
                return False

            if self.screen_width is None or self.screen_height is None:
                self.logger.error(f"Device screen dimensions not set: width={self.screen_width}, height={self.screen_height}")
                return False

            # Get screenshot size
            with Image.open(screenshot_path) as img:
                screenshot_width, screenshot_height = img.size

            self.logger.info(f"Device screen size: {self.screen_width}x{self.screen_height}")
            self.logger.info(f"Screenshot size: {screenshot_width}x{screenshot_height}")
            self.logger.info(f"Model coordinates: x={x}, y={y}")

            # Scale coordinates if screenshot size != device screen size
            if screenshot_width != self.screen_width or screenshot_height != self.screen_height:
                x = int(x * self.screen_width / screenshot_width)
                y = int(y * self.screen_height / screenshot_height)
                # Ensure coordinates stay within screen bounds
                x = max(0, min(x, self.screen_width - 1))
                y = max(0, min(y, self.screen_height - 1))
                self.logger.info(f"Scaled coordinates: x={x}, y={y}")

            # Execute the tap command
            tap_command = f"input tap {x} {y}"
            self.logger.info(f"Executing tap command: {tap_command}")
            result = self.execute_command(tap_command)
            self.logger.info(f"Tap command result: {result}")
            
            time.sleep(2)  # Wait for the like animation
            return True
        except Exception as e:
            self.logger.error(f"Error clicking heart button: {e}")
            return False
    
    def post_comment(self, comment: str) -> bool:
        """Post a comment after liking"""
        if not self.connected:
            return False
        try:
            # Click on the text input box (approximate position)
            self.execute_command(f"input tap 540 1500")
            time.sleep(1)  # Wait for keyboard to appear
            
            # Type the comment
            comment = comment.replace(" ", "%s")
            comment = comment.replace("'", "")
            comment = comment.replace("’", "")
            comment = comment.replace("!", "")
            comment = comment.replace("-", "%s")
            print(comment, 'commentttt')
            self.execute_command(f'input text "{comment}"')
            time.sleep(3)
            
            # press back
            self.execute_command(f"input tap 870 2300")

            time.sleep(1)

            # press submit
            self.execute_command(f"input tap 540 1700")

            time.sleep(2)
            return True
        except Exception as e:
            self.logger.error(f"Error posting comment: {e}")
            return False
    
    def like_and_comment(self) -> bool:
        """Like a profile and post a comment using GPT-4 Vision"""
        if not self.connected:
            self.logger.error("Not connected to device")
            return False
            
        try:
            # Take screenshot
            screenshot_data = self.take_screenshot()
            if not screenshot_data:
                self.logger.error("Failed to take screenshot")
                return False
            
            # Convert bytearray to PIL Image
            screenshot = Image.open(BytesIO(screenshot_data))
            screenshot.save("data/1/screenshot.png")
            
            self.logger.info("Successfully took screenshot")
            
            # Analyze screenshot
            analysis = self.analyze_screenshot(screenshot)
            if not analysis:
                self.logger.error("Failed to analyze screenshot")
                return False
            self.logger.info("Successfully analyzed screenshot")
            
            # Click heart button
            heart_button = analysis.get("heart_button", {})
            if not heart_button:
                self.logger.error("No heart button coordinates found in analysis")
                return False
                
            if not self.click_heart_button(heart_button, "data/1/screenshot.png"):
                self.logger.error("Failed to click heart button")
                return False
            self.logger.info("Successfully clicked heart button")
            
            # Post comment
            suggested_comment = analysis.get("suggested_comment", "")
            if not suggested_comment:
                self.logger.error("No suggested comment found in analysis")
                return False
                
            if not self.post_comment(suggested_comment):
                self.logger.error("Failed to post comment")
                return False
            self.logger.info("Successfully posted comment")
            
            return True
        except Exception as e:
            self.logger.error(f"Error in like_and_comment: {e}")
            return False
    
    def is_in_hinge_app(self) -> bool:
        """Check if we're currently in the Hinge app"""
        if not self.connected:
            return False
        
        try:
            # Get the current running app using dumpsys activity
            output = self.execute_command("dumpsys activity top | grep ACTIVITY")
            print(output, 'outputttt')
            
            # Split output into lines and get the last line
            lines = output.strip().split('\n')
            if not lines:
                return False
                
            last_line = lines[-1]
            print("Last line:", last_line)
            
            return self.HINGE_PACKAGE in last_line
        except Exception as e:
            self.logger.error(f"Error checking current app: {e}")
            return False

    def analyze_chat(self, screenshot) -> Optional[list[str]]:
        """Analyze chat screenshot and suggest 5 replies using GPT-4 Vision"""
        try:
            # Convert PIL Image to PNG bytes
            img_byte_arr = BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Use OpenAI Vision to analyze the chat
            base64_image = base64.b64encode(img_byte_arr).decode('utf-8')

            response = self.openai_client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyze this Hinge chat conversation and suggest 5 different natural, engaging replies. 
                                Each reply should be:
                                1. Contextually relevant to the conversation
                                2. Flirty but not overly sexual
                                3. Show personality and humor
                                4. Keep it concise (1-2 sentences max)
                                5. End with a question to keep the conversation going
                                
                                Format the response as a numbered list (1-5) with each reply on a new line.
                                Do not use any punctuation other than ',', '.', '?' """
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )

            # Split the response into individual replies
            suggested_replies = response.choices[0].message.content.strip().split('\n')
            # Clean up the replies (remove numbers and extra whitespace)
            suggested_replies = [reply.strip().lstrip('12345. ') for reply in suggested_replies if reply.strip()]
            
            self.logger.info(f"Generated {len(suggested_replies)} suggested replies")
            
            return suggested_replies[:5]  # Ensure we only return 5 replies
                
        except Exception as e:
            self.logger.error(f"Error analyzing chat: {e}")
            return None
