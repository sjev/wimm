# Quick start

## Set environment variable

WIMM needs to know where its database is located. This path id defined in `WIMM_PATH` environment variable.
Most convinient way to set the environment variable is to add a line to `.bashrc` file: 

``` bash
export WIMM_PATH=/home/user/accounting
```

But you can also just set the variable for current working dir like this: `WIMM_PATH="$PWD"`

You can check the configuration with `wimm info`:

``` none
$ wimm info
Data location: /home/jev/temp
Hashed files: 0
```

## Init database

`wimm init files` will create the necessary files and folders.

Now you shold be able to view current balance:

``` none
$ wimm show balance
----------Balance-----------
Assets               0.0
Assets.Bank          0.0
Assets.bank       1100.0
Expenses            50.0
Ext.Bob          -1000.0
INR.00_000           0.0
Liabilities       -150.0
tax.to_pay           0.0
tax.to_receive       0.0
----------------------------
SUM: 0.00
```
