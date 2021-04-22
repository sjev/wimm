#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions for importing bank statemens

@author: jev
"""
from wimm import DATE_FMT
import pandas as pd
from wimm.core import Transactions


def clean_str(s):
    """ replace unwanted characters"""
    return s.replace(" ", "_").replace(".", "").strip()


def knab_import(csv_file, account="Assets.Bank.KNAB"):
    """ import csv file from KNAB bank. Return transaction records """

    def fcn_from(row):
        return ('Ext.'+clean_str(row['Tegenrekeninghouder'])) if row['CreditDebet'] == 'C' else 'Assets.Bank.KNAB'

    def fcn_to(row):
        return (account) if row['CreditDebet'] == 'C' else 'Uncategorized'

    df = pd.read_csv(csv_file, sep=';', header=1, parse_dates=[
                     'Transactiedatum'], decimal=',')

    # column name conversions
    tgt_cols = ['amount', 'date', 'description']
    src_cols = ['Bedrag', 'Transactiedatum', 'Omschrijving']

    # create transactions
    # extract cols, rename
    tr = df[src_cols].rename(dict(zip(src_cols, tgt_cols)), axis=1)
    tr['from'] = df.apply(fcn_from, axis=1)
    tr['to'] = df.apply(fcn_to, axis=1)
    tr.date = tr.date.apply(lambda x: x.strftime(DATE_FMT))

    return Transactions(tr.to_dict(orient='records'))
