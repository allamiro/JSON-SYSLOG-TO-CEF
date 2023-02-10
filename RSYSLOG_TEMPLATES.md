
 If you have syslog data in a Linux system and want to convert it to CEF format, you can use the following RSYSLOG templates:

```
$template CEF,"CEF:0|%{syslog_app}|%{syslog_app}|%{syslog_pid}|%{syslog_msgid}|%{syslog_message}|%{syslog_priority}|%{syslog_facility}\"

```


This template will parse the syslog data into the following CEF format:




```

CEF:0|<Syslog App Name>|<Syslog App Name>|<Syslog PID>|<Syslog Msg ID>|<Syslog Message>|<Syslog Priority>|<Syslog Facility>

```






```$template CEF,"CEF:0|%{syslog_app}|%{syslog_hostname}|%{syslog_pid}|%{syslog_message}|%{syslog_priority}|%{syslog_facility}\"
```
This template will parse the syslog data into the following CEF format:



## CISCO Messages 

```
# Define the CEF template
$template CEF,"CEF:0|Cisco|%FROMHOST-IP%|%syslogtag%|%msg%|%syslogfacility-text%|%syslogseverity-text%\n"

# Filter to apply CEF format to syslog messages with facility local7 and severity warning or higher
if ($syslogfacility-text == 'local7' and $syslogseverity >= 'warning') then {
  action(type="omfile" file="cef.log" template="CEF")
}

# Filter to apply CEF format to syslog messages with facility local4 and tag 'CISCO-AAA-SESSION-MIB'
if ($syslogfacility-text == 'local4' and $syslogtag == 'CISCO-AAA-SESSION-MIB') then {
  action(type="omfile" file="cef.log" template="CEF")
}

```
