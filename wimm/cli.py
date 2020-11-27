#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main cli application

@author: jev
"""

import wimm # app version is defined in __init__.py
import wimm.utils as utils

import click
import yaml

@click.group()
@click.version_option(version=wimm.__version__)
def cli():
    pass

@click.command()
def init():
    """ initialize directories and necessary files """
    
    from wimm.structure import accounts
    with open(r'accounts.yaml','w') as file:
        yaml.dump(accounts, file)
    
    
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