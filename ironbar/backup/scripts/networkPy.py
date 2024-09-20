#!/usr/bin/env python3

import dbus
import dbus.mainloop.glib
from gi.repository import GLib
import signal
import sys

class NetworkListener:
    def __init__(self):
        self.network_status = "wifi-xmark.svg"
        self.previous_status = None

    def print_status(self):
        print(self.network_status)
        sys.stdout.flush()

    def on_properties_changed(self, interface, changed_properties, invalidated_properties):
        if 'State' in changed_properties:
            state = changed_properties['State']
            new_status = self.map_state_to_status(state)
            if new_status != self.network_status and new_status != "wifi-xmark.svg":
                self.network_status = new_status
                self.print_status()
            elif new_status == "wifi-xmark.svg" and self.previous_status not in ["wifi.svg", "wifi-signal-none-solid.svg"]:
                self.network_status = new_status
                self.print_status()
            self.previous_status = self.network_status

    def map_state_to_status(self, state):
        states = {
            70: "wifi-signal-none-solid.svg",
            50: "wifi.svg",
            30: "wifi-warning.svg",
            20: "wifi.svg",  # Added another state for "wifi.svg"
            10: "wifi.svg"   # Added another state for "wifi.svg"
        }
        return states.get(state, "wifi-xmark.svg")

    def main(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        system_bus = dbus.SystemBus()

        try:
            network_manager = system_bus.get_object("org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager")
            iface = dbus.Interface(network_manager, 'org.freedesktop.DBus.Properties')
            iface.connect_to_signal('PropertiesChanged', self.on_properties_changed)

            # Initial state
            props = iface.GetAll("org.freedesktop.NetworkManager")
            if 'State' in props:
                self.network_status = self.map_state_to_status(props['State'])
                self.previous_status = self.network_status
                self.print_status()

        except dbus.DBusException as e:
            self.network_status = "wifi-xmark.svg"
            self.print_status()

        loop = GLib.MainLoop()
        
        def signal_handler(sig, frame):
            loop.quit()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        loop.run()

if __name__ == '__main__':
    listener = NetworkListener()
    listener.main()

