#!/bin/bash

# Function to check if wf-recorder is running
function check_wf_recorder_status {
    if pgrep -x "wf-recorder" > /dev/null; then
        echo "Recording..."
    else
        echo "Record"
    fi
}

# Initial status
status=$(check_wf_recorder_status)
echo "$status"

# Monitor DBus signals for process start/stop
dbus-monitor  "type='signal',interface='org.freedesktop.systemd1.Manager',member='JobRemoved'" |
while read -r line; do
    if echo "$line" | grep -q "JobRemoved"; then
        new_status=$(check_wf_recorder_status)
        if [ "$status" != "$new_status" ]; then
            status=$new_status
            echo "$status"
        fi
    fi
done
