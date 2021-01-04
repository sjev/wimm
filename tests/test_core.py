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

import wimm
from wimm import core
import wimm.structure as structure
import wimm.utils as utils

wimm.settings = structure.settings

# create temp dir
if not os.path.exists('tmp'):
    os.mkdir('tmp')

def test_parser():
    
    s = 'Equity.bank.savings'
    res = core.parse_account(s)
    
    assert res == ['Equity','bank','savings']
    
def test_transaction():
    
    tr = core.Transaction.from_dict(structure.transaction)    

    assert tr.date == '2020-01-01'
    assert tr.transfers['CCC'] == -2
    
    y = tr.to_yaml()
    print(y)
    
def test_transaction_v1():

    d_v1 = structure.v1_transactions[0]

    tr = core.Transaction.from_v1(d_v1)
    assert tr.date == d_v1['date']
    assert tr.transfers['Ext.Bob'] == -1000
    assert tr.transfers['Assets.Bank'] == 1000
    assert tr.description == 'Customer paid invoice'
    
    # one without description
    d_v1 = structure.v1_transactions[1]
    tr = core.Transaction.from_v1(d_v1)
    
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

#@pytest.mark.skip   
def test_invoice_id():
    """ check if invoice id is correct,
    should be XXX.DD_DDD """
    
    inv = core.Invoice(id='INR20_0001', date="2020-01-01", amount=10)
    inv.validate()
    
    
    with pytest.raises(ValueError):
        inv = core.Invoice(id='INR20-0001', date="2020-01-01", amount=10)
        inv.validate()
        
        
    
def test_invoices_functions():
    
    invoices = structure.invoices()
    
    inv = invoices.get_by_id('INR00_000')
    assert inv['to'] == 'Microsoft'
    
    inv = invoices.get_sorted_by('id', reverse=True)[0]
    assert inv['description'] == 'bbb'
    
def test_invoices_aux():
    """ test auxilary functions """
    
    fname = 'tmp/invoices.yaml'
    invoices = core.Invoices.from_yaml(fname)
    
    res = invoices.get_by_id('INR00*')
    assert len(res) == 1
    assert res[0]['id'] == "INR00_000"
    
    res = invoices.get_by_id('INR21*')
    assert len(res) == 2
    
    assert res[-1]['id'] == 'INR21_003'
    
    year = utils.timestamp('%y')
    assert invoices.get_next_id('FOO') == f"FOO{year}_001"
    
    assert invoices.get_next_id('INR') == "INR21_004"
    assert invoices.get_next_id('INS') == "INS20_002"
    
    
def test_invoice_accounts():
    """ test correct formatting for 'from' and 'to' invoice names """
    
    
    inv = core.Invoice(id="INR_000", amount=100, tax = 10, ext_name = 'CorpX')
    inv.set_accounts()
    trs = inv._transactions()
    
    tr = trs[0]
    assert tr['to'] == 'Out.CorpX'
    assert tr['from'] == 'MyCompany.INR.INR_000'
   
    tr = trs[1]
    assert tr['to'] == 'MyCompany.tax.to_receive'
    assert tr['from'] == 'Taxes'
    
    
    # new style
    tr = inv.transaction()
    assert tr.transfers['MyCompany.tax.to_receive'] == 10
    assert tr.transfers['MyCompany.INR.INR_000'] == - 100
    
    #----------------------
    prefix = 'FOO'
    params = { 'invoice_id':'INV_000', 'ext_name':'ext_name' }
    
    res = utils.invoice_accounts(prefix, params)
    assert res == {'from':'Uncategorized', 'to':'Uncategorized'}
    
    prefix = 'INR'
    res = utils.invoice_accounts(prefix, params)
    
    
    prefix = 'INS'
    res = utils.invoice_accounts(prefix, params)
    
    assert res == {'from':'In.ext_name',
                   'to': 'MyCompany.INS.INV_000'}
    
def test_invoice_transaction():
    
    # test invoice without tax
    d = {'id':'DEC00_000', 'amount': 100, 'from':'Foo', 'to':'Bar','tax':0} 
                       
    inv = core.Invoice(d)
    tr = inv.transaction()
    print(tr)