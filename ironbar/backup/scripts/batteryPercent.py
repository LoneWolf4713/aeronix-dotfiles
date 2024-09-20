#!/usr/bin/env python3

import dbus
import dbus.mainloop.glib
from gi.repository import GLib
import signal
import sys

class BatteryListener:
    def __init__(self):
        self.battery_percentage = "Unknown"

    def print_percentage(self):
        print(self.battery_percentage)
        sys.stdout.flush()

    def on_properties_changed(self, interface, changed_properties, invalidated_properties):
        if 'Percentage' in changed_properties:
            percentage = changed_properties['Percentage']
            self.battery_percentage = f"{percentage:.0f}%"
            self.print_percentage()

    def main(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        system_bus = dbus.SystemBus()

        try:
            upower = system_bus.get_object("org.freedesktop.UPower", "/org/freedesktop/UPower/devices/battery_BAT1")
            iface = dbus.Interface(upower, 'org.freedesktop.DBus.Properties')
            iface.connect_to_signal('PropertiesChanged', self.on_properties_changed)

            # Initial state
            props = iface.GetAll("org.freedesktop.UPower.Device")
            if 'Percentage' in props:
                self.battery_percentage = f"{props['Percentage']:.0f}%"
                self.print_percentage()

        except dbus.DBusException as e:
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