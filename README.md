


# JSON to CEF converter
convert your JSON events to CEF format
* Author : Tamir Suliman
* Date : 02-09-2023

* Converting from JSON to CEF involves mapping the fields from the JSON data to the fields in the Common Event Format (CEF). CEF is a standardized log format that enables log management systems to process and store logs from various security and network devices.

* The CEF format consists of a number of key-value pairs that provide information about the log event. The basic structure of a CEF log message is as follows:
CEF:Version|Device Vendor|Device Product|Device Version|Signature ID|Name|Severity|[Extension Key]=[Value] ...

* To convert a JSON log to CEF, you would need to extract the relevant information from the JSON data and map it to the appropriate fields in the CEF format. For example, you could extract the "event.code", "event.severity", and "message" fields from the JSON data and map them to the "Signature ID", "Severity", and "Name" fields in the CEF format.

* The scripts in this repository would help you achieve that.However, since JSON structure and data changes a template must be created to address all different data sources.

* The use case scenario would be :

![JSON CEF PIPELINE ]("https://github.com/allamiro/JSON-SYSLOG-TO-CEF/blob/main/images/json.jpeg")


### CISCO Logs

# SYSLOG to CEF converter
Syslog,  is an open standard for logging and reporting events from computer systems, network devices, and other IT assets. Syslog is supported by a wide range of network devices and operating systems, making it a widely used logging format. Syslog messages contain a priority value, which indicates the severity of the event, and a message body, which provides detailed information about the event.


[LINUX END POINTS ]
[CISCO DEVICES]. === >TCP/syslog-file ===> SYSLOG-CEF.py ===> file-logs.cef 
[SYSLOG Servers]


### CISCO Logs 



### Built With

This section should list any major frameworks/libraries used to bootstrap your project. Leave any add-ons/plugins for the acknowledgements section. Here are a few examples.


# References 
Log sampels  used from https://github.com/elastic/beats/tree/main/x-pack/filebeat/module
