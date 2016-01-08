# rt-dumper
Tool for dumping ticket history with attachments from Best Practical RT.
This Python script allows you save all tickets history (including attachments) from Best Practical Request Tracker https://bestpractical.com/rt/ via REST API.

## Installing
You need install latest version of "Requests" Python library http://docs.python-requests.org/en/latest/ For example you can install it via pip:
```
pip install requests
```

Then download rt_tickets_dumper.py:
```
wget https://raw.githubusercontent.com/ivsero/rt-dumper/master/rt_tickets_dumper.py
```

## Usage
You need to specify folder to download tickets content. In this folder tool creates a separate subdirectories for each ticket (named as ticket id).
Also you need specify other Request Tracker access details.
Example:
```
python rt_tickets_dumper.py --folder /home/ivsero/data/rt_dumps --domain rt.domain.tld --username ivsero --password *secret*
```
Tested on Python v. 2.7.9, Requests v. 2.6.2 and RT v. 4.2.1
