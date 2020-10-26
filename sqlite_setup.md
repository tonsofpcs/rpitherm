# rpitherm
## sqlite setup

At an sqlite prompt, to set up the database, run the following:

```
CREATE TABLE config(config_value TEXT PRIMARY KEY, value TEXT);
CREATE TABLE status_log(datetime INTEGER PRIMARY KEY, status INTEGER);
CREATE TABLE target_log(datetime INTEGER PRIMARY KEY, target DECIMAL(4,1), targethigh DECIMAL(4,1), targetlow DECIMAL(4,1), hysteresis DECIMAL(4,1));
CREATE TABLE temp_log(datetime INTEGER PRIMARY KEY, temp DECIMAL(9,5));
```
