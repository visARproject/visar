libVisar
========

Contains everything you've ever wanted in a Python augmented reality package.

# Setup

## Requirements
* vispy (Install from source, ```git clone git@github.com:vispy/vispy.git```, must be commit b64489b)
* OSMViz (Now included in vsr)
* numpy
* PyOpenGL
* QT4
* scipy (For terrain generator)
* libasound2-dev (audio)
* either libspeex-dev (default speex codec) or libopus-dev (opus codec mode)
* gcc
* automake
* autoconf
* libtool
* bison
* swig
* python-dev
* libpulse-dev
* sphinxBase (Install from source, ```git clone https://github.com/cmusphinx/sphinxbase```)
* pocketSphinx (Install from source, ```git clone https://github.com/cmusphinx/pocketsphinx```)

Install all of these for things to work!

## Install
Get the requirements using install.sh

Do this! You don't have to run this every time you make a change
    sudo python setup.py develop
    ./build_vsr [opus]

## Uninstall
    sudo python setup.py develop --uninstall
    ./build_vsr clean

## Testing

# Usage
Type
    vsr
to start the render package, once you have installed libVisar.

Or cd into the libVisar directory
(The output of ls should be 'libVisar', 'libVisar.egg-info', 'readme.md', 'setup.py')
and run 
    python -m libVisar.visar.render_package


# Features
- Map
- Terrain simulation
- Audio Communication

# Voice Control
To add words to be recognized navigate to the file "libVisar/visar/audio/corpus.txt". Add the words you wish to add at the bottom. Go to "http://www.speech.cs.cmu.edu/tools/lmtool-new.html", and upload the file. Take the .dic and the .lm, rename them to dictionary.dic and dictionary.lm, respectively, and replace the other two in the aforementioned folder.


# Consideration
- Should be able to bench-test with a simulator (i.e. change pose source, change view source)
- Should be able to bench-test with AND without oculus rift distortion
- It should be easy to add simulated input


# Running stuff with Forrest's Kalman Filter

## Installing
To install, go to visar, pull
git submodule update --init
mkdir -p ~/repos/visar_ws/src
cd ~/repos/visar_ws/src
catkin_init_workspace
ln -s (path to visar/ros) visar_ros
cd ..
catkin_make
source ./devel/setup.bash
catkin_make

## Running
roslaunch visar_gps run.launch host_id:=visar2 interface:=192.168.1.142 fake_gps:=true --screen
(Make interface your ip)
Then run vsr your preferred way

You should see a beacon near you.

