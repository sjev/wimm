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


account_names = ['Assets', 
                  'Assets.Bank',
                  'Liabilities',
                  'Ext.Clients',
                  'Ext.Suppliers',
                  'Ext']

accounts = dict(zip(account_names, len(account_names)*[0.0]))

transactions = [ {'date' : '2020-01-01',
               'from' : {'account':'Ext.Bob','name':'Bob','iban':12345},
               'to' : 'Assets.bank',
               'amount' : 1000.0,
               'description' : 'Customer paid invoice'},
                
                {'date' : '2020-01-02',
               'from' : 'Assets.bank',
               'to' : 'Expenses',
               'amount' : 50.0,
               'description' : 'bought some pens',
               'category': 'office supplies'   },
                
                {'date' : '2020-01-03',
               'from' : 'Liabilities',
               'to' : 'Assets.bank',
               'amount' : 150.0,
               'description' : 'Borrowed some money from Bob'    } ]


#%% invoice definition



def _make_test_invoices():
    from wimm.core import Invoice, Invoices
    # create a couple of invoices for testing
    dates = ['2020-01-01','2020-02-01','2020-02-10','2020-12-05']
    #due_dates = ['2020-01-30','2020-02-15','2020-03-20','2021-01-05']
    amounts = [70,50,25,1000]
    senders = ['Bob','Bob','Alice','Alice']
    objects = [Invoice(*vals) for vals in zip(range(len(dates)),dates,amounts,senders)]
    return Invoices(objects)
    
invoices = _make_test_invoices()
