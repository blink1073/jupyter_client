#!/usr/bin/env python
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import os

from setuptools import find_packages
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

version_ns = {}
with open(os.path.join(here, 'jupyter_client', '_version.py')) as f:
    exec(f.read(), {}, version_ns)

from setuptools.command.bdist_egg import bdist_egg

class bdist_egg_disabled(bdist_egg):
    """Disabled version of bdist_egg

    Prevents setup.py install from performing setuptools' default easy_install,
    which it should never ever do.
    """
    def run(self):
        sys.exit("Aborting implicit building of eggs. Use `pip install .` to install from source.")


setup_args = dict(
    name            = name,
    version         = version_ns['__version__'],
    packages        = packages,
    description     = 'Jupyter protocol implementation and client libraries',
    author          = 'Jupyter Development Team',
    author_email    = 'jupyter@googlegroups.com',
    url             = 'https://jupyter.org',
    license         = 'BSD',
    platforms       = "Linux, Mac OS X, Windows",
    keywords        = ['Interactive', 'Interpreter', 'Shell', 'Web'],
    project_urls    = {
        'Documentation': 'https://jupyter-client.readthedocs.io',
        'Source': 'https://github.com/jupyter/jupyter_client/',
        'Tracker': 'https://github.com/jupyter/jupyter_client/issues',
    },
    classifiers     = [
        'Framework :: Jupyter',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires = [
        'traitlets',
        'jupyter_core',
        'pyzmq>=13',
        'python-dateutil>=2.1',
        'entrypoints',
        'tornado>=4.1',
    ],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, <4',
    extras_require   = {
        'test': ['ipykernel', 'ipython', 'mock'],
        'test:python_version == "3.3"': ['pytest<3.3.0'],
        'test:python_version >= "3.4" or python_version == "2.7"': ['pytest'],
    },
    cmdclass         = {
        'bdist_egg': bdist_egg if 'bdist_egg' in sys.argv else bdist_egg_disabled,
    },
    entry_points={
        'console_scripts': [
            'jupyter-kernelspec = jupyter_client.kernelspecapp:KernelSpecApp.launch_instance',
            'jupyter-run = jupyter_client.runapp:RunApp.launch_instance',
            'jupyter-kernel = jupyter_client.kernelapp:main',
        ],
        'jupyter_client.kernel_providers' : [
            'spec = jupyter_client.discovery:KernelSpecProvider',
            'pyimport = jupyter_client.discovery:IPykernelProvider',
        ]
    },
)
