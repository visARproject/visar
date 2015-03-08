libVisar
========

Contains everything you've ever wanted in a Python augmented reality package.

# Setup

## Requirements
* vispy (Install from source, ```git clone git@github.com:vispy/vispy.git```)
* OSMViz (For mapping, install from source, ```git clone https://github.com/cbick/osmviz.git```)
* numpy
* PyOpenGL
* QT4
* scipy (For terrain generator)

Install all of these for things to work!

## Install
Do this! You don't have to run this every time you make a change
    sudo python setup.py develop

## Uninstall
    sudo python setup.py develop --uninstall

## Permanent Install
    sudo python setup.py install

## Uninstall from permanent install
    sudo pip uninstall libVisar


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


# Consideration
- Should be able to bench-test with a simulator (i.e. change pose source, change view source)
- Should be able to bench-test with AND without oculus rift distortion
- It should be easy to add simulated input