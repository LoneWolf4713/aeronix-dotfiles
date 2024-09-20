#!/bin/bash

BRIGHTNESS_PATH="/sys/class/backlight/intel_backlight/brightness"
MAX_BRIGHTNESS_PATH="/sys/class/backlight/intel_backlight/max_brightness"

# Get current brightness percentage
get_brightness_percentage() {
    brightness=$(cat "$BRIGHTNESS_PATH")
    max_brightness=$(cat "$MAX_BRIGHTNESS_PATH")
    brightness_percentage=$(( 100 * brightness / max_brightness ))
    echo "$brightness_percentage"
}

# Output the correct brightness icon based on percentage
print_brightness_icon() {
    brightness_percentage=$(get_brightness_percentage)

    if [ "$brightness_percentage" -le 40 ]; then
        echo "brightness-auto.svg"
    elif [ "$brightness_percentage" -le 75 ]; then
        echo "brightness-half.svg"
    else
        echo "brightness-full.svg"
    fi
}

# Monitor brightness file changes using inotifywait
monitor_brightness_changes() {
    # Initial brightness state
    print_brightness_icon

    # Monitor changes to the brightness file
    while inotifywait -q -e modify "$BRIGHTNESS_PATH"; do
        print_brightness_icon
    done
}

# Run the brightness monitoring
monitor_brightness_changes

