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
    
    s = 'Alice/bank/savings'
    res = core.parse_destination(s)
    
    assert res == ['Alice','bank','savings']