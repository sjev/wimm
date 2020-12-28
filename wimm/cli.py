#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main cli application

@author: jev
"""

import wimm  # app version is defined in __init__.py
import wimm.utils as utils
import wimm.core as core
import wimm.structure as structure

import os
import shutil
from pathlib import Path
import click
from click import echo



def accounts():
    return core.load_data('accounts', PATH)


def transactions():
    return core.load_data('transactions', PATH)


def invoices():
    return core.load_data('invoices', PATH)


@click.command()
def info():
    """ show status """
    echo(f'Data location: {PATH}')


@click.group()
@click.version_option(version=wimm.__version__)
def cli():
    pass


@click.group()
def show():
    """ print reports. Provide an command what to show """
    pass

@click.group()
def add():
    """ add items to database """
    pass


@click.group('import')
def import_data():
    """ import statements, documents etc. """
    pass

@click.group()
def init():
    """ initialize data, use with caution """
    pass

@click.command('files')
def init_files():
    """ initialize current directory with necessary files. Also creates a config file in user directory"""

    # create files
    utils.save_yaml(PATH / structure.files['accounts'], structure.accounts)
    utils.save_yaml(
        PATH / structure.files['transactions'], structure.transactions)
    core.Invoices([structure.invoices()[0]]).to_yaml(
        PATH / structure.files['invoices'])

    # create folders
    for folder in structure.folders.values():
        try:
            (PATH / folder).mkdir()
        except Exception as e:
            print('Could not create folder:', e)


@click.command('hash')
def init_hash():
    """ rebuild stored file hashes """
    
    hasher = utils.Hasher(PATH / structure.files['hashes'])
    hasher.delete_hashes()
    
    for key in ['INR','INS']:
        hasher.add(PATH / structure.folders[key])
    

@click.command('statement')
@click.option('--bank', default='ASN', help='type of bank statement')
@click.argument('account_name')
@click.argument('data_file')
def import_statement(bank, account_name, data_file):
    """import bank statement to the end of `transactions.yaml`"""
    print(f'importing {data_file}')

    if not os.path.exists(data_file):
        print('ERROR: file not found')
        return

    account = accounts()[account_name]
    transactions = account.parse_bank_statement(data_file)

    with open('transactions.yaml', 'a') as f:
        f.write(f'\n# ---IMPORT--- at {utils.timestamp()} file: {data_file}\n')
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


@click.command('invoices')
def show_invoices():
    """ show invoices """

    for inv in invoices():
        print(inv)


@click.command('invoice')
@click.argument("filename", autocompletion = ['foo.pdf', 'bar.pdf'])
def add_invoice(filename):
    
    
    src_file = Path(filename).absolute()
    if not src_file.exists():
        echo('File not found')
        return
    
    import subprocess, sys
    devnull = open(os.devnull, 'w')
    opener ="open" if sys.platform == "darwin" else "xdg-open"
    #subprocess.call([opener, src_file.as_posix()],stdout=devnull, stderr=devnull)
    
    echo('Adding invoce. negative amount = incoming invoice')
    
    data = {}
    
    data['amount'] = click.prompt('amount', type=float)
    
    prefix = 'INS' if data['amount'] > 0 else 'INR'
    data['id'] = click.prompt('id',invoices().get_next_id(prefix))
    data['tax'] = click.prompt('tax',utils.tax(data['amount']))
    
    if prefix == 'INR':
        data['sender']  = click.prompt('sender')
        
    data['description'] = click.prompt('description')
    data['date'] = click.prompt('date', utils.date())
    data['due_date'] = click.prompt('due_date', utils.date(30))
    
    dest_file = PATH / structure.folders[prefix] / (data['id']+'_'+src_file.name)
    echo('copying file to:'+str(dest_file))
    shutil.copy(src_file,dest_file)
    
    data['documents'] = dest_file.relative_to(PATH).as_posix()
    
    invoices_new = core.Invoices()
    invoices_new.append(core.Invoice(**data))    
    
    
    with open(PATH / structure.files['invoices'],'a') as f:
        f.write(invoices_new.to_yaml())

# build groups
import_data.add_command(import_statement)

show.add_command(show_balance)
show.add_command(show_transactions)
show.add_command(show_accounts)
show.add_command(show_invoices)

init.add_command(init_files)
init.add_command(init_hash)

add.add_command(add_invoice)

# build top levelcommands
cli.add_command(init)
cli.add_command(import_data)
cli.add_command(show)
cli.add_command(info)
cli.add_command(add)



PATH = utils.get_path()


if __name__ == "__main__":  # note - name will be wimm.cli in case of terminal cmd
    cli()
