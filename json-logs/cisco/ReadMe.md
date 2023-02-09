
## Converting CISCO IOS JSON LOGS to CEF

### STEP 1 
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
### STEP 2 

Idenity what CEF field will map  to the key - map the cef field

| CEF Field| Key Extracted from the Json file   |
|----------|------------------------------------|
|          |                                    |
|          |                                    |
|          |                                    |




|Field Name	|Field Description	|Data Type|	Required|	Example|
|-----|------|-----|---|---|---|
|act	|Action performed|	String	No	Login
|src	|Source IP address	String	No	10.0.0.1
|dst	|Destination IP address	String	No	10.0.0.2
|prt	|Port number	Integer	No	80
|spt	|Source port number	Integer	No	12345
|dpt	|Destination port number	Integer	No	8080
|smac|	Source MAC address	String	No	00:11:22:33:44:55
|dmac|	Destination MAC address	String	No	AA:BB:CC:DD:EE:FF
|cs1|	Custom field 1 |	String	No	User1
|cs2|	Custom field 2|	String	No	Department1






