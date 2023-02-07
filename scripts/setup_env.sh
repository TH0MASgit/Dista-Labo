#!/bin/bash
# This script will install all the required packages for dista

sudo apt update && sudo apt upgrade


echo "Installing basic system utilities"

# Make sure numlock is on by default:
gsettings set org.gnome.settings-daemon.peripherals.keyboard numlock-state 'on'

# There's a couple basic tools that might be missing or outdated:
sudo apt install --yes htop tree curl ssh git ffmpeg

# Nano is the best text editor for the average user:
sudo apt install nano && echo -e "\nexport EDITOR=nano" >> ~/.bashrc

# We need this in order to connect to wifi networks:
sudo apt install network-manager && sudo service NetworkManager start
# or use this command: sudo nmcli device wifi connect 'SSID' password 'PASSWORD'

# We had problems setting some camera parameters via OpenCV so we use v4l:
sudo apt install --yes v4l-utils
# (run it using v4l2-ctl)


read -t 10 -n 1 -p 'Install VNC server? [Y/n] ' -i 'y' answer ; echo
[ -z "$answer" ] && answer="yes"  # 'yes' is the default choice
if [ "$answer" != "${answer#[Yy]}" ] ; then
    echo "Installing VNC server"
    cd "$(dirname "$0")"
    . setup_vnc.sh
fi


echo "Installing gitg and meld"
sudo apt install gitg
if sudo apt install meld ; then
    git config --global diff.tool meld
    git config --global merge.tool meld
fi


echo "Installing python3 and pip3"
sudo apt install python3 #&& echo "alias python=python3" >> ~/.bash_aliases
sudo apt install python3-pip #&& echo "alias pip=pip3" >> ~/.bash_aliases
sudo apt install python3-setuptools
sudo apt install libpython3-dev
#sudo apt install python-pip # (for python2)


echo "Installing core python libraries" 
# (installed system-wide since they are very common)
sudo apt install --yes gfortran # otherwise the scipy install fails on arm
sudo -H pip3 install -U cython numpy scipy


echo "Preparing development environment"
if [[ "$(uname -r)" == *tegra ]] ; then
    # All NVidia Jetsons (Xavier, Nano, TX2...) have a custom tegra kernel
    platform="jetson"
else
    platform=$(uname -m)
    case $platform in
      aarch*) platform="rpi" ;; # Raspberry pies run under the arm architecture
      x86_64) platform="x64" ;; # Desktops and laptops run on x86_64
      *) read -e -p "Platform detection failed, please specify: " -i "$platform" platform ;;
    esac
fi
echo "Target platform is $platform"

case $platform in
  jetson* | nano* | xavier*)
    # First, all Jetsons should have this built-in:
    sudo -H pip3 install -U jetson-stats
    # You can also manually set a specific fan speed using:
    #sudo sh -c 'echo 255 > /sys/devices/pwm-fan/target_pwm'
    
    # Having stability issues (especially on the Xaviers)? Try this:
    #service jetson_clocks status
    #systemctl disable jetson_clocks
    
    # Increase swap size to 8 GB:
    cd ~/util
    git clone https://github.com/JetsonHacksNano/resizeSwapMemory
    resizeSwapMemory/setSwapMemorySize.sh -g 8
    # Reboot and check it worked using `zramctl`
    echo 'Reboot now? (y/n)' && read x && [[ "$x" == "y" ]] && sudo reboot
    zramctl # expected = 4x 2GB
    
    # Cuda is already installed on the Jetsons
    # See https://developer.nvidia.com/embedded/jetpack
    
    echo "Installing PyTorch and TorchVision" # Jetsons require a custom version of PyTorch
    # See https://forums.developer.nvidia.com/t/pytorch-for-jetson-version-1-8-0-now-available/72048
    cd ~/util
    wget https://nvidia.box.com/shared/static/p57jwntv436lfrd78inwl7iml6p13fzh.whl -O torch-1.8.0-cp36-cp36m-linux_aarch64.whl
    sudo apt install --yes libopenblas-base libopenmpi-dev
    sudo -H pip3 install -U torch-1.8.0-cp36-cp36m-linux_aarch64.whl
    
    # Installing torchvision is a little more complicated:
    sudo apt install libjpeg-dev zlib1g-dev libavcodec-dev libavformat-dev libswscale-dev
    cd ~/util
    git clone --branch v0.9.0 https://github.com/pytorch/vision torchvision
    cd torchvision
    export BUILD_VERSION=0.9.0  # where 0.x.0 is the torchvision version
    sudo -H python3 setup.py install
    
    echo "Installing OpenCV" #TODO Isn't this already preinstalled too? maybe no contrib?
    cd ~/util
    git clone https://github.com/JetsonHacksNano/buildOpenCV
    cd buildOpenCV
    # Consider replacing the line NUM_JOBS=$(nproc) with NUM_JOBS=1 before continuing
    ./buildOpenCV.sh |& tee openCV_build.log
    
    echo "Installing Zed SDK"
    sdk_url="https://download.stereolabs.com/zedsdk/3.5/jp45/jetsons"
    sdk_ver="zedsdk-3.5-jp45"
    cd ~/util
    wget -O "$sdk_ver.run" "$sdk_url" && sh "$sdk_ver.run" --accept
    
    echo "Installing VS Code"
    cd ~/util
    git clone git@github.com:JetsonHacksNano/installVSCode.git
    installVSCode/installVSCodeWithPython.sh
  ;;
  
  
  rpi | rasp* | arm*) # NB: Rpies do not support Cuda
    # You might have to update pip to the latest version first:
    #python3 -m pip install --upgrade pip
    
    echo "Installing PyTorch and TorchVision"
    # See https://pytorch.org/get-started/previous-versions/
    sudo -H pip3 install -U torch==1.8.0 torchvision==0.9.0
    
    echo "Installing OpenCV"
    sudo -H pip3 install -U opencv-contrib-python==4.1.1
  ;;
  
  
  x64 | amd64 | *86)
    # Install Cuda 10.2
    echo "Installing Cuda"
    sudo mv cuda-ubuntu1804.pin /etc/apt/preferences.d/cuda-repository-pin-600
    wget http://developer.download.nvidia.com/compute/cuda/10.2/Prod/local_installers/cuda-repo-ubuntu1804-10-2-local-10.2.89-440.33.01_1.0-1_amd64.deb
    sudo dpkg -i cuda-repo-ubuntu1804-10-2-local-10.2.89-440.33.01_1.0-1_amd64.deb
    sudo apt-key add /var/cuda-repo-10-2-local-10.2.89-440.33.01/7fa2af80.pub
    sudo apt-get update
    sudo apt-get -y install cuda
    
    echo "Installing PyTorch and TorchVision"
    # See https://pytorch.org/get-started/previous-versions/
    sudo -H pip3 install -U torch==1.8.0 torchvision==0.9.0
    
    echo "Installing OpenCV"
    #TODO we should use the version compiled for Cuda
    sudo -H pip3 install -U opencv-contrib-python==4.1.1
    
    # Install Zed SDK for x86
    echo "Installing Zed SDK"
    wget https://stereolabs.sfo2.cdn.digitaloceanspaces.com/zedsdk/3.2/ZED_SDK_Ubuntu18_cuda10.2_v3.2.0.run
    sh ZED_SDK_Ubuntu18_cuda10.2_v3.1.2.run
    cd /usr/local/zed
    python3 -m pip install `python3 get_python_api.py`
    
    echo "Installing PyCharm and VS Code"
    sudo snap install --classic pycharm-community
    sudo snap install --classic code
  ;;
  
  
  *)
    echo "Unknown platform: $platform"
    echo "Make sure to install Cuda, OpenCV and Zed SDK yourself"
  ;;
esac


echo "Installing python libraries"
cd "$(dirname "$0")"
. setup_pip.sh


read -t 10 -n 1 -p 'Install SQL server? [Y/n] ' -i 'y' answer ; echo
[ -z "$answer" ] && answer="yes"  # 'yes' is the default choice
if [ "$answer" != "${answer#[Yy]}" ] ; then
    echo "Installing sqlite and mariadb"
    cd "$(dirname "$0")"
    . setup_sql.sh
fi


echo "Installation finished"

