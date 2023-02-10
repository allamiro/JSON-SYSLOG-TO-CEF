#!/usr/bin/python3
# Author Tamir Suliman
# Email allamiro@gmail.com
# Date : 02-09-2023

# Import libraries 

import json
import re 
import os 
import socket 

# CEF_template = "CEF:0|{cisco.ios.facility}|{event.module}|{event.code}|{message}|{event.severity}|"
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

        
        
        
        
        
        
        
