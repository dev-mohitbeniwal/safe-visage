import os
import platform
import shutil
import subprocess

class Chrome:
    def __init__(self):
        self.os_name = platform.system()
        self.chrome_data_path = self._get_chrome_data_path()
        self.locked_chrome_data_path = self._get_locked_chrome_data_path()
        self.status_file = self._get_status_file()
        self.locked = self._read_locked_status()

    def _get_chrome_data_path(self):
        if self.os_name == "Windows":
            user_profile = os.getenv("USERPROFILE")
            return os.path.join(user_profile, "AppData/Local/Google/Chrome/User Data")
        elif self.os_name == "Darwin":
            user_home = os.path.expanduser("~")
            return os.path.join(user_home, "Library/Application Support/Google/Chrome")
        elif self.os_name == "Linux":
            user_home = os.path.expanduser("~")
            return os.path.join(user_home, ".config/google-chrome")
        else:
            print("Unsupported operating system.")
            return None

    def _get_locked_chrome_data_path(self):
        if self.chrome_data_path:
            return f"{self.chrome_data_path}.locked"
        else:
            return None

    def _get_status_file(self):
        if self.os_name == "Windows":
            user_profile = os.getenv("USERPROFILE")
            return os.path.join(user_profile, "chrome_data_status.txt")
        elif self.os_name == "Darwin":
            user_home = os.path.expanduser("~")
            return os.path.join(user_home, "chrome_data_status.txt")
        elif self.os_name == "Linux":
            user_home = os.path.expanduser("~")
            return os.path.join(user_home, "chrome_data_status.txt")
        else:
            print("Unsupported operating system.")
            return None

    def _read_locked_status(self):
        if os.path.exists(self.status_file):
            with open(self.status_file, 'r') as f:
                status = f.read().strip()
                if status == 'locked':
                    return True
                else:
                    return False
        else:
            return False

    def _write_locked_status(self, status):
        with open(self.status_file, 'w') as f:
            f.write(status)

    def lock(self):
        self.close_all_instances()
        self.lock_unlock_chrome_data('lock')
        self.locked = True
        self._write_locked_status('locked')

    def unlock(self):
        self.close_all_instances()
        self.lock_unlock_chrome_data('unlock')
        self.locked = False
        self._write_locked_status('unlocked')

    def lock_unlock_chrome_data(self, action):
        if not self.chrome_data_path or not self.locked_chrome_data_path:
            print("Cannot lock or unlock Chrome data due to an unsupported operating system.")
            return

        if action == "lock":
            if os.path.exists(self.chrome_data_path):
                if os.path.exists(self.locked_chrome_data_path):
                    print("Cannot lock Chrome data because a locked folder already exists.")
                else:
                    shutil.move(self.chrome_data_path, self.locked_chrome_data_path)
                    print("Chrome data is locked.")
            else:
                print("Chrome data is already locked or doesn't exist.")
        elif action == "unlock":
            if os.path.exists(self.locked_chrome_data_path):
                if os.path.exists(self.chrome_data_path):
                    shutil.rmtree(self.chrome_data_path)
                shutil.move(self.locked_chrome_data_path, self.chrome_data_path)
                print("Chrome data is unlocked.")
            else:
                print("Chrome data is already unlocked or doesn't exist.")
        else:
            print("Invalid action. Please use 'lock' or 'unlock'.")


    def close_all_instances(self):
        if self.os_name == "Windows":
            subprocess.call("taskkill /f /im chrome.exe", shell=True)
        elif self.os_name == "Darwin":
            subprocess.call('pgrep -x "Google Chrome" | xargs kill -9', shell=True)
        elif self.os_name == "Linux":
            subprocess.call('pgrep -x "Google Chrome" | xargs kill -9', shell=True)
        else:
            print("Unsupported operating system.")



