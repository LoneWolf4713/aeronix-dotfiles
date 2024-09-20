#!/usr/bin/env bash

# Function to print the active network interface name
print_active_interface() {
    local interface_name=$(nmcli -t -f DEVICE,STATE device status | grep ':connected' | grep -v '^lo:' | cut -d':' -f1)
    if [ -n "$interface_name" ]; then
        echo "$interface_name"
    else
        echo "No active interface"
    fi
}

# Print the initial state
print_active_interface

# Monitor network connection changes
nmcli monitor | while read -r line; do
    print_active_interface
done
