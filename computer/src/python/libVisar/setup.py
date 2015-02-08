from distutils.core import setup
setup(name='jOpenGL',
    version='1.0',
    description='Python Oculus Rift DK2 Driver',
    author='Jacob Panikulam',
    author_email='jpanikulam@ufl.edu',
    url='https://www.python.org/',
    #entry_points={
    #    "console_scripts": ["ds4drv=ds4drv.__main__:main"]
    #},
    package_dir = {
    	'libVisar': '.',

    },
    packages=[
    	'libVisar.OpenGL', 'libVisar.OpenGL.shaders', 'libVisar.OpenGL.rift_parameters',
        'libVisar.visar', 'libVisar.visar.drawables',
    ],
)
