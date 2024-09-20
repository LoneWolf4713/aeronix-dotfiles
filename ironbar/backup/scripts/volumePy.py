#!/usr/bin/env python3

import subprocess
import re
import sys
import signal

class VolumeListener:
    def __init__(self):
        self.volume_level = None
        self.active_sink = self.get_active_sink()

    def get_active_sink(self):
        """Get the currently active sink (audio device)."""
        try:
            output = subprocess.check_output(["pactl", "get-default-sink"]).decode().strip()
            return output
        except Exception as e:
            print(f"Error getting active sink: {e}")
            return None

    def get_current_volume(self):
        """Get the volume level of the active sink."""
        try:
            if self.active_sink:
                output = subprocess.check_output(["pactl", "list", "sinks"]).decode()
                # Look for the section that corresponds to the active sink
                sink_section = re.search(rf'Sink #([0-9]+)[\s\S]*?Name: {re.escape(self.active_sink)}[\s\S]*?Volume:.*?(\d+)%', output)
                if sink_section:
                    return sink_section.group(2)
            return None
        except Exception as e:
            print(f"Error reading volume: {e}")
            return None

    def print_volume(self, volume):
        """Output the current volume level."""
        print(volume)
        sys.stdout.flush()

    def subscribe_to_volume_changes(self):
        """Subscribe to PulseAudio volume changes."""
        process = subprocess.Popen(["pactl", "subscribe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process

    def main(self):
        # Initial volume retrieval
        self.active_sink = self.get_active_sink()
        initial_volume = self.get_current_volume()
        if initial_volume is not None:
            self.volume_level = initial_volume
            self.print_volume(self.volume_level)

        process = self.subscribe_to_volume_changes()

        for line in iter(process.stdout.readline, b''):
            line = line.decode()
            if "sink" in line.lower():
                new_active_sink = self.get_active_sink()
                if new_active_sink != self.active_sink:
                    self.active_sink = new_active_sink

                new_volume = self.get_current_volume()
                if new_volume is not None and new_volume != self.volume_level:
                    self.volume_level = new_volume
                    self.print_volume(self.volume_level)

        process.stdout.close()
        process.wait()

        # Handle signals for a clean exit
        def signal_handler(sig, frame):
            process.terminate()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    listener = VolumeListener()
    listener.main()

