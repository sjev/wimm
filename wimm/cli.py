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


def start_balance():
    return core.load_data('balance', PATH)


def transactions():
    return core.load_data('transactions', PATH)


def invoices():
    return core.load_data('invoices', PATH)


def hasher():
    return utils.Hasher(PATH / structure.files['hashes'])


@click.command()
def info():
    """ show status """
    echo(f'Data location: {PATH}')
    echo('Hashed files: %i' % len(hasher().hashes))


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
    utils.save_yaml(PATH / structure.files['balance'], structure.accounts)
    utils.save_yaml(
        PATH / structure.files['transactions'], structure.transactions)
    utils.save_yaml(PATH / structure.files['invoices'], structure.invoices())
    utils.save_yaml(PATH / structure.files['settings'], structure.settings)

    # create folders
    for folder in structure.folders.values():
        p = PATH / folder
        if not p.exists():
            p.mkdir()


@click.command('hash')
def init_hash():
    """ rebuild stored file hashes """

    h = hasher()
    h.delete_hashes()

    for key in ['INR', 'INS']:
        h.add(PATH / structure.folders[key])


@click.command('statement')
@click.argument('bank')
@click.option('--account', default=None, help='account name to fill in')
@click.argument('data_file')
def import_statement(bank, data_file, account):
    """import bank statement to the end of `transactions.yaml`"""

    import wimm.data_importers as importers
    import wimm.structure as structure 

    loaders = {'KNAB': importers.knab_import}

    if bank not in loaders.keys():
        echo(
            f'Import for {bank} not supported.\nSupported options are {list(loaders.keys())}')
        return

    echo(f'importing {data_file}')

    if not os.path.exists(data_file):
        echo('ERROR: file not found')
        return

    if account is None:
        transactions = loaders[bank](data_file)
    else:
        transactions = loaders[bank](data_file, account)

    
    with (PATH / structure.files['transactions']).open('a') as f:
        f.write(f'\n# ---IMPORT--- at {utils.timestamp()} file: {data_file}\n')
        f.write(transactions.to_yaml())


@click.command('balance')
@click.option('--depth', default=2, help='account depth level to show')
@click.option('--nozeros', is_flag=True)
def show_balance(depth, nozeros):
    """ print current balance """

    balance = core.balance(
        transactions(), start_balance(), invoices(), depth=depth)

    if nozeros:
        balance = balance[balance != 0]

    print('----------Balance-----------')
    print(balance.to_string())
    print('----------------------------')
    print(f'SUM: {balance.sum():.2f}')


@click.command('transactions')
def show_transactions():
    """ show transactions as yaml data """

    print(transactions().to_yaml())


@click.command('invoices')
def show_invoices():
    """ show invoices """

    print(invoices().to_df().to_string())


@click.command('config')
def show_config():
    """ show wimm configuration """
    for k, v in wimm.config.items():
        print(f'{k}:{v}')

@click.command('invoice')
@click.argument("pattern")
def add_invoice(pattern):
    """ add invoice(s). For multiple files provide a search pattern, like *.pdf """

    if pattern[0] == '*':
        files = [p.absolute() for p in Path('.').glob(pattern)]
        # sort on modification times
        files = sorted(files, key=os.path.getmtime)
        echo(f'Adding {len(files)} files')
    else:
        files = [Path(pattern).absolute()]

    for src_file in files:
        if not src_file.exists():
            echo('File not found')
            continue

        hsh = hasher()
        if hsh.is_present(src_file):
            echo(f'{src_file} is already in database.')
            continue

        import subprocess
        import sys
        devnull = open(os.devnull, 'w')
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, src_file.as_posix()],
                        stdout=devnull, stderr=devnull)

        echo('Adding invoce. negative amount = incoming invoice')

        data = {}

        data['amount'] = click.prompt('amount', type=float)

        prefix = 'INS' if data['amount'] > 0 else 'INR'
        data['id'] = click.prompt('id', invoices().get_next_id(prefix))
        data['tax'] = click.prompt('tax', utils.tax(data['amount']))

        if prefix == 'INR':
            data['sender'] = click.prompt('sender')

        data['description'] = click.prompt('description')
        data['date'] = click.prompt('date', utils.date())
        data['due_date'] = click.prompt(
            'due_date', utils.date_offset(data['date'], 30))

        dest_file = PATH / \
            structure.folders[prefix] / \
            (data['id']+'_'+src_file.name.replace(' ', '_'))
        echo('copying file to:'+str(dest_file))
        shutil.copy(src_file, dest_file)
        hsh.add(dest_file)

        data['documents'] = dest_file.relative_to(PATH).as_posix()

        invoices_new = core.Invoices()
        invoices_new.append(core.Invoice(**data))

        with open(PATH / structure.files['invoices'], 'a') as f:
            f.write(invoices_new.to_yaml())


# build groups
import_data.add_command(import_statement)

show.add_command(show_balance)
show.add_command(show_transactions)
show.add_command(show_invoices)
show.add_command(show_config)

init.add_command(init_files)
init.add_command(init_hash)

add.add_command(add_invoice)

# build top levelcommands
cli.add_command(init)
cli.add_command(import_data)
cli.add_command(show)
cli.add_command(info)
cli.add_command(add)


if __name__ == "__main__":  # note - name will be wimm.cli in case of terminal cmd

    PATH = list(Path(__file__).parents)[1] / 'tests/data'
else:
    PATH = wimm.config['path']
    if not PATH:
        echo("WARNING: environment variable WIMM_PATH is not set")