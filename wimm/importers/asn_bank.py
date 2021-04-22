#!/usr/bin/env python
"""
    importer for ASN bank statement

"""
import pandas as pd
from wimm.importers import abstract_classes
from wimm.core import Transactions
from wimm.utils import clean_str

mapping = {'header': ['Boekingsdatum',
                      'Opdrachtgeversrekening',
                      'Tegenrekeningnummer',
                      'Naam tegenrekening',
                      'Adres',
                      'Postcode',
                      'Plaats',
                      'Valutasoort rekening',
                      'Saldo voor mutatie',
                      'Valutasoort mutatie',
                      'Bedrag',
                      'Jounaaldatum',
                      'Valutadatum',
                      'Interne transactiecode',
                      'Globale transactiecode',
                      'Volgnummer',
                      'Betalingskenmerk',
                      'Omschrijving',
                      'Afschriftnummer'],
           'mapping': {'Bedrag': 'amount',
                       'Boekingsdatum': 'date',
                       'Naam tegenrekening': 'name',
                       'Omschrijving': 'description',
                       'Tegenrekeningnummer': 'iban_other'}}


class Importer(abstract_classes.Importer):

    def __init__(self, csv_file) -> None:
        super().__init__()

        header = mapping['header']
        renaming = mapping['mapping']

        df = pd.read_csv(csv_file, names=header)
        df.rename(renaming, axis=1, inplace=True)

        relevant_cols = [v for k, v in renaming.items()]

        self.df = df[relevant_cols]

    def transactions(self, acct_name='Assets.Bank.ASN') -> Transactions:

        records = self.df.to_dict(orient='records')

        data = []
        for r in records:

            # init data element
            d = {}
            d['date'] = r['date']
            d['description'] = r['description'].strip("'")

            try:
                ext_name = 'Ext.'+clean_str(r['name'])
            except AttributeError:
                ext_name = 'Ext.unknown'

            d['transfers'] = {acct_name: r['amount'],
                              ext_name: -r['amount']}

            data.append(d)

        return Transactions(data)


if __name__ == '__main__':

    fName = r'/home/jev/Documents/Jev/Sojuz/Boekhouding/statements/0783206356_22042021_120234.csv'
    importer = Importer(fName)
    print(importer.df)
    transactions = importer.transactions()
    print(transactions.to_yaml())
