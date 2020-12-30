#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test core functionality using pytest.
This file is being used during module development.
@author: jev
"""
import pytest
# add wimm to path
import os
import sys
from pathlib import Path
cwd = Path(os.getcwd())
sys.path.insert(0, cwd.parent.as_posix())  

from wimm import core
import wimm.structure as structure
import wimm.utils as utils

# create temp dir
if not os.path.exists('tmp'):
    os.mkdir('tmp')

def test_parser():
    
    s = 'Equity.bank.savings'
    res = core.parse_account(s)
    
    assert res == ['Equity','bank','savings']
    

    
    

    
def test_transactions_roundtrip():
    
    core.Transactions(structure.transactions).to_yaml('transactions.yaml')
    
    transactions = core.Transactions.from_yaml('transactions.yaml')
    
    for i,t in enumerate(structure.transactions):
        transactions[i] = t

def test_transactions():
    """ test applying transactions to accounts """
    
    #accounts = core.Accounts()
    transactions = core.Transactions.from_yaml('transactions.yaml')
    accounts = transactions.process()
    
    assert accounts.sum() == 0
     
    print(accounts)
    
def test_invoices_roundtrip():
    
    invoices = structure.invoices()
    
    fname = 'tmp/invoices.yaml'
    invoices.to_yaml(fname)
    
    invoices1 = core.Invoices.from_yaml(fname)
    
    assert invoices == invoices1
    
def test_invoice_id():
    """ check if invoice id is correct,
    should be XXX.DD_DDD """
    
    _ = core.Invoice('INR.20_0001', "2020-01-01", 10)
    
    with pytest.raises(ValueError):
        _ = core.Invoice('INR.20-0001', "2020-01-01", 10)
    
    
def test_invoices_functions():
    
    invoices = structure.invoices()
    
    inv = invoices.get_by_id('INR.00_000')
    assert inv.sender == 'Microsoft'
    
    inv = invoices.get_sorted_by('id', reverse=True)[0]
    assert inv.description == 'bbb'
    
def test_invoices_aux():
    """ test auxilary functions """
    
    fname = 'tmp/invoices.yaml'
    invoices = core.Invoices.from_yaml(fname)
    
    res = invoices.get_by_id('INR.00*')
    assert len(res) == 1
    assert res[0].id == "INR.00_000"
    
    res = invoices.get_by_id('INR.21*')
    assert len(res) == 2
    
    assert res[-1].id == 'INR.21_003'
    
    year = utils.timestamp('%y')
    assert invoices.get_next_id('FOO') == f"FOO{year}_001"
    
    assert invoices.get_next_id('INR') == "INR.21_004"
    assert invoices.get_next_id('INS') == "INS.20_002"