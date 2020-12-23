#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 23 13:26:41 2020

@author: jev
"""

from flask_table import Table, Col, LinkCol
from flask import Flask, Markup, request, url_for

import wimm.utils as utils
import wimm.core as core
import wimm.structure

"""
A example for creating a Table that is sortable by its header
"""

app = Flask(__name__)

invoices = wimm.structure.invoices

class SortableTable(Table):
    #classes = ['striped']
    id = Col('ID')
    date = Col('Date')
    amount = Col('amount')
    link = LinkCol(
        'Link', 'show_item', url_kwargs=dict(id='id'), allow_sort=False)
    allow_sort = True

    def sort_url(self, col_key, reverse=False):
        if reverse:
            direction = 'desc'
        else:
            direction = 'asc'
        return url_for('index', sort=col_key, direction=direction)


@app.route('/')
def index():
    sort = request.args.get('sort', 'id')
    reverse = (request.args.get('direction', 'asc') == 'desc')
    table = SortableTable(invoices.get_sorted_by(sort, reverse),
                          sort_by=sort,
                          sort_reverse=reverse)
    page = f""" <!DOCTYPE html>
                <html>
                <head>
                <link rel="stylesheet" href="https://cdn.rawgit.com/Chalarangelo/mini.css/v3.0.1/dist/mini-default.min.css">
                </head>
                <body>
                
                <h1>Invoices</h1>
                {table.__html__()}
                
                </body>
                </html>
            """
    
    return page


@app.route('/item/<id>')
def show_item(id):
    inv = invoices.get_by_id(id)
    return str(inv.to_dict())



invoices = wimm.structure.invoices


if __name__ == '__main__':
    app.run(debug=True)
