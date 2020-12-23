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
from collections import UserDict, UserList
import yaml
import wimm.utils as utils
import pandas as pd
from dataclasses import dataclass, asdict, is_dataclass

def parse_account(s):
    """ parse entity and account string """
    
    return s.strip().split('.')


def get_account(item):
    """ return account from an item. Can be a string or a dict """
    try:
        account = item['account'] # try value from dict
    except TypeError:
        account = item
        
    return account


class Entity:
    """ class holding accounts and transactions for a company or a person """
    
    def __init__(self, 
                 accounts_yaml = 'accounts.yaml',
                 transactions_yaml = 'transactions.yaml'):
        self.accounts = Accounts.from_yaml(accounts_yaml)
        self.transactions = Transactions.from_yaml(transactions_yaml)
        self.transactions.apply(self.accounts)
        
    def balance(self):
        """ calculate balance. Returns pd.Series """
        
        names = []
        values = []
        for k, acc in self.accounts.items():
            names.append(k)
            values.append(acc.value)
        return pd.Series(data=values,index=names)

    def __repr__(self):
        return f"Entity Accounts:{len(self.accounts)} Transactions:{len(self.transactions)}"
        
    
    

class Account:
    """ account is what holds money """
    
    def __init__(self, name, start_value = 0.0):
        self.name = name
        self.value = start_value
        
       
    def add(self, amount):
        self.value += amount
    
    def subtract(self, amount):
        self.value -= amount
        
    def __repr__(self):
        return f"{self.name}:{self.value:.2f}"
        
    def parse_bank_statement(self, statement_file, bank = 'ASN'):
        """
        parse bank statement

        Parameters
        ----------
        statement_file : string
            csv or other file to parse
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
            
            #init data element
            d = {}
            
            if r['amount'] < 0: # withdrawal
                d['amount'] = -r['amount']
                d['from'] = self.name
                d['to'] = {'account': 'Ext.Unknown', 'name':r['name'], 'iban':r['iban_other']}
            else:
                d['amount'] = r['amount']
                d['from'] = {'account': 'Ext.Unknown', 'name':r['name'], 'iban':r['iban_other']}
                d['to'] = self.name
            
            d['date'] = r['date']
            d['description'] = r['description']
                
            data.append(d)
        
        return Transactions(data)

class Accounts(UserDict):
    """ dictionary holding multiple accounts """
         
    def sum(self):
        
        total = 0
        for k,v in self.items():
            total += v.value        
        return total
    
    def create(self,name):
        """ add account """
        self.__setitem__(name,Account(name))
    
    def exists(self, key):
        """ check if account exists """
        return True if key in self.keys() else False
    
    def to_yaml(self, yaml_file):
        
        data_dict = {}
        for name, account in self.items():
            data_dict[name] = account.value
        
        utils.save_yaml(yaml_file, data_dict ,ask_confirmation=False)
      
    @classmethod
    def from_dict(cls, data_dict):
        
        data = {}
        for name,val in data_dict.items():
            data[name] = Account(name,val)
        
        return cls(data)    
    
    @classmethod 
    def from_yaml(cls,yaml_file):
        """ create class from a yaml file """
               
        return cls.from_dict(yaml.load(open(yaml_file), Loader=yaml.SafeLoader))


class ListPlus(UserList):
    """ base extensions for a list """
    
    
    
    def to_yaml(self, yaml_file=None):
        """ write to file or return string """
        
        
        data = [utils.to_dict(obj) for obj in self.data]
        
        if yaml_file:
            utils.save_yaml(yaml_file, data ,ask_confirmation=False)
     
        return yaml.dump(data)

        

    @classmethod 
    def from_yaml(cls,yaml_file):
        """ create class from a yaml file """
        
        data = yaml.load(open(yaml_file), Loader=yaml.SafeLoader)
        
        return cls(data)

class Transactions(ListPlus):
    """ transactons class, extension of a list """

    def apply(self, accounts, create_accounts=True):
        """
        apply transactions to accounts 

        Parameters
        ----------
        accounts : dict
            accounts and their values
        create_accounts : TYPE, optional
            automatically creaate accounts if these don't exist.
            raise exception otherwise

        Returns
        -------
        None.

        """
        
        for t in self:
            for data in [t['from'],t['to']]:
                account = get_account(data)
                if not accounts.exists(account):
                    if create_accounts:
                        accounts.create(account)
                    else:
                        raise ValueError(f'Account {account} does not exist')
            
            accounts[get_account(t['from'])].subtract(t['amount'])
            accounts[get_account(t['to'])].add(t['amount'])

    
    
@dataclass
class Invoice:
    number : int
    date : str
    amount : float
    prefix : str = 'INV' #  INR / INS
    sender : str = None
    due_date : str = None
    amount_payed : float = 25.0
    document : str = None
    
    def rest_amount(self):
        return self.amount - self.amount_payed
    
    @property
    def id(self):
        "string prefix XXX_nr"
        
        return f"{self.prefix}_{self.number:03d}"
        
    def __repr__(self):
        return "Invoice " + self.name()

    def to_dict(self):
        return asdict(self)

class Invoices(ListPlus):
    
      def __init__(self, lst):
        
        objects = []
        for d in lst:
            if isinstance(d, Invoice):
                objects.append(d)
            else:
                objects.append(Invoice(**d))

        super().__init__(objects)
    
      def get_by_id(self, id):
        """ get invoice from id """
        for inv in self.data:
            if inv.id == id:
                return inv
        
        raise KeyError('id not found')         
   
      def get_sorted_by(self, key, reverse = False):
          
          return sorted(self,
                        key = lambda x: getattr(x, key),
                        reverse = reverse)
