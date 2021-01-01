#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core classes and functions
============================


Entities & accounts
--------------------

The system is built upon the concept of  *accounts* and 
*transactions*. 

An *account* is wehere the money goes to (or comes from) and 
can be a person, company or a generic destination like for example 'expenses.'

Subaccounts are used for grouping
and better organisation.

The dot `.` sign is used to denote an entity and its (sub)accounts

Example of an entity with a subaccount:
    
`Equity.bank.savings`



Transactions
--------------

Transaction define money flow. In its basic form it is a transfer from A to B.
A tranaction may be taxed (with a VAT for example)


"""
from collections import UserList, UserDict
import yaml
import wimm.utils as utils
import pandas as pd
from dataclasses import dataclass, asdict, fields, _MISSING_TYPE


def parse_account(s):
    """ parse entity and account string """

    return s.strip().split('.')


def load_data(name, db_path):
    """ load data from yaml """
    import wimm.structure as structure
    fcns = {'balance': load_start_balance,
            'transactions': Transactions.from_yaml,
            'invoices': Invoices.from_yaml}

    p = db_path / structure.files[name]
    assert p.exists(), f"File {p} not found"
    return fcns[name](p)


def load_start_balance(yaml_file):
    d = yaml.load(open(yaml_file), Loader=yaml.SafeLoader)
    return pd.Series(d)


def get_account(item):
    """ return account from an item. Can be a string or a dict """
    try:
        account = item['account']  # try value from dict
    except TypeError:
        account = item

    return account


def parse_bank_statement(self, statement_file, acct_name='Assets.bank', bank='ASN'):
    """
    parse bank statement

    Parameters
    ----------
    statement_file : string
        csv or other file to parse
    acct_name : string
        account name to use (from/to name)
    bank : string, optional
        Type of statement. The default is 'ASN'.

    Returns
    -------
    Transactions 

    """

    df = utils.read_bank_statement(statement_file, bank)
    records = df.to_dict(orient='records')

    data = []

    for r in records:

        # init data element
        d = {}
        # TODO : remove nested data
        if r['amount'] < 0:  # withdrawal
            d['amount'] = -r['amount']
            d['from'] = acct_name
            d['to'] = {'account': 'Ext.Unknown',
                       'name': r['name'], 'iban': r['iban_other']}
        else:
            d['amount'] = r['amount']
            d['from'] = {'account': 'Ext.Unknown',
                         'name': r['name'], 'iban': r['iban_other']}
            d['to'] = acct_name

        d['date'] = r['date']
        d['description'] = r['description']

        data.append(d)

    return Transactions(data)


def balance(transactions, start_balance=None, invoices=None, depth=None):
    """ calculate balance """

    accounts = transactions.process()
    
    if start_balance is not None:
        accounts = accounts.add(start_balance, fill_value=0)

    if invoices is not None:
        inv_acc  = invoices.to_accounts() # convert to series
        accounts = accounts.add(inv_acc, fill_value=0)
        
    names = accounts.index.to_list()

    if depth is None:
        return accounts
    else:
        return accounts.groupby(utils.names_to_labels(names, depth)).sum()


class ListPlus(UserList):
    """ base extensions for a list """

    def to_yaml(self, yaml_file=None, confirm=False):
        """ write to file or return string """

        data = [utils.to_dict(obj) for obj in self.data]

        if yaml_file:
            utils.save_yaml(yaml_file, data, ask_confirmation=confirm)

        return yaml.dump(data)

    @classmethod
    def from_yaml(cls, yaml_file):
        """ create class from a yaml file """

        data = yaml.load(open(yaml_file), Loader=yaml.SafeLoader)

        return cls(data)


class Transactions(ListPlus):
    """ transactons class, extension of a list """

    def process(self):
        """ return accounts and their balances """
        tr = pd.DataFrame.from_records(self.data)
        return tr.groupby(['to']).amount.sum().subtract(tr.groupby(['from']).amount.sum(), fill_value=0)



class Invoice(UserDict):
     
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        keys = ['id','amount','tax','date','from','to','description','attachment','due_date']
        vals = [None, 0.0, 0,  None, 'Uncategorized', 'Uncategorized', None, None]
        for k,v in zip(keys,vals):
            self.setdefault(k,v)
        

    def validate(self):

        utils.validate(self.data['id'], "IN([A-Z]{1}[0-9]{2}_[0-9]{3})")
        utils.validate(self.data['date'], "([0-9]{4}-[0-9]{2}-[0-9]{2})")

  
    def to_yaml(self):
        return yaml.dump(self.data, sort_keys=False)

    def rest_amount(self):
        return self.amount - self.amount_payed

    def transactions(self):
        """ return transactions corresponding to an invoice """
        
        keys = ['amount','date','from','to']
        vals = [self.data[key] for key in keys]
        out = [dict(zip(keys,vals))]
        
        
        # if self.data['tax'] > 0:
        #     out.append({'from':'Ext.Taxes', 'to':'MyCompany.tax.to_receive', 'amount':})
        
        return out
    # def __repr__(self):
    #     return f"Invoice {self['id']} {self.amount}"

 


class Invoices(ListPlus):

    def __init__(self, lst=[]):

        objects = []
        for d in lst:
            if isinstance(d, Invoice):
                objects.append(d)
            else:
                objects.append(Invoice(**d))

        super().__init__(objects)

    def get_by_id(self, id):
        """ get a invoice(s) by id 
        id may be a partial string, with a wildcard *. Example INS*
        """

        if id[-1] == '*':  # multiple matching
            pat = id[:-1]
            n = len(pat)
            matches = []
            for inv in self.data:
                if inv['id'][:n] == pat:
                    matches.append(inv)
            return Invoices(matches).get_sorted_by('id')

        else:
            for inv in self.data:  # single matching
                if inv['id'] == id:
                    return inv

        raise KeyError('id not found')

    def get_next_id(self, prefix):
        """ get next available invoice number for a prefix """

        try:
            id = self.get_by_id(prefix+'*')[-1]['id']
        except IndexError:  # prefix not found, make new one
            return f"{prefix}{utils.timestamp('%y')}_001"

        nr = int(id[-3:]) + 1
        return id[:-3] + '%03d' % nr

    def get_sorted_by(self, key, reverse=False):

        return sorted(self,
                      key=lambda x: x[key],
                      reverse=reverse)

    def to_df(self):
        """ convert to DataFrame """
        return pd.DataFrame.from_records(self.data)

    def to_accounts(self):
        """ convert to accounts, including taxes """
        df =self.to_df()
        acc = df.set_index('id')['amount'] # account series
        tax = pd.Series( [df.tax[df.tax>0].sum(),
                    df.tax[df.tax<0].sum()],
                    index=['tax.to_receive','tax.to_pay'])
        return pd.concat((acc,tax))