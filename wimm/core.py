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
from typing import Tuple
import yaml
import wimm.utils as utils
import pandas as pd
import wimm
from dataclasses import dataclass, asdict


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


def balance(transactions, start_balance=None, invoices=None, depth=None):
    """ calculate balance """

    accounts = transactions.process()

    if start_balance is not None:
        accounts = accounts.add(start_balance, fill_value=0)

    # if invoices is not None:
    #     inv_acc  = invoices.to_accounts() # convert to series
    #     accounts = accounts.add(inv_acc, fill_value=0)

    names = accounts.index.to_list()

    if depth is None:
        return accounts
    else:
        return accounts.groupby(utils.names_to_labels(names, depth)).sum()


class ListPlus(UserList):
    """ base extensions for a list """

    def __init__(self,  *args, cls_factory=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.cls_factory = cls_factory
        if self.cls_factory is not None:
            self.data = [self.cls_factory(**d) for d in self.data]

    def to_yaml(self, yaml_file=None, confirm=False):
        """ write to file or return string """

        data = [utils.to_dict(obj) for obj in self.data]

        if yaml_file:
            utils.save_yaml(yaml_file, data, ask_confirmation=confirm)

        return yaml.dump(data, sort_keys=False)

    @classmethod
    def from_yaml(cls, yaml_file):
        """ create class from a yaml file """

        data = yaml.load(open(yaml_file), Loader=yaml.SafeLoader)

        # if cls.cls_factory is None:
        return cls(data)
        # else:
        #    return cls( [cls.cls_factory.from_dict(d) for d in data])


class Transaction(UserDict):
    date: str
    description: str
    transfers: dict

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        defaults = [('date', None),
                    ('description', ''),
                    ('transfers', {})]

        for k, v in defaults:
            self.setdefault(k, v)

        self._check_totals()

    def _check_totals(self):

        total = 0
        missing = None
        for k, v in self.transfers.items():
            if v is None:
                if missing is None:
                    missing = k
                else:
                    raise ValueError('More than one entry is missing')
            else:
                total += v

        if missing:
            self.transfers[missing] = -total

    def __getattr__(self, name):
        if name in self.data:
            return self.data[name]
        else:
            raise AttributeError(name)

    def to_records(self):
        """ convert to simple account operations """
        return [{'date': self.date, 'account': acct, 'amount': amount} for acct, amount in self.transfers.items()]

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    def to_dict(self, compact=False):
        """ save to dict (dropping None values if `compact` is True) """
        if compact:
            return {k: v for k, v in self.items() if v is not None}
        else:
            return self

    def to_yaml(self, compact=True):
        return yaml.dump([self.to_dict(compact)], sort_keys=False)

    @classmethod
    def from_v1(cls, tr):
        """ create from old (v1) dict type """

        d = {'date': tr['date'],
             'description': tr.get('description', None),
             'transfers': {tr['from']: -tr['amount'],
                           tr['to']: tr['amount']}
             }
        return cls(**d)


class Transactions(ListPlus):
    """ transactons class, extension of a list """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, cls_factory=Transaction, **kwargs)

    def to_records(self):
        for tr in self.data:
            for rec in tr.to_records():
                yield rec

    def process(self):
        """ return accounts and their balances """
        return self.to_df().groupby(['account']).sum()['amount']

    def to_df(self, date_range: Tuple = None) -> pd.DataFrame:
        """ transactions as DataFrame """

        df = pd.DataFrame.from_records(self.to_records())
        df['date'] = pd.to_datetime(df['date'])

        if date_range is None:
            return df

        # select dates
        mask = (df.date >= date_range[0]) & (df.date < date_range[1])
        return df[mask]


class Invoice(UserDict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        keys = ['id', 'amount', 'tax', 'date', 'from', 'to',
                'description', 'attachment', 'due_date', 'ext_name']
        vals = ['INV00_000', 0.0, None,  None, 'Uncategorized',
                'Uncategorized', None, None, None, 'ext_company_name']
        for k, v in zip(keys, vals):
            self.setdefault(k, v)

    def __getattr__(self, name):
        if name in self.data:
            return self.data[name]
        else:
            raise AttributeError(name)

    @property
    def prefix(self):
        return self['id'][:3]

    def validate(self):

        utils.validate(self.data['id'], "IN([A-Z]{1}[0-9]{2}_[0-9]{3})")
        utils.validate(self.data['date'], "([0-9]{4}-[0-9]{2}-[0-9]{2})")

    def set_accounts(self, accounts=None):

        if accounts is None:
            params = {'invoice_id': self.id, 'ext_name':  self.ext_name}
            accounts = utils.invoice_accounts(
                self.prefix, params, 'invoice_accounts')

        self.data['from'] = accounts['from']
        self.data['to'] = accounts['to']

    def transaction(self):
        """ single transaction for an invoice """

        # TODO: refactor. Ok, it's late and I don't have time to rewrite all the old code.
        # so  I'll just gently wrap it in a new function.
        trs = [Transaction.from_v1(tr) for tr in self._transactions()]
        tr = trs[0]
        if len(trs) == 2:
            tr.transfers = {**tr.transfers, **trs[1].transfers}
        return tr

    def _transactions(self):
        """ return ivoice transactions as a list, `old style` transactions """

        trs = Transactions()

        # ----- invoice transaction

        trs.append({'date': self.date,
                    'description': 'Invoice '+self.id,
                    'amount': self.amount,
                    'from': self['from'],
                    'to': self['to']})

        # ----- tax transaction
        if self.tax:
            params = {'invoice_id': self.id, 'ext_name':  self.ext_name}
            accounts = utils.invoice_accounts(
                self.prefix, params, 'tax_accounts')

            trs.append({'date': self.date,
                        'description': 'Tax for invoice '+self.id,
                        'amount': self.tax,
                        **accounts})

        return trs

    def to_yaml(self):
        return yaml.dump(self.data, sort_keys=False)

    def rest_amount(self):
        return self.amount - self.amount_payed

    def __repr__(self):
        return f"{self.id} amount:{self.amount:<10}  {self['from']} -->  {self.to}"


class Invoices(ListPlus):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, cls_factory=Invoice, **kwargs)

    def get_by_id(self, invoice_id):
        """ get a invoice(s) by id
        id may be a partial string, with a wildcard *. Example INS*
        """

        if invoice_id[-1] == '*':  # multiple matching
            pat = invoice_id[:-1]
            n = len(pat)
            matches = []
            for inv in self.data:
                if inv['id'][:n] == pat:
                    matches.append(inv)
            return Invoices(matches).get_sorted_by('id')

        else:
            for inv in self.data:  # single matching
                if inv['id'] == invoice_id:
                    return inv

        raise KeyError('id not found')

    def get_next_id(self, prefix):
        """ get next available invoice number for a prefix """

        try:
            invoice_id = self.get_by_id(prefix+'*')[-1]['id']
        except IndexError:  # prefix not found, make new one
            return f"{prefix}{utils.timestamp('%y')}_001"

        nr = int(invoice_id[-3:]) + 1
        return invoice_id[:-3] + '%03d' % nr

    def get_sorted_by(self, key, reverse=False):

        return sorted(self,
                      key=lambda x: x[key],
                      reverse=reverse)

    def to_df(self):
        """ convert to DataFrame """
        return pd.DataFrame.from_records(self.data)

    def to_transactions(self):
        """ convert to transactions """

        trs = Transactions()
        for inv in self.data:
            trs += inv.transactions()

        return trs

    def to_accounts(self):
        """ convert to accounts, including taxes """
        df = self.to_df()
        acc = df.set_index('id')['amount']  # account series
        tax = pd.Series([df.tax[df.tax > 0].sum(),
                         df.tax[df.tax < 0].sum()],
                        index=['tax.to_receive', 'tax.to_pay'])
        return pd.concat((acc, tax))
