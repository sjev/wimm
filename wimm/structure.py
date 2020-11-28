#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Definitions for default directories, files etc.
Used for initialization

"""

settings = {'doc_nr': '%i_%03d',
            'invoices': {'received':  {'prefix':'INR', 'folder':'invoices_received'},
                       'sent':      {'prefix':'INS', 'folder':'invoices_sent'}}
            }



folders = [settings['invoices']['sent']['folder'],
           settings['invoices']['received']['folder']]


_account_names = ['Assets', 
                  'Assets.bank',
                  'Liabilities',
                  'External.clients',
                  'External.suppliers',
                  'External']

accounts = dict(zip(_account_names, len(_account_names)*[0.0]))

transactions = [ {'timestamp' : '2020-01-01',
               'from' : 'Income',
               'to' : 'Assets.bank',
               'amount' : 1000.0,
               'description' : 'Customer paid invoice'},
                {'timestamp' : '2020-01-02',
               'from' : 'Assets.bank',
               'to' : 'Expenses',
               'amount' : 50.0,
               'description' : 'bought some pens',
               'category': 'office supplies'   },
                {'timestamp' : '2020-01-03',
               'from' : 'Liabilities',
               'to' : 'Assets.bank',
               'amount' : 150.0,
               'description' : 'Borrowed some money from Bob'    } ]