
## Converting CISCO IOS JSON LOGS to CEF
## STEP 1
Update the logstash pipeline to ouput the file in json format 
* I guess I could also use output tcp but the socket wasnt workin on mac - will test it 


```

input {
  udp {
    port => 514
    type => "syslog"
  }
}

filter {
  grok {
    match => { "message" => "%{SYSLOGTIMESTAMP:syslog_timestamp} %{SYSLOGHOST:syslog_hostname} %{DATA:syslog_message}" }
  }
  date {
    match => [ "syslog_timestamp", "MMM d HH:mm:ss", "MMM dd HH:mm:ss" ]
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    manage_template => false
    index => "syslog-%{+YYYY.MM.dd}"
  }
  file {
    path => "/path/to/output/file.json"
    codec => "json"
  }
}

```
### STEP 2
Identify and generate the keys in the logs 


```

import json
with open("cisco-ios.json", "r") as file:
    data = json.load(file)
# Loop through the dictionary and print all the keys
for log in data:
    for key in log.keys():
         print(key) 

```


|     |
|----|
|cisco.ios.access_list|
|cisco.ios.facility|
|destination.address|
|destination.ip|
|destination.port|
|event.category|
|event.code|
|event.dataset|
|event.kind|
|event.module|
|event.original|
|event.outcome|
|event.sequence|
|event.severity|
|event.timezone|
|event.type|
|fileset.name|
|input.type|
|log.level|
|log.offset|
|log.source.address|
|message|
|network.community_id|
|network.packets|
|network.transport|
|network.type|
|related.ip|
|service.type|
|source.address|
|source.ip|
|source.packets|
|source.port|
|tags|


### STEP 3

Idenity what/which CEF fields that you will need to map  to the keys - map the cef field

| CEF Field| Key Extracted from the Json file   |
|----------|------------------------------------|
| act      |                                    |
| src      |  source.ip                         |
|          |                                    |





### STEP 4

Create your python parser 


```
#!/usr/bin/python3
# Author Tamir Suliman
# Email allamiro@gmail.com
# Date : 02-09-2023

# Import libraries 
import json
import re 
import os 
import socket 


#CEF_template = "CEF:0|{cisco.ios.facility}|{event.module}|{event.code}|{message}|{event.severity}|"
# Define the CEF header template
cef_header = "CEF:0|Cisco|IOS|1.0|"

cef_data = []

# Read the json files in the directory 
with open('data2.json', 'r+') as ciscolog:
        jess_dict = json.load(ciscolog)
        #jess_dict1 = json.dumps(jess_dict, indent=4)
        jess_dict1 = json.dumps(jess_dict)

# Passing the JSON file to a Converter Function


with open("cisco-cef_logs.log", "w") as f:
    for log in jess_dict:
        cef_log = cef_header + "id=" + str(log.get("event.sequence", "")) + " "
        cef_log += "src=" + log.get("source.address", "") + " "
        cef_log += "spt=" + str(log.get("source.port", "")) + " "
        cef_log += "dst=" + log.get("destination.ip", "") + " "
        cef_log += "dpt=" + str(log.get("destination.port", "")) + " "
        cef_log += "proto=" + log.get("network.transport", "") + " "
        cef_log += "cat=" + ','.join(log.get("event.category", [])) + " "
        cef_log += "dvc=" + ','.join(log.get("log.source.address", [])) + " "
        cef_log += "msg=" + log.get("event.original", "") + " "
        cef_log += "outcome=" + log.get("event.outcome", "") + " "
        cef_log += "cs1=" + log.get("event.code", "") + " "
        cef_log += "cs2=" + log.get("network.community_id", "") + " "
        cef_log += "cs3=" + log.get("cisco.ios.access_list", "") + " "
        cef_log += "severity=" + str(log.get("event.severity", "")) + " "
        print(cef_log)
        f.write(cef_log + "\n")

```












## STEP 5 

Run and update the python script 





## References
[1] https://help.deepsecurity.trendmicro.com/10_2/on-premise/Events-Alerts/syslog-parsing.html

[2] https://github.com/elastic/beats/tree/main/x-pack/filebeat

