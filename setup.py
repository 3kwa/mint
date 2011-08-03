from distutils.core import setup

version = '0.5'

setup(
    name='mint',
    version=version,
    description='Simple indetion based template engine',
    #long_description=open('README.rst').read(),
    packages=['mint'],
    license='MIT',
    author='Tim Perevezentsev',
    author_email='riffm2005@gmail.com',
    url='http://github.com/riffm/mint',
    entry_points={'console_scripts': ['mint = mint.cli:main']}
)
