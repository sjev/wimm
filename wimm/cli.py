#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main cli application

@author: jev
"""

import wimm

import click

@click.group()
@click.version_option(version=wimm.__version__)
def cli():
    print('starting cli')

@click.command()
def hello():
    print('hello')
    
@click.command()
def bye():
    print('bye')
    
@click.command()
@click.argument('what')
def say_what(what):
    """ repeat after me..."""
    print('Say:',what)

cli.add_command(hello)
cli.add_command(bye)
cli.add_command(say_what)

if __name__ == "__main__":
    cli()