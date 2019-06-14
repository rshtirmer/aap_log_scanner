# aap_log_scanner
128Technologies script for handling log files in python. 

# Usage
```
usage: scanlogs.py [-h] [--startdate [STARTDATE]] [--enddate [ENDDATE]]
                   [--file [FILE]] [--ap [AP]] [--event [EVENT]] [--saltcall]
                   [--force]

optional arguments:
  -h, --help            show this help message and exit
  --startdate [STARTDATE]
                        Provide a start date, for example: 2019-06-13.
                        Defaults to today's date
  --enddate [ENDDATE]   Provide an end date, for example: 2019-06-13. Defaults
                        to today's date
  --file [FILE]         Provide a log file, for example:
                        /var/log/128technology/t128_aap.log
  --ap [AP]             Provide an access provider to filter by, for example:
                        optimum
  --event [EVENT]       Filter events by e6 or e7. If not set, no filtering by
                        event is done.
  --saltcall            Set this flag to run a salt call on gathered store
                        numbers.
  --force               Set this flag to autoagree to all user prompts.
  ```
