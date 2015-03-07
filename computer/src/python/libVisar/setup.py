#!/usr/bin/env python

from setuptools import setup

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
        'libVisar.OpenGL', 'libVisar.OpenGL.shaders', 'libVisar.OpenGL.rift_parameters', 
        'libVisar.visar', 'libVisar.visar.drawables', 'libVisar.visar.environments', 'libVisar.visar.globals'
    ],
)
