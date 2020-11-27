#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Definitions for default directories, files etc.
Used for initialization

"""

folders = ['invoices_received','invoices_sent']


_account_names = ['Assets', 
                  'Assets.bank',
                  'Liabilities',
                  'Expenses',
                  'Income']

accounts = dict(zip(_account_names, len(_account_names)*[0.0]))