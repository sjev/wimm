#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main cli application

@author: jev
"""

import wimm # app version is defined in __init__.py
import wimm.utils as utils

import os
import click
import yaml


@click.group()
@click.version_option(version=wimm.__version__)
def cli():
    pass

@click.command()
def init():
    """ initialize directories and necessary files """
    
    # create files
    import wimm.structure as structure
    utils.save_yaml(r'accounts.yaml',structure.accounts)
    utils.save_yaml(r'settings.yaml', structure.settings)
    utils.save_yaml(r'transactions.yaml', structure.transactions)
    
    # create folders
    for folder in structure.folders:
        try:
            os.mkdir(folder)
        except Exception as e:
            print('Could not create folder:',e)
    
@click.command()
def bye():
    print('bye')
    
@click.command()
@click.argument('what')
def say_what(what):
    """ repeat after me..."""
    print('Say:',what)

cli.add_command(init)
cli.add_command(bye)
cli.add_command(say_what)

if __name__ == "__main__":
    cli()