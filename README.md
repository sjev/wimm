

# Introduction 

## What is WIMM

*WIMM* is a text-based acconting tool. It joins the ranks of [plain text accounting](https://plaintextaccounting.org/) software, such as *ledger* and co.

**WIMM features**:

* yaml file format
* support for invoice management
* import of bank statements 
* tax (VAT or BTW in Dutch)


## Why WIMM 

There is a lot of accounting sofware out there, so why *wimm*? 
Well, there are many great advantages of of *plain text accounting*, to name a few of them:

* data is human readable/editable
* plays nicely with version control systems
* new tools/scripts are easy to build

However, I could not find a piece of software that would sufficiently automate my workflow, especially around invoce and tax management. So WIMM was born.

## Installation

Wimm is currently in development phase. For this reason there is no pip package available.
To install WIMM, clone the repository, then run

``` none
pip install -r requirements.txt
pip install -e .
```
(this will install wimm in development mode)


## Documentation

see [WIMM documentation](https://sjev.github.io/wimm/)


## How it works

WIMM works with a database stored in a folder. The folder location is specified with `WIMM_PATH` envirionment variable.

### Data files

Overview of the data files:

 `balance.yaml` - account names that are included in balance calculations, including their starting values
``` yaml
Assets: 0.0
Assets.Bank: 0.0
Ext: 0.0
```


`transactions.yaml` - operations for moving money from one account to another

``` yaml 
- amount: 1000.0
  date: '2020-01-01'
  description: Customer paid invoice
  from: Ext.Bob
  to: Assets.bank
- amount: 50.0
  labels: office_supplies
  date: '2020-01-02'
  description: bought some pens
  from: Assets.bank
  to: Expenses
```

`invoices.yaml` - overview of sent and received invoices. 

!!! note
	invoices have a predefined id that starts with INS or INR in a form `INSYY_nnn` (INS stands for 'INvoice Sent', INS for 'INvoice Received').
	INS and INR prefixes will be recognized by wimm, resulting in suggestions for accounts and tax handling.

``` yaml
- amount: 0
  date: '2000-12-31'
  description: dummy invoice
  documents: invoices/INR.20_000_sample_invoice.pdf
  due_date: null
  id: INR.20_000
  sender: Microsoft
  tax: 0
```

### Data folders

Files added to the database will be copied to corresponding folders. 
Invoices are stored in the `invoices` folder.
A file location is added as `documents` field to corresponing data entry in `invoices.yaml` 
