#!/usr/bin/env python

from setuptools import setup
from subprocess import call

setup(name='libVisar',
    version='1.0',
    description='Python Oculus Rift DK2 Driver',
    author='Jacob Panikulam',
    author_email='jpanikulam@ufl.edu',
    url='https://www.python.org/',
    entry_points={
       "console_scripts": ["vsr=libVisar.visar.render_package:main"]
    },
    package_dir={
        '': '.',
    },
    packages=[
        'libVisar',
        'libVisar.OpenGL', 'libVisar.OpenGL.shaders', 'libVisar.OpenGL.rift_parameters', 'libVisar.OpenGL.drawing',
        'libVisar.visar', 'libVisar.visar.drawables', 'libVisar.visar.environments', 'libVisar.visar.globals'
    ],
    test_suite="libVisar.test"

)

# Janky way of running the make command, replace later
call(['make','-C','libVisar/visar/audio/','test']) # build the c files


