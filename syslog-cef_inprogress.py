
import os
from datetime import datetime

def syslog_to_cef(syslog_message):
    # Split the syslog message into fields
    fields = syslog_message.split()
    
    # Extract relevant fields
    date = fields[0] + " " + fields[1] + " " + fields[2]
    host = fields[3]
    process_name = fields[4]
    message = " ".join(fields[5:])

    # Construct the CEF message
    cef = "CEF:0|{}|{}|{}|{}|{}".format("Syslog", host, process_name, "", message)
    return cef

syslog_messages = [
    "Feb  9 14:43:51 kafka3 dnf[141385]: Rocky Linux 8 - AppStream                        13 kB/s | 4.8 kB     00:00",
    "Feb  9 14:43:52 kafka3 dnf[141385]: Rocky Linux 8 - BaseOS                           14 kB/s | 4.3 kB     00:00",
    "Feb  9 14:43:52 kafka3 dnf[141385]: Rocky Linux 8 - Extras                           11 kB/s | 3.1 kB     00:00",
    # ... other messages ...
]

for syslog_message in syslog_messages:
    cef = syslog_to_cef(syslog_message)
    #print(cef)

import re
from datetime import datetime

def extract_data(message):
    log_data = {}
    # Extract date and time
    date_time = re.search(r'(\w{3} \d{2} \d{4} \d{2}:\d{2}:\d{2})', message)
    log_data['date_time'] = datetime.strptime(date_time.group(1), '%b %d %Y %H:%M:%S')
    # Extract log level
    log_level = re.search(r'(%\w{3}-\d{1}-\d{6}):', message)
    if log_level:
        log_data['log_level'] = log_level.group(1)
    else:
        log_data['log_level'] = None
    # Extract log message
    log_message = re.search(r'(%\w{3}-\d{1}-\d{6}): (.*)', message)
    if log_message:
        log_data['log_message'] = log_message.group(2)
    else:
        log_data['log_message'] = None
    return log_data


def read_file(file_path):
    log_entries = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            log_entries.append(extract_data(line.strip()))      
    return log_entries


def main():
    log_entries = []
    file_path = "ciscosyslog"
    log_entries = read_file(file_path)
    print(log_entries)


if __name__ == '__main__':
    main()
