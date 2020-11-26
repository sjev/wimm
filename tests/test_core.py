#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test core functionality using pytest.
This file is being used during module development.
@author: jev
"""

# add wimm to path
import os
import sys
from pathlib import Path
cwd = Path(os.getcwd())
sys.path.insert(0, cwd.parent.as_posix())  

from wimm import core

def test_parser():
    
    s = 'Equity.bank.savings'
    res = core.parse_account(s)
    
    assert res == ['Equity','bank','savings']
    
def test_create_accounts():
    
    # --- create with dict
    d =  {'acc1':50.0,'acc2':100.0}
    
    acc = core.Accounts(d)
    
    assert acc['acc1'] == 50
    assert acc['acc2'] == 100
    assert acc.sum() == 150
    
def test_load_accounts():    

    # --- cretate from file
    acc = core.Accounts.from_file('accounts.yaml')
    assert acc['Assets'] == 0
    assert acc['Assets.bank'] == 1000.0