#!/usr/bin/env python3

import os
import sys
import pyinotify
import signal

class BrightnessListener:
    def __init__(self):
        self.brightness_path = "/sys/class/backlight/intel_backlight/brightness"
        self.max_brightness_path = "/sys/class/backlight/intel_backlight/max_brightness"
        self.brightness_level = None

    def get_brightness_percentage(self):
        try:
            with open(self.brightness_path, 'r') as f:
                brightness = int(f.read().strip())
            with open(self.max_brightness_path, 'r') as f:
                max_brightness = int(f.read().strip())
            return int((brightness / max_brightness) * 100)
        except Exception as e:
            print(f"Error reading brightness: {e}")
            return None

    def print_brightness(self):
        brightness_percentage = self.get_brightness_percentage()
        if brightness_percentage is not None:
            print(brightness_percentage)
            sys.stdout.flush()

    def process_IN_MODIFY(self, event):
        self.print_brightness()

    def monitor_brightness_changes(self):
        wm = pyinotify.WatchManager()
        notifier = pyinotify.Notifier(wm, self.process_IN_MODIFY)
        wm.add_watch(self.brightness_path, pyinotify.IN_MODIFY)

        self.print_brightness()  # Print the initial brightness level

        notifier.loop()

    def main(self):
        def signal_handler(sig, frame):
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        self.monitor_brightness_changes()

if __name__ == '__main__':
    listener = BrightnessListener()
    listener.main()

