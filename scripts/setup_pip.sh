#!/bin/bash
# This script will install the required python modules for dista;
# It can be called at any time to update the dependencies to their latest version

# Interface
pip3 install -U pyopengl webcolors

# Cameras (other than the Zeds and Nerian)
pip3 install -U nanocamera

# Streaming
pip3 install -U pyzmq vidgear

# Databases
pip3 install -U mysql-connector-python mariadb

# Visualizations
pip3 install -U pandas plotly matplotlib

