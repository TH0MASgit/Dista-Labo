#!/bin/bash
# This script can setup a useful VNC-based environment for a headless system


# First, let's enable Vino (Ubuntu's built-in VNC server for screensharing):
# https://www.answertopia.com/ubuntu/ubuntu-remote-desktop-access-with-vino/
sudo apt install vino

# Register the VNC server to start each time you log in
mkdir -p ~/.config/autostart
cp /usr/share/applications/vino-server.desktop ~/.config/autostart

# Configure the VNC server
gsettings set org.gnome.Vino prompt-enabled false
gsettings set org.gnome.Vino require-encryption false

# Set a password to access the VNC server (TODO: choose a better password...)
gsettings set org.gnome.Vino authentication-methods "['vnc']"
gsettings set org.gnome.Vino vnc-password $(echo -n '12345678' | base64)

# Only allow connections from the loopback interface
gsettings set org.gnome.Vino network-interface 'lo'


# NB: The VNC server is only available after you have logged in to Jetson locally.
# If you wish VNC to be available automatically, use the system settings application
# to enable automatic login.

# Also, the desktop resolution is typically determined by the capabilities of
# the display that is attached to Jetson. If no display is attached, Vino will
# refuse connections. To force a default resolution even with no monitor, edit
# /etc/X11/xorg.conf and append the following lines:

# Section "Screen"
#    Identifier    "Default Screen"
#    Monitor       "Configured Monitor"
#    Device        "Tegra0"
#    SubSection "Display"
#        Depth    24
#        Virtual 1280 720 # Modify the resolution by editing these values
#    EndSubSection
# EndSection


# Now let's setup a lightweight VNC server for headless access:
if sudo apt install tigervnc-standalone-server ; then
    cd "$(dirname "$0")/config"
    cp -ri .vnc .vncrc ~/
    
    # Once installed, you can start the vncserver over ssh using `vncserver :1` 
    # (with an optional -geometry 1920x1080 argument to set a specific resolution)
    # Stop the server with vncserver -kill :1 (assuming you started it on display 1)
    # View the active servers with vcnserver -list
fi

