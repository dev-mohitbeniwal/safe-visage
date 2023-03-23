from os import path, remove, makedirs
import json
import os
from datetime import datetime
import time
import warnings

with warnings.catch_warnings():
    warnings.filterwarnings("ignore")
    import cv2


class System:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = None
        self.minVideoLength = 10
        self.configure()
        self.save_config()

    def configure(self):
        # If config file doesn't exist, create the file
        if not path.isfile(self.config_file):
            with open(self.config_file, "w") as fp:
                config = self.getEmptyConfig()
                json.dump(config, fp)

        # Load and validate config
        try:
            with open(self.config_file, 'r') as fp:
                config = json.load(fp)
                check_or_create_dir(config["system"]["dataDir"])
                check_or_create_dir(config["system"]["imageDir"])

                if not config["owner"]["name"]:
                    config["owner"]["name"] = input("Please enter your name: ")

        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Error loading configuration: {e}")
            remove(self.config_file)
            self.configure()

        self.config = config

        # Capture reference images if necessary
        if not self.is_reference_images_available():
            self.capture_images(self.minVideoLength, config["system"]["imageDir"])

    def save_config(self):
        with open(self.config_file, 'w') as fp:
            json.dump(self.config, fp, indent=4)

    def is_reference_images_available(self):
        files = os.listdir(self.config["system"]["imageDir"])
        count = len([file for file in files if file.endswith(".png")])
        return count > 200

    def getEmptyConfig(self):
        return {
            "owner": {
                "name": "",
                "images": []
            },
            "system": {
                "dataDir": "./data",
                "featuresFile": "./data/features.npy",
                "imageDir": "./data/imageDir"
            }
        }
    
    def capture_images(self, video_length, save_folder):
        """
        Record a video of the specified length and save each frame as a PNG file in the specified folder.

        Args:
            video_length (int): The length of the video to record, in seconds.
            save_folder (str): The folder path to save the recorded frames to.

        Returns:
            None
        """

        input("""
        Visage need to record a small video to capture your facial features. 
        It will be a {} second video. Please try to capture your face from all angels
        especially the way you work on your laptop. It would be great if you can capture 
        your face from different distance to the camera.

        A good practice is to look at all the 8 cornors of the laptop (4 on display, 4 on the keyboard).
        Please make sure you have good lighting.

        Press enter when you are ready...
        """.format(video_length))

        images = list() 

        # Create save folder if it doesn't exist
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        # Set up video capture
        video_width = 640
        video_height = 480
        fps = 30
        capture = cv2.VideoCapture(0)
        time.sleep(2)

        # Record the video
        start_time = cv2.getTickCount()
        frame_count = 0
        while (cv2.getTickCount() - start_time) / cv2.getTickFrequency() < video_length:
            ret, frame = capture.read()
            if ret:
                frame = cv2.resize(frame, (video_width, video_height))
                save_path = os.path.join(save_folder, f"frame_{frame_count:04d}.png")
                images.append(save_path)
                cv2.imwrite(save_path, frame)
                frame_count += 1
            else:
                print(f"Frame {frame_count}: Error capturing frame")

        # Release video capture
        capture.release()

        # Print output
        print(f"Recorded {frame_count} frames to {save_folder}")
        return images

    

def get_timestamp():
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    return timestamp

def check_or_create_dir(dirPath):
    if not os.path.isdir(dirPath):
        os.mkdir(dirPath)