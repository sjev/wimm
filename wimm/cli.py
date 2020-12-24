#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main cli application

@author: jev
"""

import wimm # app version is defined in __init__.py
import wimm.utils as utils
import wimm.core as core
import wimm.structure as structure

import os
import click
from click import echo
import yaml
from pathlib import Path



def get_path():
    """ get path of database directory """

    var = 'WIMM_PATH'
    val = os.getenv(var)
    
    if not val:
        echo(f"environment variable {var} not found. ")
        import sys
        sys.exit()
        
    return Path(val)

def accounts():
    """ load accounts """
    
    p = PATH / structure.files['accounts']
    assert p.exists(), f"File {p} not found"
    return core.Accounts.from_yaml(p)

def transactions():
    """ load transactions """
    p = PATH / structure.files['transactions']
    assert p.exists(), f"File {p} not found"
    return core.Transactions.from_yaml(p)

@click.group()
@click.version_option(version=wimm.__version__)
def cli():
    pass

@click.group()
def show():
    """ print reports. Provide an command what to show """

@click.group('import')
def import_data():
    """ import statements, documents etc. """
    pass

@click.command()
def init():
    """ initialize current directory with necessary files. Also creates a config file in user directory"""
    
    # create files
    
    utils.save_yaml(PATH / structure.files['accounts'], structure.accounts)
    utils.save_yaml(PATH / structure.files['settings'], structure.settings)
    utils.save_yaml(PATH / structure.files['transactions'], structure.transactions)
    
    # create folders
    for folder in structure.folders:
        try:
            os.mkdir(folder)
        except Exception as e:
            print('Could not create folder:',e)
    

    
@click.command('statement')
@click.option('--bank',default='ASN',help='type of bank statement')
@click.argument('account_name')
@click.argument('data_file')
def import_statement(bank, account_name,data_file):
    """import bank statement to the end of `transactions.yaml`"""
    print(f'importing {data_file}') 
    
    if not os.path.exists(data_file):
        print('ERROR: file not found')
        return
    
    account = accounts()[account_name]
    transactions = account.parse_bank_statement(data_file)
    
    with open('transactions.yaml','a') as f:
        f.write( f'\n# ---IMPORT--- at {utils.timestamp()} file: {data_file}\n')
        f.write(transactions.to_yaml())
        

@click.command('balance')
def show_balance():
    """ print current balance """
    
    balance = core.balance(accounts(), transactions())
    
    print('----------Balance-----------')
    print(balance)
    print('----------------------------')
    print(f'SUM: {balance.sum():.2f}')


@click.command('transactions')
def show_transactions():
    """ show transactions as yaml data """
    
    print(transactions().to_yaml())
    
@click.command('accounts')
def show_accounts():
    """ show accounts """
    for name in accounts().keys():
        print(name)

# build groups
import_data.add_command(import_statement)    
    
show.add_command(show_balance)
show.add_command(show_transactions)
show.add_command(show_accounts)

cli.add_command(init)
cli.add_command(import_data)
cli.add_command(show)

PATH = get_path()


if __name__ == "__main__": # note - name will be wimm.cli in case of terminal cmd
    cli()