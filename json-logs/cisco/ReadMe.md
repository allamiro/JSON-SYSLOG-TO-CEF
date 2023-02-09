
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
|act	|Action performed|	String	|No	|Login|






