#!/bin/bash

get_connected_device() {
    # Get the list of all Bluetooth devices
    devices=$(bluetoothctl devices | awk '{print $2}')
    
    for device in $devices; do
        # Check if the device is connected
        connected=$(bluetoothctl info "$device" | grep "Connected: yes")
        if [ -n "$connected" ]; then
            # Get the name of the connected device
            name=$(bluetoothctl info "$device" | grep "Name:" | awk -F'Name: ' '{print $2}')
            echo "$name"
            return
        fi
    done
    
    # If no device is connected, return "Bluetooth"
    echo "Bluetooth"
}

print_connected_device() {
    connected_device=$(get_connected_device)
    echo "$connected_device"
}

# Initial output
print_connected_device

# Monitor Bluetooth connection changes
dbus-monitor --system "type='signal',interface='org.freedesktop.DBus.Properties',member='PropertiesChanged',path_namespace='/org/bluez'" 2>/dev/null |
while read -r line; do
    if [[ "$line" =~ "Connected" ]]; then
        print_connected_device
    fi
done
