#!/usr/bin/env python3

import dbus
import dbus.mainloop.glib
from gi.repository import GLib
import signal
import sys
import subprocess

class BatteryListener:
    def __init__(self):
        self.battery_percentage = "Unknown"
        self.on_battery = False

    def print_percentage(self):
        print(self.battery_percentage)
        sys.stdout.flush()

    def check_and_notify(self, percentage):
        if self.on_battery:
            if percentage <= 15 and percentage > 5:
                subprocess.run(["notify-send", "Warning", "Battery low! System will hibernate soon."])
            elif percentage <= 5:
                subprocess.run(["notify-send", "Critical", "Battery critically low! System hibernating..."])
                subprocess.run(["systemctl", "hibernate"])

    def on_properties_changed(self, interface, changed_properties, invalidated_properties):
        if 'Percentage' in changed_properties:
            percentage = changed_properties['Percentage']
            self.battery_percentage = f"{percentage:.0f}%"
            self.print_percentage()
            self.check_and_notify(percentage)
        if 'State' in changed_properties:
            state = changed_properties['State']
            # State 1 is charging, 2 is discharging, 4 is fully charged, 5 is pending discharge
            self.on_battery = state == 2 or state == 5

    def main(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SystemBus()

        try:
            upower = self.bus.get_object("org.freedesktop.UPower", "/org/freedesktop/UPower/devices/battery_BAT1")
            iface = dbus.Interface(upower, 'org.freedesktop.DBus.Properties')
            iface.connect_to_signal('PropertiesChanged', self.on_properties_changed)

            # Initial state
            props = iface.GetAll("org.freedesktop.UPower.Device")
            if 'Percentage' in props:
                self.battery_percentage = f"{props['Percentage']:.0f}%"
                self.print_percentage()
                self.check_and_notify(props['Percentage'])
            if 'State' in props:
                state = props['State']
                self.on_battery = state == 2 or state == 5

        except dbus.DBusException as e:
            print(f"Failed to initialize: {e}")
            self.battery_percentage = "Unknown"
            self.print_percentage()

        loop = GLib.MainLoop()
        
        def signal_handler(sig, frame):
            loop.quit()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        loop.run()

if __name__ == '__main__':
    listener = BatteryListener()
    listener.main()
