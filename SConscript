env = Environment()

def build_oglplus(target, source, env):
    target, = target
    source, = source
    
    import os
    import subprocess
    import tempfile
    import shutil
    
    builddir = tempfile.mkdtemp()
    
    try:
        subprocess.check_call([os.path.join(source.get_abspath(), 'configure.py'),
            '--use-glew', '--prefix='+target.get_abspath(),
            '--no-examples', '--no-docs',
        ], cwd=builddir)
        subprocess.check_call(['make'], cwd=os.path.join(builddir, '_build'))
        
        if os.path.exists(target.get_abspath()):
            shutil.rmtree(target.get_abspath())
        subprocess.check_call(['make', 'install'], cwd=os.path.join(builddir, '_build'))
        subprocess.check_call(['cp', '-rv', os.path.join(source.get_abspath(), 'utils', 'oglplus'),
            os.path.join(target.get_abspath(), 'include')])
    finally:
        shutil.rmtree(builddir)
oglplus = env.Command(Dir('oglplus'), Dir('#ext/oglplus'), build_oglplus)

env.Program(target='main', source=['src/main.cpp'])
