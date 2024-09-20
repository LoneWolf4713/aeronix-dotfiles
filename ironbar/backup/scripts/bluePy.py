#!/usr/bin/env python3

import subprocess
import dbus
import dbus.mainloop.glib
from gi.repository import GLib
import signal
import sys

class BluetoothListener:
    def __init__(self):
        self.bluetooth_status = "bluetoothOff.png"
        self.service_status = "bluetoothDisabled.png"
        self.devices = []
        self.previous_status = None

    def print_status(self, status):
        if status != self.previous_status:
            print(status)
            sys.stdout.flush()
            self.previous_status = status

    def check_service_status(self):
        try:
            output = subprocess.check_output(["systemctl", "is-active", "bluetooth"]).decode().strip()
            if output == "active":
                self.service_status = "bluetoothEnabled.png"
            else:
                self.service_status = "bluetoothDisabled.png"
            self.print_status(self.service_status)
        except subprocess.CalledProcessError:
            self.service_status = "bluetoothDisabled.png"
            self.print_status(self.service_status)

    def get_initial_status(self):
        try:
            self.check_service_status()
            output = subprocess.check_output(["bluetoothctl", "show"]).decode()
            if "Powered: yes" in output:
                self.bluetooth_status = "bluetoothOn.png"
            else:
                self.bluetooth_status = "bluetoothOff.png"

            connected_devices = subprocess.check_output(["bluetoothctl", "devices", "Connected"]).decode()
            if connected_devices:
                self.bluetooth_status = "bluetoothConnected.png"
                self.devices = [line.split()[1] for line in connected_devices.split('\n') if line]

            self.print_status(self.bluetooth_status)
        except subprocess.CalledProcessError:
            self.bluetooth_status = "bluetoothOff.png"
            self.print_status(self.bluetooth_status)

    def properties_changed(self, interface, changed, invalidated, path):
        if 'Powered' in changed:
            if changed['Powered']:
                self.bluetooth_status = "bluetoothOn.png"
            else:
                self.bluetooth_status = "bluetoothOff.png"
                self.devices = []  # Clear devices list if Bluetooth is powered off
            self.print_status(self.bluetooth_status)

    def device_properties_changed(self, interface, changed, invalidated, path):
        if 'Connected' in changed:
            if changed['Connected']:
                self.bluetooth_status = "bluetoothConnected.png"
            else:
                device_path = path.split("/")[-1]
                if device_path in self.devices:
                    self.devices.remove(device_path)
                self.bluetooth_status = "bluetoothConnected.png" if self.devices else "bluetoothOn.png"
            self.print_status(self.bluetooth_status)

    def monitor_service_status(self):
        self.bus = dbus.SystemBus()
        systemd_manager = self.bus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
        systemd_interface = dbus.Interface(systemd_manager, 'org.freedesktop.systemd1.Manager')
        systemd_interface.connect_to_signal('UnitNew', self.on_unit_changed)
        systemd_interface.connect_to_signal('UnitRemoved', self.on_unit_changed)

    def on_unit_changed(self, *args, **kwargs):
        self.check_service_status()

    def main(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SystemBus()

        self.previous_status = None

        self.get_initial_status()

        adapter = self.bus.get_object("org.bluez", "/org/bluez/hci0")
        adapter_interface = dbus.Interface(adapter, "org.freedesktop.DBus.Properties")
        adapter_interface.connect_to_signal("PropertiesChanged", self.properties_changed, path_keyword='path')

        self.bus.add_signal_receiver(self.device_properties_changed,
                                     bus_name="org.bluez",
                                     signal_name="PropertiesChanged",
                                     dbus_interface="org.freedesktop.DBus.Properties",
                                     path_keyword='path')

        self.monitor_service_status()

        loop = GLib.MainLoop()

        def signal_handler(sig, frame):
            loop.quit()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        loop.run()

if __name__ == '__main__':
    listener = BluetoothListener()
    listener.main()
