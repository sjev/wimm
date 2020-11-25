#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core classes and functions
============================


Entities & accounts
--------------------

The system is built upon the concept of *entities*, *accounts* and 
*transactions*. 

An *entity* is wehere the money goes to (or comes from) and 
can be a person, company or a generic destination like for example 'expenses.'

An *account* holds money within an entity. Subaccounts are used for grouping
and better organisation.

The `:` sign is used to denote an entity and its (sub)accounts

Example of an entity with a subaccount:
    
`Alice:bank:savings`

Transactions
--------------

Transaction define money flow. In its basic form it is a transfer from A to B.
A tranaction may be taxed (with a VAT for example)


"""


def parse_destination(s):
    """ parse entity and account string """
    
    return s.strip().split(':')


