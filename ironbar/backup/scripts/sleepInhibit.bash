#!/bin/bash

SERVICE_NAME="wayland-idle-inhibitor.service"
DBUS_PATH="/org/freedesktop/systemd1/unit/wayland_2didle_2dinhibitor_2eservice"

# Function to get and output the current status of the service
function output_status {
    STATUS=$(systemctl --user is-active "$SERVICE_NAME")
    if [[ "$STATUS" == "active" ]]; then
        echo "eye.svg"
    else
        echo "eye-closed.svg"
    fi
}

# Output initial status
output_status

# Monitor DBus signals for the specified service
dbus-monitor "type='signal',sender='org.freedesktop.systemd1',path='$DBUS_PATH',interface='org.freedesktop.DBus.Properties',member='PropertiesChanged'" |
while read -r line; do
    if echo "$line" | grep -q "ActiveState"; then
        output_status
    fi
done
