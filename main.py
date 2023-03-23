from utils.system import System
from utils.visage import Visage
from utils.applications import Chrome
import time

import warnings
warnings.filterwarnings("ignore")

config_file = "./config.json"

system = System(config_file)
visage = Visage(system.config["system"]["imageDir"], system.config["system"]["featuresFile"])
chrome = Chrome()

count = 0  # Initialize counter variable

while True:
    time.sleep(5)
    if visage.is_same_person() and chrome.locked:
        cmd = input(f"Welcome back {system.config['owner']['name']}. Do you want to unlock the chrome? (Y)/n")
        if cmd == "Y" or cmd == "":
            chrome.unlock()
            count = 0  # Reset counter if owner is detected
            
    elif not visage.is_same_person() and not chrome.locked:
        count += 1  # Increment counter if unauthorized user is detected
        if count >= 5:  # Lock if more than 5 attempts
            chrome.lock()
            count = 0  # Reset counter
