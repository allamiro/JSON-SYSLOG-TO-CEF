
 If you have syslog data in a Linux system and want to convert it to CEF format, you can use the following RSYSLOG templates:

```
$template CEF,"CEF:0|%{syslog_app}|%{syslog_app}|%{syslog_pid}|%{syslog_msgid}|%{syslog_message}|%{syslog_priority}|%{syslog_facility}\"

```


This template will parse the syslog data into the following CEF format:




```

CEF:0|<Syslog App Name>|<Syslog App Name>|<Syslog PID>|<Syslog Msg ID>|<Syslog Message>|<Syslog Priority>|<Syslog Facility>

```

This template will parse the syslog data into the following CEF format:




$template CEF,"CEF:0|%{syslog_app}|%{syslog_hostname}|%{syslog_pid}|%{syslog_message}|%{syslog_priority}|%{syslog_facility}\"
This template will parse the syslog data into the following CEF format:

