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


def test_parser():
    
    s = 'Equity.bank.savings'
    res = core.parse_account(s)
    
    assert res == ['Equity','bank','savings']
    
def test_create_accounts():
    
    # --- create with dict
    
    acc = core.Accounts(structure.accounts)
    
    assert acc.exists('Assets') == True
    assert acc.exists('Assets.bank') == True
    assert acc.exists('foo') == False
    
    acc.create('foo')
    assert acc.exists('foo') == True
    
    
    acc['Assets'] = 50
    acc['External'] = 100
    
    assert acc['Assets'] == 50
    assert acc['External'] == 100
    assert acc.sum() == 150
    
def test_load_accounts():    

    # --- cretate from file
    acc = core.Accounts.from_file('accounts.yaml')
    assert acc['Assets'] == 0
    assert acc['Assets.bank'] == 1000.0
    
def test_load_transactions():
    
    t = core.Transactions.from_file('transactions.yaml')
    assert len(t) == 3

def test_transactions():
    """ test applying transactions to accounts """
    
    accounts = core.Accounts()
    transactions = core.Transactions.from_file('transactions.yaml')
    transactions.apply(accounts, create_accounts=True)
    
    assert accounts.sum() == 0
     
    print(accounts)
    
    