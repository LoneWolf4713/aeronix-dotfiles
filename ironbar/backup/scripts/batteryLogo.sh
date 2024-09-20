#!/bin/bash

get_battery_status() {
    # Get the battery percentage
    battery_percentage=$(upower -i /org/freedesktop/UPower/devices/battery_BAT1 | grep -E "percentage" | awk '{print $2}' | sed 's/%//')
    
    # Get the charging state
    charging_state=$(upower -i /org/freedesktop/UPower/devices/battery_BAT1 | grep -E "state" | awk '{print $2}')

    # If battery is charging
    if [[ "$charging_state" == "charging" ]]; then
        if [[ "$battery_percentage" -eq 100 ]]; then
            echo "batteryfull.svg"
        else
            echo "batteryCharging.svg"
        fi
    else
        # Not charging
        if [[ "$battery_percentage" -eq 100 ]]; then
            echo "batteryfull.svg"
        elif [[ "$battery_percentage" -ge 0 && "$battery_percentage" -lt 25 ]]; then
            echo "battery-1.svg"
        elif [[ "$battery_percentage" -ge 25 && "$battery_percentage" -lt 50 ]]; then
            echo "battery-2.svg"
        elif [[ "$battery_percentage" -ge 50 && "$battery_percentage" -lt 75 ]]; then
            echo "battery-3.svg"
        elif [[ "$battery_percentage" -ge 75 && "$battery_percentage" -lt 100 ]]; then
            echo "battery-4.svg"
        fi
    fi
}

# Listen for changes in battery status using dbus-monitor
dbus-monitor --system "type='signal',interface='org.freedesktop.DBus.Properties',member='PropertiesChanged',path='/org/freedesktop/UPower/devices/battery_BAT1'" |
while read -r line; do
    # Call the function to get and output the battery status each time there's a change
    get_battery_status
done

