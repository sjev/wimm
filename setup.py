#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from setuptools import setup, find_packages
import wimm

setup(
      name='wimm',
      version = wimm.__version__,
      description="Where Is My Money? - plain text accounting tool",
      packages=find_packages(include=['wimm']),
      author= "Jev Kuznetsov",
      url = "https://github.com/sjev/wimm",
      install_requires=['click'],
      license='BSD',
      entry_points={
        'console_scripts': ['wimm=wimm.cli:cli'], }
      )