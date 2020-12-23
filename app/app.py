#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 23 13:26:41 2020

@author: jev
"""

from flask_table import Table, Col, LinkCol
from flask import Flask, Markup, request, url_for, render_template
import json

import wimm.utils as utils
import wimm.core as core
import wimm.structure

"""
A example for creating a Table that is sortable by its header
"""

app = Flask(__name__)

invoices = wimm.structure.invoices
#invoices = wimm.core.Invoices.from_yaml('invoices.yaml')

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
    
    
    return render_template('invoices_received.html', title="WIMM", table = table)


@app.route('/item/<id>')
def show_item(id):
    inv = invoices.get_by_id(id)
    return json.dumps(inv.to_dict(),indent=4)



if __name__ == '__main__':
    app.run(debug=True)
