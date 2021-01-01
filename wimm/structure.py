#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Definitions for default directories, files etc.
Used for initialization and testing

"""



settings = {'doc_nr': '%i_%03d',
            'company_name': 'MyCompany',
            'tax_rate': 0.21}


files = {'balance':'balance.yaml',
         'transactions':'transactions.yaml',
         'settings':'settings.yaml',
         'invoices':'invoices.yaml',
         'hashes': '.wimm/hashes'}

folders = {'INS':'invoices', 
           'INR':'invoices',
           'WIMM':'.wimm'}


account_names = ['Assets', 
                  'Assets.Bank',
                  'Liabilities']

accounts = dict(zip(account_names, len(account_names)*[0.0]))

transactions = [ {'date' : '2020-01-01',
               'from' : 'Ext.Bob',
               'to' : 'Assets.Bank',
               'amount' : 1000.0,
               'description' : 'Customer paid invoice'},
                
                {'date' : '2020-01-02',
               'from' : 'Assets.Bank',
               'to' : 'Expenses',
               'amount' : 50.0,
               'description' : 'bought some pens',
               'category': 'office supplies'   },
                
                {'date' : '2020-01-03',
               'from' : 'Liabilities',
               'to' : 'Assets.Bank',
               'amount' : 150.0,
               'description' : 'Borrowed some money from Bob'    } ]


#%% invoice definition



def invoices():
    from wimm.core import Invoice, Invoices
    # create a couple of invoices for testing
    ids = ['INR00_000','INR20_001','INS20_001','INR21_001','INR21_003']
    dates = ['2000-12-31','2020-01-01','2020-02-01','2020-02-10','2020-12-05']
    #due_dates = ['2020-01-30','2020-02-15','2020-03-20','2021-01-05']
    amounts = [0, 70,50,25,1000]
    taxes = [0,10,20,4.3,12.0]
    senders = ['Microsoft','Bob','Bob','Alice','Alice']
    descriptions = ['dummy invoice', 'aaa', 'bbb', 'ccc', 'ddd']
    objects = [Invoice(*vals) for vals in zip(ids,dates,amounts,taxes,senders,descriptions)]
    return Invoices(objects)
    

