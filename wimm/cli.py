#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main cli application

@author: jev
"""

import os
import shutil
from pathlib import Path
import click
from click import echo
import yaml

import wimm  # app version is defined in __init__.py
import wimm.utils as utils
import wimm.core as core
import wimm.structure as structure


def start_balance():
    return core.load_data('balance', PATH)


def transactions():
    return core.load_data('transactions', PATH)


def invoices():
    return core.load_data('invoices', PATH)


def hasher():
    return utils.Hasher(PATH / structure.files['hashes'])


def initialize():
    """
    initialization function for data
    names are comma separated items

    """

    if click.confirm('Init files?'):
        # create files
        utils.save_yaml(PATH / structure.files['balance'], structure.accounts)
        utils.save_yaml(
            PATH / structure.files['transactions'], structure.transactions)
        utils.save_yaml(
            PATH / structure.files['invoices'], structure.invoices()[:1])

        # create folders
        for folder in structure.folders.values():
            p = PATH / folder
            if not p.exists():
                p.mkdir()

    if click.confirm('Init hash?'):
        echo('Rebuilding hashes')
        h = hasher()
        h.delete_hashes()

        for key in ['INR', 'INS']:
            h.add(PATH / structure.folders[key])

    if click.confirm('Init settings?'):

        settings = structure.settings
        settings['company_name'] = click.prompt(
            'Company name:', settings['company_name'])

        utils.save_yaml(PATH / structure.files['settings'],
                        settings,
                        ask_confirmation=False)


@click.command()
def info():
    """ show status """
    #echo(f'PATH: {PATH}')
    echo('Hashed files: %i' % len(hasher().hashes))
    for k, v in wimm.get_settings().items():
        if isinstance(v, dict):
            print(k)
            print(yaml.dump(v))
        else:
            print(f'{k}: {v}')


@click.group()
@click.version_option(version=wimm.__version__)
def cli():
    pass


@click.group()
def show():
    """ print reports. Provide an command what to show """


@click.group()
def add():
    """ add items to database """


@click.group()
def convert():
    """ conversion utils """


@click.group('import')
def import_data():
    """ import statements, documents etc. """


@click.command()
def init():
    """ initialize data, use with caution """
    initialize()


@click.command('statement')
@click.argument('bank')
@click.argument('data_file')
def import_statement(bank, data_file):
    """import bank statement to the end of `transactions.yaml`"""

    import wimm.importers.asn_bank as asn
    loaders = {'ASN': asn.Importer}

    if bank not in loaders.keys():
        echo(
            f'Import for {bank} not supported.\nSupported options are {list(loaders.keys())}')
        return

    echo(f'importing {data_file}')

    if not os.path.exists(data_file):
        echo('ERROR: file not found')
        return

    loader = loaders[bank](data_file)

    trs = loader.transactions()

    with (PATH / structure.files['transactions']).open('a') as f:
        f.write(f'\n# ---IMPORT--- at {utils.timestamp()} file: {data_file}\n')
        f.write(trs.to_yaml())


@click.command('balance')
@click.option('--depth', default=3, help='account depth level to show')
@click.option('--nozeros', is_flag=True)
def show_balance(depth, nozeros):
    """ print current balance """

    balance = core.balance(
        transactions(), start_balance(), invoices(), depth=depth)

    if nozeros:
        balance = balance[balance != 0]

    print('----------Balance-----------')
    print(balance.to_string(float_format=utils.human_format))
    print('----------------------------')
    print(f'SUM: {balance.sum():.2f}')


@click.command('transactions')
def show_transactions():
    """ show transactions as yaml data """

    print(transactions().to_yaml())


@click.command('invoices')
def show_invoices():
    """ show invoices """

    for inv in invoices():
        print(inv)


def add_invoice(prefix, src_file=None, no_hash=False):
    """ add a single invoice """

    if src_file is not None:
        assert src_file.exists(), 'File not found'

    inv = core.Invoice()

    inv['amount'] = click.prompt('amount', type=float)

    inv['id'] = click.prompt('id', invoices().get_next_id(prefix))
    inv['tax'] = click.prompt('tax', utils.tax(inv['amount']))

    inv['ext_name'] = click.prompt('ext_company_name')

    inv.set_accounts()
    inv['from'] = click.prompt('from acct', inv['from'])
    inv['to'] = click.prompt('to acct', inv['to'])

    inv['description'] = click.prompt('description')
    inv['date'] = click.prompt('date', utils.date())
    inv['due_date'] = click.prompt(
        'due_date', utils.date_offset(inv['date'], 30))

    if src_file is not None:
        dest_file = PATH / \
            structure.folders[prefix] / \
            (inv['id']+'_'+src_file.name.replace(' ', '_'))
        echo('copying file to:'+str(dest_file))
        shutil.copy(src_file, dest_file)
        inv['attachment'] = dest_file.relative_to(PATH).as_posix()

        if not no_hash:
            hsh = hasher()
            hsh.add(dest_file)

    invoices_new = core.Invoices()
    invoices_new.append(inv)

    with open(PATH / structure.files['invoices'], 'a') as f:
        f.write(invoices_new.to_yaml())

    with (PATH / structure.files['transactions']).open('a') as f:
        f.write(inv.transaction().to_yaml())


@click.command('invoice')
@click.argument('prefix')
@click.option('--pattern', '-p', default=None, help='Filename or a search pattern, like *.pdf')
@click.option("--no_hash", is_flag=True, help="Do not check if file is already in database")
def add_invoices(prefix, pattern, no_hash):
    """ add invoice(s).

    \b
    PREFIX invoice prefix, 3 characters (INR,INS etc.)

    """
    import subprocess
    import sys

    if pattern is None:
        add_invoice(prefix)
        return

    else:
        if pattern[0] == '*':
            files = [p.absolute() for p in Path('.').glob(pattern)]
            # sort on modification times
            files = sorted(files, key=os.path.getmtime)
            echo(f'Adding {len(files)} files')
        else:
            files = [Path(pattern).absolute()]

    for src_file in files:
        try:
            assert src_file.exists(), 'File not found'

            if not no_hash:
                hsh = hasher()
                assert hsh.is_present(
                    src_file) == False, f'{src_file} is already in database.'

            devnull = open(os.devnull, 'w')
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, src_file.as_posix()],
                            stdout=devnull, stderr=devnull)

            add_invoice(prefix, src_file, no_hash)

        except AssertionError as e:
            echo(e)


@click.command('transactions')
def convert_transactions():

    if click.confirm('Transactions file will be overwritten. Sure?'):
        fname = PATH / structure.files['transactions']
        data_v1 = yaml.load(fname.open(), Loader=yaml.SafeLoader)
        trs = core.Transactions(
            [wimm.core.Transaction.from_v1(d).to_dict() for d in data_v1])
        trs.to_yaml(fname)


# build groups
import_data.add_command(import_statement)

show.add_command(show_balance)
show.add_command(show_transactions)
show.add_command(show_invoices)

convert.add_command(convert_transactions)

add.add_command(add_invoices)

# build top levelcommands
cli.add_command(init)
cli.add_command(import_data)
cli.add_command(show)
cli.add_command(info)
cli.add_command(add)
cli.add_command(convert)


if __name__ == "__main__":  # note - name will be wimm.cli in case of terminal cmd

    PATH = list(Path(__file__).parents)[1] / 'tests/data'
else:
    PATH = wimm.get_settings()['path']
    if not PATH:
        echo("WARNING: environment variable WIMM_PATH is not set")
