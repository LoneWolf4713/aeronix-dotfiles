#!/usr/bin/env bash

# Function to print the active network connection name
print_active_connection() {
    local connection_name=$(nmcli -t -f NAME,DEVICE connection show --active | grep -v ":lo" | awk -F: '{print $1}')
    if [ -n "$connection_name" ]; then
        echo "$connection_name"
    else
        echo "No connection"
    fi
}

# Print the initial state
print_active_connection

# Monitor network connection changes
nmcli monitor | while read -r line; do
    print_active_connection
done
