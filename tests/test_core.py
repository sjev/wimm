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

# create temp dir
if not os.path.exists('tmp'):
    os.mkdir('tmp')

def test_parser():
    
    s = 'Equity.bank.savings'
    res = core.parse_account(s)
    
    assert res == ['Equity','bank','savings']
    

    
    
def test_create_accounts():
    
    # --- create with dict
    
    acc = core.Accounts.from_dict(structure.accounts)
    
    for name in structure.account_names:
        assert acc.exists(name) 
        
    assert acc.exists('foo') == False
    
    acc.create('foo')
    assert acc.exists('foo') == True
    
    acc['Assets'].value = 150.0
    
    assert acc.sum() == 150
  
def test_accounts_roundtrip():    

    accounts = core.Accounts.from_dict(structure.accounts)
    
    
    accounts['Assets.Bank'].value = 100
    assert accounts['Assets.Bank'].value == 100.0
    accounts.to_yaml('accounts.yaml')


    # --- cretate from file
    acc = core.Accounts.from_yaml('accounts.yaml')
    for k in accounts.keys():
        assert acc[k].value == accounts[k].value
    
def test_transactions_roundtrip():
    
    core.Transactions(structure.transactions).to_yaml('transactions.yaml')
    
    transactions = core.Transactions.from_yaml('transactions.yaml')
    
    for i,t in enumerate(structure.transactions):
        transactions[i] = t

def test_transactions():
    """ test applying transactions to accounts """
    
    accounts = core.Accounts()
    transactions = core.Transactions.from_yaml('transactions.yaml')
    transactions.apply(accounts, create_accounts=True)
    
    assert accounts.sum() == 0
     
    print(accounts)
    
    