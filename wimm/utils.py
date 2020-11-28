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

def timestamp():
    t=dt.datetime.now()
    return t.strftime("%Y-%m-%d_%H%M")

def date():
    return dt.datetime.now().strftime("%Y-%m-%d")

def save_yaml(yaml_file, data, ask_confirmation=True):
    """ write data to file, optionally ask for overwrite confirmation """
    
    
    if os.path.exists(yaml_file) and ask_confirmation:
        overwrite = click.confirm(f'Overwrite {yaml_file}?')
        if not overwrite:
            return
    
    with open(yaml_file,'w') as f:
        yaml.dump(data, f)


class SafeLineLoader(SafeLoader):
    def construct_mapping(self, node, deep=False):
        mapping = super(SafeLineLoader, self).construct_mapping(node, deep=deep)
        # Add 1 so line numbering starts at 1
        mapping['__line__'] = node.start_mark.line + 1
        return mapping
   
def df_to_yaml(df):
    """ conert DataFrame to yaml string """
    
    d = df.to_dict(orient='records')
    return yaml.dump(d)

def read_csv_ASN(csv_file):
    """
    load ASN bank csv file.

    Parameters
    ----------
    csv_file : string
        statement in csv format

    Returns
    -------
    DataFrame

    """
    header = ['Boekingsdatum','Opdrachtgeversrekening','Tegenrekeningnummer',
              'Naam tegenrekening','Adres','Postcode','Plaats','Valutasoort rekening',
              'Saldo voor mutatie','Valutasoort mutatie','Bedrag','Jounaaldatum','Valutadatum',
              'Interne transactiecode', 'Globale transactiecode', 'Volgnummer','Betalingskenmerk',
              'Omschrijving','Afschriftnummer']
    
    mapping = {'Boekingsdatum':'timestamp', 'Naam tegenrekening':'name','Bedrag':'amount','Omschrijving':'description'}
    
    df = pd.read_csv(csv_file,names=header)
    df.rename(mapping,axis=1,inplace=True)

    relevant_cols = [v for k,v in mapping.items()]
    
    df = df[relevant_cols]
   
    
    return df