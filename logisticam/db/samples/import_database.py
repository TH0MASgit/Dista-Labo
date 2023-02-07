from datetime import datetime
import sys

import mariadb
dbp = ('?',)


def import_database(target=None, scripts=[]) :
    try :
        dbpath = target.rsplit('/', 1) if target else ['localhost']
        database = mariadb.connect(
            host=dbpath[0],
            database=dbpath[-1] if len(dbpath) > 1 else 'dista-dev',
            user='loady',
            password='dista-SQL-import')
        print(datetime.now(), "Connected to MariaDB on ", target)
    except mariadb.Error as e :
        print("Could not to MariaDB on", e)
        sys.exit(1)
    
    # Disabling FK checks will help speed up this process
    cursor = database.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
    database.commit()
    
    for script in scripts :
        with open(script, 'r') as f :
            print(datetime.now(), "Executing", script)
            cursor.executescript(f.read())
            database.commit()
    
    # We must also convert the created_at column from INT to TIMESTAMP
    cursor.execute("""ALTER TABLE `Frames`
    ADD COLUMN `created_at_tmp` TIMESTAMP NULL DEFAULT 0 AFTER `created_at`;""")
    cursor.execute("""UPDATE `Frames`
    SET `created_at_tmp` = FROM_UNIXTIME(`created_at`);""")
    
    database.commit()
    
    cursor.execute("""ALTER TABLE `Frames`
    DROP COLUMN `created_at`;""")
    cursor.execute("""ALTER TABLE `Frames`
    CHANGE `created_at_tmp` `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;""")
    
    database.commit()
    
    cursor.execute("""ALTER TABLE `Sessions`
    ADD COLUMN `started_at_tmp` TIMESTAMP NULL DEFAULT 0 AFTER `started_at`;""")
    cursor.execute("""UPDATE `Sessions`
    SET `started_at_tmp` = FROM_UNIXTIME(`started_at`);""")
    
    database.commit()
    
    cursor.execute("""ALTER TABLE `Sessions`
    DROP COLUMN `started_at`;""")
    cursor.execute("""ALTER TABLE `Sessions`
    CHANGE `started_at_tmp` `started_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;""")
    
    cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
    database.commit()
    cursor.close()
    
    print(datetime.now(), "Done")
    return database


if __name__ == '__main__' :
    target = sys.argv[1] if len(sys.argv) > 1 else 'dista-test.cuyasziqzqwn.us-east-1.rds.amazonaws.com'
    scripts = sys.argv[2:] if len(sys.argv) > 2 else ['dista_ete_part1_schema.sql',
                                                      'dista_ete_part2_frames.sql',
                                                      'dista_ete_part3_detections.sql',
                                                      'dista_ete_part4_distances.sql']
    
    db_conn = import_database(target, scripts)
    db_conn.execute("""
        SELECT TABLE_SCHEMA AS 'schema_name', table_name, table_rows
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA <> 'mysql' AND TABLE_SCHEMA NOT LIKE '%_schema';
    """)
    