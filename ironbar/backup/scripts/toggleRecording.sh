#!/bin/bash

# Function to check if wf-recorder is running
function is_wf_recorder_running {
    pgrep -x "wf-recorder" > /dev/null
}

# Function to start wf-recorder
function start_wf_recorder {
    timestamp=$(date +"%Y%m%d%H%M%S")
    wf-recorder -f "/home/prtyksh/Videos/n${timestamp}.mp4" &
    echo "wf-recorder started with file ${timestamp}.mp4"
}

# Function to stop wf-recorder
function stop_wf_recorder {
    pkill -SIGTERM -x "wf-recorder"
    echo "wf-recorder stopped"
}

# Main logic
if is_wf_recorder_running; then
    stop_wf_recorder
else
    start_wf_recorder
fi
