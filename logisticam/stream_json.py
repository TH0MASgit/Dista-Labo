from argparse import ArgumentParser
from datetime import datetime, timedelta
from threading import Timer

import pandas as pd

from db.distaDB import *


def to_json(df) :
    df['time'] = df['time'].astype('int64') // 10**6
    return df.values.tolist()


def start_stream(args, db) :
    ignored = 0
    
    def get_query(name) :
        try:
            return getattr(db, name)
        except AttributeError :
            ignored += 1
            print(f"Warning: query {name} not found")
            return lambda *args: pd.DataFrame(columns = ['time'])
    
    queries = {query_name : get_query(query_name) for query_name in args.queries}
    
    def fetch_data(start_time, end_time=None) :
        print('{')
        for (name, query) in queries.items() :
            df = query(args.cameras, start_time, end_time)
            print(f'"{name}": {to_json(df)},')
        print(f'"ignored": {ignored}\n}}', flush=True)
    
    if args.stop : # 'instant replay' mode for historical data
        fetch_data(args.start, args.stop)
        return
    
    # else we go into 'realtime' mode for fresh data (or replaying older data in realtime)
    interval = 1 # update interval in seconds (TODO should be an argument)
    
    def replay(ts) :
        try :
            next = ts + timedelta(seconds=interval)
            timer = Timer(interval, replay, args=[next])
            timer.start()
            fetch_data(ts, next)
        except :
            timer.cancel()
            raise
    
    def refresh(ts) :
        try :
            next = datetime.now()
            timer = Timer(interval, refresh, args=[next])
            timer.start()
            fetch_data(ts)
        except :
            timer.cancel()
            raise
    
    if args.start :
        replay(args.start)
    else :
        refresh(datetime.now() - timedelta(seconds=interval))


## USAGE:
## python stream_json.py queries... [-c ids...] [--start dt [--stop dt]]
## start and stop are ISO formatted datetimes
if __name__ == '__main__' :
    parser = ArgumentParser(description="""
        example: python stream_json.py "select_nb_detections" -c 1 3 --start "2020-07-02 08:30:00"
    """)

    parser.add_argument('queries', type=str, nargs='+',
                        help="name of the query or queries to call")
    parser.add_argument('-c', '--cameras', type=int, nargs='+',
                        help="list of cameras to fetch data for (default=all)")
    parser.add_argument('--start', type=datetime.fromisoformat,
                        help="iso formatted datetime of the data replay time (default=now)")
    parser.add_argument('--stop', type=datetime.fromisoformat,
                        help="iso formatted datetime of the data replay end (if start is also set)")
    
    args = parser.parse_args()
    if args.stop and not args.start :
        print(args)
        parser.error("Start time must be present when end time is.")
    
    #TODO db should be an argument too
    db = DistaDB("db/samples/dista_ete_06-29_au_07-02_globale.sqlite")
    #db = DistaDB("mysql:192.168.0.19/dista_test6")
    #db = DistaDB("mysql:10.180.5.121/dista")
    
    start_stream(args, db)
