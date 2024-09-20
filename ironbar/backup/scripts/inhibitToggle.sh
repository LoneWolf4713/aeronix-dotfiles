#!/bin/bash

# Service name
SERVICE_NAME="wayland-idle-inhibitor.service"

# Function to check if the service is active
function is_service_active {
    systemctl --user is-active --quiet "$SERVICE_NAME"
}

# Function to start the service
function start_service {
    systemctl --user start "$SERVICE_NAME"
    echo "$SERVICE_NAME started"
}

# Function to stop the service
function stop_service {
    systemctl --user stop "$SERVICE_NAME"
    echo "$SERVICE_NAME stopped"
}

# Main logic
if is_service_active; then
    stop_service
else
    start_service
fi
