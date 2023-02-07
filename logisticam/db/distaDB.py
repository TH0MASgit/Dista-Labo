import os, errno

import pandas as pd


# This function encapsulates its input in a list, if it's not one already.
def lwrap(val):
    if val is None:
        return []
    elif hasattr(val, "__iter__") and not isinstance(val, str):
        return val
    else:
        return [val]

# This function converts python values to SQL literals.
def qstr(val):  # NB. This function does not escape or sanitize strings!
    if val is None:
        return "NULL"
    elif isinstance(val, (int, float)):
        return str(val)  # Numbers should not be quoted in SQL,
    else:
        return f"'{val}'"  # but everything else must be.


class DistaDB:

    def __init__(self, db_url):
        db_conn = db_url.split(':', 1)

        if len(db_conn) == 1 or db_conn[0] == 'sqlite:':
            from .time_utils import SQLite_time
            self.db_time = SQLite_time.to_dbformat
            self.db_type = 'sqlite'
            db_path = db_conn[-1] or 'dista.sqlite'  # the default database name is dista.sqlite

            import sqlite3
            try:
                if os.path.isfile(db_path):
                    self.dbc = sqlite3.connect(db_path, check_same_thread=False)  #TODO Only for reading!
                else:
                    print(f"Cannot open {db_path} :\n{os.strerror(errno.ENOENT)}")
                    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), db_path)
            except sqlite3.Error as e:
                print(f"Could not connect to sqlite:{db_path} :\n{e}")
                raise

        else:
            from .time_utils import MySQL
            self.db_time = MySQL.to_datetime
            self.db_type = 'mysql'
            db_path = db_conn[1].rsplit('/', 1)

            if db_conn[0] == 'mysql':
                import mysql.connector
                db_module = mysql.connector

            elif db_conn[0] == 'mariadb':
                import mariadb
                db_module = mariadb

            else:
                print(f"Unsupported database: {db_conn[0]}")
                raise

            try:
                self.dbc = db_module.connect(
                    host=db_path[-2] if len(db_path) > 1 else 'localhost',
                    user='innovlog',
                    password='logisticam-SQL-read',
                    database=db_path[-1] if db_path[-1] else 'dista-test')

                # We also need to set the timezone _per session_ (for AWS)
                cur = self.dbc.cursor()
                cur.execute("SET time_zone = 'America/Toronto'")
                cur.close()
            except db_module.Error as e:
                print(f"Could not connect to {db_url} :\n{e}")
                raise


    def create_time_range(self, start=None, end=None):
        if start and end:
            if start == end:
                return f"= {self.db_time(start)}"
            else:
                return f"BETWEEN {self.db_time(start)} AND {self.db_time(end)}"
        elif start:
            return f">= {self.db_time(start)}"
        elif end:
            return f"<= {self.db_time(end)}"
        else:
            return ""

    def timestamp_to_int(self, timestamp_col):
        if self.db_type == 'mysql':
            return f"UNIX_TIMESTAMP({timestamp_col})"
        else:
            return f"CAST({timestamp_col} AS INTEGER)"


    def _select_query(self, sql, *labels):
        # print(sql)

        # First, query the data from the database
        cur = self.dbc.cursor()
        cur.execute(sql)  #TODO Should have prepared the statements (with ?)
        rows = cur.fetchall()
        cur.close()

        # Second, wrap the data in a DataFrame
        data = pd.DataFrame(rows, columns=['time', 'camera', *labels])
        data['time'] = pd.to_datetime(data['time'], unit='s', utc=True)
        data['time'] = data['time'].dt.tz_convert('Canada/Eastern').dt.tz_localize(None)
        #TODO Time localization should be handled by the db (return a datetime, not an int)
        return data

    def _select_template(self, stat_name, agg_function, data_source,
                         camera, start_time, end_time, agg_period):
        camera = lwrap(camera)
        time_range = self.create_time_range(start_time, end_time)
        agg_period = int(agg_period)  # agg_period _must_ be an integer (in seconds)

        sql_frame = f"""
        SELECT
            Frames.id,
            Frames.created_at,
            Frames.created_by,
            {agg_function} AS agg_per_frame
        FROM {data_source}
        {f"WHERE Frames.created_by IN ({','.join(map(qstr, camera))})" if camera else ""}
        {f"{'AND' if camera else 'WHERE'} Frames.created_at {time_range}" if time_range else ""}
        GROUP BY Frames.id, Frames.created_at, Frames.created_by
        """

        sql_second = f"""
        SELECT
            {self.timestamp_to_int('T_frame.created_at')} AS time,
            Camera_configurations.description AS camera,
            AVG(T_frame.agg_per_frame) AS agg_per_second
        FROM ({sql_frame}) AS T_frame
            INNER JOIN Camera_configurations ON T_frame.created_by = Camera_configurations.id
        GROUP BY time, camera
        """

        if agg_period <= 1:
            return self._select_query(sql_second, stat_name)

        timeslice = "(T_second.time {0:s} {1:d}) * {1:d}".format(
            'DIV' if self.db_type == 'mysql' else '/', agg_period)

        return self._select_query(f"""
        SELECT
            ({timeslice}) AS timeslice,
            T_second.camera AS camera,
            AVG(T_second.agg_per_second) AS {stat_name}
        FROM ({sql_second}) AS T_second
        GROUP BY timeslice, camera
        """, stat_name)


    # Nombre de personnes détectées
    def select_nb_detections(self, camera=[], start_time=None, end_time=None,
                             time_interval=1):
        return self._select_template(
            "nb_detections",
            "COUNT(Detections.tracking_id)",
            "Frames LEFT JOIN Detections ON Detections.frame = Frames.id",
            camera, start_time, end_time, time_interval)

    # Nombre de personnes en état de collision
    def select_nb_colliding_detections(self, camera=[], start_time=None, end_time=None,
                                       time_interval=1, collision_threshold=200.0):
        return self._select_template(
            "nb_colliding_detections",
            "COUNT(T0.tracking_id)",
            f"""Frames LEFT JOIN (
                SELECT * FROM Detections
                WHERE Detections.min_distance < {float(collision_threshold)}
            ) AS T0 ON T0.frame = Frames.id""",
            camera, start_time, end_time, time_interval)

    # Nombre [total] de collisions (interactions de moins de 2m)
    def select_nb_collisions(self, camera=[], start_time=None, end_time=None,
                             time_interval=1, collision_threshold=200.0):
        return self._select_template(
            "nb_collisions",
            "COUNT(T0.distance)",
            f"""Frames LEFT JOIN (
                SELECT * FROM Distances
                WHERE Distances.distance < {float(collision_threshold)}
            ) AS T0 ON T0.frame = Frames.id""",
            camera, start_time, end_time, time_interval)

    # Distance moyenne entre [toutes] les personnes
    def select_avg_distance(self, camera=[], start_time=None, end_time=None,
                            time_interval=1):
        # TODO Consider converting the distance to meters here, ie:
        # df['avg_distance'] /= 100
        return self._select_template(
            "avg_distance",
            "AVG(Distances.distance)",
            "Frames LEFT JOIN Distances ON Distances.frame = Frames.id",
            camera, start_time, end_time, time_interval)

    # Distance moyenne de chaque personne à son plus proche voisin
    def select_avg_closest_neighbor(self, camera=[], start_time=None, end_time=None,
                                    time_interval=1):
        #TODO Consider converting the distance to meters here, ie:
        # df['avg_closest_neighbor'] /= 100
        return self._select_template(
            "avg_closest_neighbor",
            "AVG(Detections.min_distance)",
            "Frames LEFT JOIN Detections ON Detections.frame = Frames.id",
            camera, start_time, end_time, time_interval)

    def select_sampled_positions(self, camera=[], start_time=None, end_time=None,
                                 time_interval=1):
        #TODO end_time=None => time.now()
        #TODO interval devrait pouvoir être éliminé (0) pour avoir un flux continu

        camera = lwrap(camera)
        time_range = self.create_time_range(start_time, end_time)
        time_interval = int(time_interval)  # time_interval _must_ be an integer (in seconds)

        timeslice = self.timestamp_to_int('Frames.created_at')
        if time_interval > 1:
            timeslice = "({0:s} {1:s} {2:d}) * {2:d}".format(timeslice,
                                                             'DIV' if self.db_type == 'mysql' else '/', time_interval)

        inner_sql = f"""
        SELECT
            ({timeslice}) AS timeslice,
            Camera_configurations.description AS camera,
            MAX(Frames.id) AS lastframe
        FROM Frames
            INNER JOIN Camera_configurations ON Frames.created_by = Camera_configurations.id
        {f"WHERE Frames.created_by IN ({','.join(map(qstr, camera))})" if camera else ""}
        {f"{'AND' if camera else 'WHERE'} Frames.created_at {time_range}" if time_range else ""}
        GROUP BY timeslice, camera
        """

        return self._select_query(f"""
        SELECT
            T_slice.timeslice AS timeslice,
            T_slice.camera AS camera,
            Detections.tracking_id AS det, Detections.pos_x AS X, Detections.pos_y AS Y
        FROM ({inner_sql}) AS T_slice
            LEFT JOIN Detections ON Detections.frame = T_slice.lastframe
        """, 'det', 'X', 'Y')


if __name__ == "__main__":  # Lancez-moi avec `cd .. ; python -m db.distaDB`
    import sys, time

    if len(sys.argv) > 1 :
        db = sys.argv[1]
    else:
        #db = DistaDB("db/samples/dista_ete_06-29_au_07-02_globale.sqlite")
        #db = DistaDB("mysql:192.168.0.19/dista_test")
        #db = DistaDB("mysql:10.180.5.121/dista")
        db = DistaDB("mariadb:dista.cuyasziqzqwn.us-east-1.rds.amazonaws.com/dista-test")

    print('select_nb_detections')
    t0 = time.time()
    data = db.select_nb_detections(start_time=1593719037, end_time=1593719037)
    print(data)
    print(f"Returned {len(data)} rows in {(time.time() - t0) * 1000:.0f} ms\n")

    print('select_nb_colliding_detections')
    t0 = time.time()
    data = db.select_nb_colliding_detections(camera=1, collision_threshold=200)
    print(data)
    print(f"Returned {len(data)} rows in {(time.time() - t0) * 1000:.0f} ms\n")

    print('select_nb_collisions')
    t0 = time.time()
    data = db.select_nb_collisions(camera=1, collision_threshold=150)  # 150 cm
    print(data)
    print(f"Returned {len(data)} rows in {(time.time() - t0) * 1000:.0f} ms\n")

    print('select_avg_distance')
    t0 = time.time()
    data = db.select_avg_distance(camera=[1, 2], time_interval=60)  # 60 secondes
    print(data)
    print(f"Returned {len(data)} rows in {(time.time() - t0) * 1000:.0f} ms\n")

    print('select_avg_closest_neighbor')
    t0 = time.time()
    data = db.select_avg_closest_neighbor(camera=[1, 2], time_interval=60)
    print(data)
    print(f"Returned {len(data)} rows in {(time.time() - t0) * 1000:.0f} ms\n")

    print('select_sampled_positions')
    t0 = time.time()
    data = db.select_sampled_positions(camera=1, time_interval=1, start_time=1593719037, end_time=1593719637)
    print(data)
    print(f"Returned {len(data)} rows in {(time.time() - t0) * 1000:.0f} ms\n")
