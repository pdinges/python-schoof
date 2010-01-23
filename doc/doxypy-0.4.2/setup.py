#!/usr/bin/env python

import sys
import os

from glob import glob
from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES 

import doxypy

setup(
	name=doxypy.__applicationName__,
	version=doxypy.__version__,
	author='Philippe Neumann & Gina Haeussge',
	author_email='doxypy@demod.org',
	url=doxypy.__website__,
	description=doxypy.__blurb__,
	license=doxypy.__licenseName__,
	
	classifiers=[
		"Programming Language :: Python",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: GNU General Public License (GPL)",
		"Operating System :: OS Independent",
		"Topic :: Software Development :: Documentation"
	],
	scripts=['doxypy.py']
)
