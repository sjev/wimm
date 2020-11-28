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


class Accounts(UserDict):
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
    
    def to_yaml(self, yaml_file):
        utils.save_yaml(yaml_file, self.data ,ask_confirmation=False)
        
    
    @classmethod 
    def from_file(cls,yaml_file):
        """ create class from a yaml file """
        data = yaml.load(open(yaml_file), Loader=yaml.SafeLoader)
        return cls(data)



class Transactions(UserList):
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
            for data in [t['from'],t['to']]:
                account = get_account(data)
                if not accounts.exists(account):
                    if create_accounts:
                        accounts.create(account)
                    else:
                        raise ValueError(f'Account {account} does not exist')
            
            accounts[get_account(t['from'])] -= t['amount']
            accounts[get_account(t['to'])] += t['amount']

    def to_yaml(self, yaml_file=None):
        """ write to file or return string """
        
        if yaml_file:
            utils.save_yaml(yaml_file, self.data ,ask_confirmation=False)
     
        return yaml.dump(self.data)

        
    @classmethod 
    def from_bank_statement(cls, statement_file, statement_type = 'ASN'):
        """
        parse bank statement

        Parameters
        ----------
        statement_file : string
            csv or other file to parse
        statement_type : string, optional
            Type of statement. The default is 'ASN'.

        Returns
        -------
        Statements

        """
        
        if statement_type == 'ASN':
            df = utils.read_csv_ASN(statement_file)
            data = df.to_dict(orient='records')
            
            # flip directions for withdrawals
            for d in data:
                if d['amount'] < 0:
                    d['amount'] = -d['amount']
                    d['from'] = 'Assets.Bank.ASN'
                    d['to'] = d.pop('name')
                else:
                    d['to'] = 'Assets.Bank.ASN'
                    d['from'] = d.pop('name')
            
            
            return cls(data)
        else:
            raise ValueError(f'Unknown statement type: {statement_type}')

    @classmethod 
    def from_file(cls,yaml_file):
        """ create class from a yaml file """
        
        data = yaml.load(open(yaml_file), Loader=yaml.SafeLoader)
        return cls(data)
    