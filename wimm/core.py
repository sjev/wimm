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
import yaml

def parse_account(s):
    """ parse entity and account string """
    
    return s.strip().split('.')

class Accounts(dict):
    """ class for working with accounts """
         
    def sum(self):
        
        total = 0
        for k,v in self.items():
            total += v        
        return total
    
    def create(self,key):
        """ add account """
        self.__setitem__(key,0.0)
    
    def exists(self, key):
        """ check if account exists """
        return True if key in self.keys() else False
    
    @classmethod 
    def from_file(cls,yaml_file):
        """ create class from a yaml file """
        
        data = yaml.load(open(yaml_file), Loader=yaml.SafeLoader)
        
        accounts = {}
        for d in data:
            if isinstance(d,str):
                accounts[d] = 0.0
            elif isinstance(d,dict):
                accounts = {**accounts,**d}
            else:
                raise TypeError
            
        return cls(accounts)
                

class Transactions(list):
    """ transactons class, extension of a list """

    def apply(self, accounts, create_accounts=False):
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
            
            for account in [t['from'],t['to']]:
                if not accounts.exists(account):
                    if create_accounts:
                        accounts.create(account)
                    else:
                        raise ValueError(f'Account {account} does not exist')
            
            
            accounts[t['from']] -= t['amount']
            accounts[t['to']] += t['amount']

        
    @classmethod 
    def from_file(cls,yaml_file):
        """ create class from a yaml file """
        
        data = yaml.load(open(yaml_file), Loader=yaml.SafeLoader)
        return cls(data)
    