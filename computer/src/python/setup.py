from distutils.core import setup
setup(name='jOpenGL',
    version='1.0',
    description='Python Oculus Rift DK2 Driver',
    author='Jacob Panikulam',
    author_email='jpanikulam@ufl.edu',
    url='https://www.python.org/',
    package_dir = {
    	'': '.',
	},
    packages=[
    	'libVisar.OpenGL', 'libVisar.OpenGL.shaders', 'libVisar.OpenGL.rift_parameters',
    	# 'oculusvr',
    ],
)
