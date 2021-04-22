#!/usr/bin/env python
"""
    Abstract class templates for data importers

"""

from abc import ABC, abstractmethod
from wimm.core import Transactions


class Importer(ABC):

    def __init__(self) -> None:
        self.df = None

    @abstractmethod
    def transactions(self, acct_name='Assets.Bank') -> Transactions:
        """ return Transactions """
