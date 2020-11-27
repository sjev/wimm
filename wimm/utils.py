#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
utility functions
"""
import datetime as dt
from yaml.loader import SafeLoader

def timestamp():
    t=dt.datetime.now()
    return t.strftime("%Y-%m-%d_%H%M")

def date():
    return dt.datetime.now().strftime("%Y-%m-%d")


class SafeLineLoader(SafeLoader):
    def construct_mapping(self, node, deep=False):
        mapping = super(SafeLineLoader, self).construct_mapping(node, deep=deep)
        # Add 1 so line numbering starts at 1
        mapping['__line__'] = node.start_mark.line + 1
        return mapping