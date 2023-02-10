
 If you have syslog data in a Linux system and want to convert it to CEF format, you can use the following RSYSLOG templates:

```
$template CEF,"CEF:0|%{syslog_app}|%{syslog_app}|%{syslog_pid}|%{syslog_msgid}|%{syslog_message}|%{syslog_priority}|%{syslog_facility}\"

```

