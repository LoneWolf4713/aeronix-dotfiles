#!/bin/bash

# Function to get the currently playing song and artist from Spotify
get_current_song_and_artist() {
    metadata=$(dbus-send --print-reply \
        --dest=org.mpris.MediaPlayer2.spotify \
        /org/mpris/MediaPlayer2 \
        org.freedesktop.DBus.Properties.Get \
        string:"org.mpris.MediaPlayer2.Player" string:"Metadata")

    # Extract song title
    song=$(echo "$metadata" | awk -F '"' '/title/{getline; print $2}')

    # Extract artist name
    artist=$(echo "$metadata" | awk -F '"' '/artist/{getline; getline; print $2}')

    # If artist is not found, set to "Unknown Artist"
    if [ -z "$artist" ]; then
        artist="Unknown Artist"
    fi

    echo "$song - $artist"
}

# Initial song and artist name
current_song_and_artist=$(get_current_song_and_artist)
echo "$current_song_and_artist"

# Monitor DBus signals for changes in the Spotify player
dbus-monitor "type='signal',interface='org.freedesktop.DBus.Properties',member='PropertiesChanged',path='/org/mpris/MediaPlayer2'" |
while read -r line; do
    if echo "$line" | grep -q "org.mpris.MediaPlayer2.Player"; then
        new_song_and_artist=$(get_current_song_and_artist)
        if [ "$new_song_and_artist" != "$current_song_and_artist" ]; then
            current_song_and_artist=$new_song_and_artist
            echo "$current_song_and_artist"
        fi
    fi
done

