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

class Accounts:
    """ class for working with accounts """
    
    def __init__(self, accounts):
        """
        Parameters
        ----------
        accounts : dict
            definition in in form of {'account_name':value}

        Returns
        -------
        None.

        """
        self.accounts = accounts
        
    
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
                
        
