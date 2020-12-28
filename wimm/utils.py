#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
utility functions
"""
import datetime as dt
from yaml.loader import SafeLoader
import click
import yaml
import os
import pandas as pd
from pathlib import Path
from dataclasses import asdict, is_dataclass
import re


def tax(amount, rate=0.21):
    return -round(amount-amount/(1+rate), 2)


def dialog(data_in):
    """
    Interactive click dialog.

    Parameters
    ----------
    data_in : dict
        field names and their defaults in form {field:default_val}

    Returns
    -------
    dict

    """

    data_out = {}
    for key, val in data_in.items():
        new_val = click.prompt(key, default=val)
        data_out[key] = new_val

    return data_out


def get_path():
    """ get path of database directory """

    var = 'WIMM_PATH'
    val = os.getenv(var)

    if not val:
        print(f"environment variable {var} not found. ")
        import sys
        sys.exit()

    return Path(val)


def validate(s, regex):
    """ validates a string against regular expression """

    pattern = re.compile(regex)
    res = pattern.match(s)
    if not res:
        raise ValueError(f"{s} is not valid")


def to_dict(obj):
    """ convert object to dict """
    if isinstance(obj, dict):
        return obj
    elif is_dataclass(obj):
        return asdict(obj)
    else:
        return dict(obj)


def timestamp(fmt="%Y-%m-%d_%H%M", offset_days=0):
    t = dt.datetime.now() + dt.timedelta(days=offset_days)
    return t.strftime(fmt)


def date(offset=0):
    return timestamp("%Y-%m-%d", offset)


def save_yaml(yaml_file, data, ask_confirmation=True):
    """ write data to file, optionally ask for overwrite confirmation """

    if os.path.exists(yaml_file) and ask_confirmation:
        overwrite = click.confirm(f'Overwrite {yaml_file}?')
        if not overwrite:
            return

    with open(yaml_file, 'w') as f:
        yaml.dump(data, f)


def get_data_mappings(yaml_file='data_mappings.yaml'):
    """ load data conversion definintions """

    p = Path(yaml_file)
    if not p.is_absolute():
        p = Path(__file__).absolute().parent / p

    data = yaml.load(p.open('r'), Loader=SafeLoader)
    return data


class SafeLineLoader(SafeLoader):
    def construct_mapping(self, node, deep=False):
        mapping = super(SafeLineLoader, self).construct_mapping(
            node, deep=deep)
        # Add 1 so line numbering starts at 1
        mapping['__line__'] = node.start_mark.line + 1
        return mapping


def df_to_yaml(df):
    """ conert DataFrame to yaml string """

    d = df.to_dict(orient='records')
    return yaml.dump(d)


def read_bank_statement(csv_file, bank='ASN'):
    """
    load bank statement csv file.
    The transactions returned are relative to the bank account.

    Parameters
    ----------
    csv_file : string
        statement in csv format

    Returns
    -------
    DataFrame

    """

    mappings = get_data_mappings()

    if bank not in mappings.keys():
        raise ValueError(f'No data mapping present for bank: {bank}')

    header = mappings[bank]['header']
    mapping = mappings[bank]['mapping']

    df = pd.read_csv(csv_file, names=header)
    df.rename(mapping, axis=1, inplace=True)

    relevant_cols = [v for k, v in mapping.items()]

    df = df[relevant_cols]

    return df


def md5(path):
    """ calculate MD5 checksum may provide a dir or a file"""
    import hashlib

    def hash_file(p):
        with p.open('rb') as fid:
            hasher = hashlib.md5()
            hasher.update(fid.read())
            hsh = hasher.hexdigest()

        return hsh

    if path.is_dir():
        hashes = []
        for f in path.glob('*'):
            if f.is_file():
                hashes.append(hash_file(f))
        return hashes

    elif path.is_file():
        return [hash_file(path)]

    else:
        raise ValueError('provide path to file or dir')


class Hasher:
    """ class to manage file hashes 
    hashes are stored as  hash per line

    """

    def __init__(self, data_file):

        self.data_file = Path(data_file)

        if self.data_file.exists():
            with self.data_file.open('r') as fid:
                lines = fid.readlines()
            
            
            self.hashes = [l.strip() for l in lines]
        else:
            self.hashes = []
            
    def add(self, path):
        """ add hashes of a file or path """
        
        hashes = md5(path)
        with self.data_file.open('a') as f:
            for l in hashes:
                f.write(l+'\n')

    def delete_hashes(self):
       """ clear all hashes """
       self.hashes = []
       if self.data_file.exists():
           self.data_file.unlink()
       
       