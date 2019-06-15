# aap_log_scanner
128Technology script for handling log files in python.

# Usage
```
usage: t128_aap_logscanner.py [-h] [--startdate [STARTDATE]]
                              [--enddate [ENDDATE]] [--ap [AP]] [--saltcall]
                              [--force] [--e6] [--e7] [--getstore [GETSTORE]]

optional arguments:
  -h, --help            show this help message and exit
  --startdate [STARTDATE]
                        Provide a start date, for example: 2019-06-13.
                        Defaults to today's date
  --enddate [ENDDATE]   Provide an end date, for example: 2019-06-13. Defaults
                        to today's date
  --ap [AP]             Provide an access provider to filter by, for example:
                        optimum
  --saltcall            Set this flag to run a salt call on gathered store
                        numbers.
  --force               Set this flag to autoagree to all user prompts.
  --e6                  Set this flag to filter by E6 stores.
  --e7                  Set this flag to filter by E7 stores.
  --getstore [GETSTORE]
                        Prove a StoreNumber to retrieve.
```
