
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
