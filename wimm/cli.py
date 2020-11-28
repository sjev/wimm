#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main cli application

@author: jev
"""

import wimm # app version is defined in __init__.py
import wimm.utils as utils
import wimm.core as core

import os
import click
import yaml


@click.group()
@click.version_option(version=wimm.__version__)
def cli():
    pass

@click.group()
def show():
    """ print reports """

@click.group('import')
def import_data():
    """ import statements, documents etc. """
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
    

    
@click.command('statement')
@click.argument('data_file')
def import_statement(data_file):
    """import bank statement to the end of `transactions.yaml`"""
    print(f'importing {data_file}') 
    
    if not os.path.exists(data_file):
        print('ERROR: file not found')
        return
    
    transactions = core.Transactions.from_bank_statement(data_file)
    
    with open('transactions.yaml','a') as f:
        f.write( f'\n# ---IMPORT--- at {utils.timestamp()} file: {data_file}\n')
        f.write(transactions.to_yaml())
        

@click.command('balance')
def show_balance():
    """ print current balance """
    transactions = core.Transactions.from_yaml('/home/jev/Development/wimm/scratch/transactions.yaml')
    accounts = core.Accounts()
    transactions.apply(accounts,create_accounts=True) # TODO: make option for creating accounts
    
    print('----------Balance-----------')
    for k,v in accounts.items():
        print(f"{k:<25}{v:>20.2f}")
    print('----------------------------')
    print(f'SUM: {accounts.sum():.2f}')

# build groups
import_data.add_command(import_statement)    
    
show.add_command(show_balance)

cli.add_command(init)
cli.add_command(import_data)
cli.add_command(show)

if __name__ == "__main__":
    cli()