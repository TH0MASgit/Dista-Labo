import datetime


# This utility function converts python values to SQL literals.
def qstr(val) :  # NB. This function does not escape or sanitize strings!
    if val is None :
        return "NULL"
    elif isinstance(val, (int, float)) :
        return str(val)     # Numbers should not be quoted in SQL,
    else :
        return f"'{val}'"   # but everything else must be.


# Convert between SQLite's datetime representations ============================
# See https://www.sqlite.org/lang_datefunc.html
# and https://www.techonthenet.com/sqlite/functions/julianday.php

class SQLite_time :

    @staticmethod
    def to_datetime(ts, to_localtime=True) :  # 'ts' can be unix or julianday
        return f"""(
        CASE typeof({ts})
            WHEN 'integer' THEN datetime({ts}, 'unixepoch'{", 'localtime'" if to_localtime else ""})
            ELSE datetime({ts}{", 'localtime'" if to_localtime else ""})
        END)"""

    @staticmethod
    def to_julianday(dt, to_utc=True) :  # julianday is SQLite's native timestamp format somehow...
        return f"""(
        CASE typeof({dt})
            WHEN 'integer' THEN julianday({dt}, 'unixepoch'{", 'utc'" if to_utc else ""})
            ELSE julianday({dt}{", 'utc'" if to_utc else ""})
        END)"""

    @staticmethod
    def to_unixepoch(dt, to_utc=True) :
        return f"""(
        CASE typeof({dt})
            WHEN 'integer' THEN strftime('%s', {dt}, 'unixepoch'{", 'utc'" if to_utc else ""})
            ELSE strftime('%s', {dt}{", 'utc'" if to_utc else ""})
        END)"""

    # This function converts python datetimes to SQLite timestamp-integers
    @staticmethod
    def to_dbformat(dt) :
        if isinstance(dt, (int, float)) :  # timestamps must be UTC
            return str(int(dt))
        elif isinstance(dt, datetime.datetime) :  # strings or others are local
            return SQLite_time.to_unixepoch(dt.strftime("'%Y-%m-%d %H:%M:%S'"))
        else :
            return SQLite_time.to_unixepoch(qstr(dt))


# Convert between MySQL's datetime representations ============================
# See https://www.w3resource.com/mysql/date-and-time-functions/mysql-from_unixtime-function.php
# and https://www.epochconverter.com/programming/mysql

class MySQL :

    @staticmethod
    def to_datetime(ts) :
        if ts is None :
            return "NULL"
        elif isinstance(ts, (int, float)) :  # Integer timestamps must be in UTC, and will be localized by the server.
            return f"FROM_UNIXTIME({int(ts)})"
        elif isinstance(ts, datetime.datetime) :
            return ts.strftime("'%Y-%m-%d %H:%M:%S'")
        elif isinstance(ts, str) :
            try :
                datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            except ValueError :
                return f"FROM_UNIXTIME(`{ts}`)"  # We'll assume `ts` is a column name.
        else :
            return f"'{ts}'"  # DT strings and other types are passed as-is

    @staticmethod
    def to_timestamp(dt) :  # This always converts to UTC
        if dt is None :
            return "NULL"
        elif isinstance(dt, (int, float)) :
            return str(int(dt))
        elif isinstance(dt, datetime.datetime) :  # Datetimes must be local, and will be converted to UTC by the server.
            return dt.strftime("UNIX_TIMESTAMP('%Y-%m-%d %H:%M:%S')")
        elif isinstance(dt, str) :
            try :
                datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
            except ValueError :
                return f"UNIX_TIMESTAMP(`{dt}`)"  # We'll assume `dt` is a column name.
        else :
            return f"UNIX_TIMESTAMP('{dt}')"  # DT strings and other types are converted to timestamps
