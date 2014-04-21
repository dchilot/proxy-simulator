# commands that may be used to test the simulator
# install mandatory packages (mercurial is only needed for the vim install from sources)
sudo apt-get update
sudo apt-get install -qq -y git
sudo apt-get install -qq -y python-dev
sudo apt-get install -qq -y python-virtualenv
sudo apt-get install -qq -y mercurial
sudo apt-get install -qq -y make
sudo apt-get install -qq -y g++
sudo apt-get install -qq -y libzmq-dev
sudo apt-get install -qq -y libprotobuf-dev libprotobuf-lite7 protobuf-compiler
sudo apt-get install -qq -y libsdl1.2-dev
sudo apt-get install -qq -y libsdl-image1.2-dev libsdl-sound1.2-dev libsdl-mixer1.2-dev
sudo apt-get install -qq -y libode-dev
sudo apt-get install -qq -y libsmpeg-dev
sudo apt-get install -qq -y libv4l-dev
sudo apt-get install -qq -y freeglut3-dev
sudo apt-get install -qq -y libc6 libjpeg8 libpng12-0 libportmidi0 libsdl-image1.2 libsdl-ttf2.0-0 libsdl1.2debian libsmpeg0 libx11-6 ttf-freefont
cd /usr/include/linux
# patch needed for a python package (probably pygame)
sudo ln -s ../libv4l1-videodev.h videodev.h
# now deal with the project itself
mkdir /home/vagrant/orwell
cd /home/vagrant/orwell
git clone http://github.com/dchilot/proxy-simulator.git
cd proxy-simulator
git submodule init
git submodule update
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=$(pwd)
git submodule update --init --recursive
source ./generate.sh
#./runner.sh