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
    
def test_accounts():
    
    # --- create with dict
    d =  {'acc1':0.0,'acc2':100.0}
    
    acc = core.Accounts(d)
    
    assert acc.accounts['acc1'] == 0
    assert acc.accounts['acc2'] == 100
    
    # --- cretate from file
    acc = core.Accounts.from_file('accounts.yaml')
    assert acc.accounts['Assets'] == 0
    assert acc.accounts['Assets.bank'] == 1000.0