from distutils.core import setup

setup(
    name='py-august',
    version='0.12.0',
    packages=['august'],
    url='https://github.com/snjoetw/py-august',
    license='MIT',
    author='snjoetw',
    author_email='snjoetw@gmail.com',
    description='Python API for August Smart Lock and Doorbell',
    install_requires=['requests', 'vol', 'python-dateutil']
)
