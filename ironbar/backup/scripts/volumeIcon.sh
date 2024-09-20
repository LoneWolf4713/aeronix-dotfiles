#!/bin/bash

VOLUME_ICON_0="volume-3.svg"
VOLUME_ICON_1="volume-2.svg"
VOLUME_ICON_2="volume.svg"

get_active_sink() {
    pactl get-default-sink
}

get_current_volume() {
    local sink_name
    sink_name=$(get_active_sink)
    pactl list sinks | awk -v sink="$sink_name" '
    $1 == "Name:" && $2 == sink { in_sink=1 }
    in_sink && $1 == "Volume:" { sub(/%/, "", $5); print $5; exit }
    in_sink && /^$/ { in_sink=0 }'
}

print_volume_icon() {
    local volume=$1
    if [ "$volume" -eq 0 ]; then
        echo "$VOLUME_ICON_0"
    elif [ "$volume" -le 50 ]; then
        echo "$VOLUME_ICON_1"
    else
        echo "$VOLUME_ICON_2"
    fi
}

subscribe_to_volume_changes() {
    pactl subscribe | while read -r line; do
        if echo "$line" | grep -i "sink" > /dev/null; then
            local active_sink new_volume
            active_sink=$(get_active_sink)
            new_volume=$(get_current_volume)
            if [ "$new_volume" != "$volume_level" ]; then
                volume_level=$new_volume
                print_volume_icon "$volume_level"
            fi
        fi
    done
}

main() {
    # Get initial volume level and print the icon
    volume_level=$(get_current_volume)
    print_volume_icon "$volume_level"

    # Listen for volume changes via pactl
    subscribe_to_volume_changes
}

# Run the main function
main

