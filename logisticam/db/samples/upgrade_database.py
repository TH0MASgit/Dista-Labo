import sys
import sqlite3

database = sqlite3.connect(sys.argv[1])

LATEST_VERSION = 3.0

# NB: I didn't document every upgrade here because it would take longer to write
# this script than performing the upgrades manually on our early dbs, but I want
# to document that if needed, you can disable all FK constraints in SQLite using
# PRAGMA foreign_keys = off


# Check if database has a version tag or is too early for that =================
cursor = database.cursor()
try :
    cursor.execute("SELECT MAX(CAST(db_version AS FLOAT)) FROM Meta;")
    version = cursor.fetchone()[0]
    print(f"Current database version: {version}")
except :
    print("Couldn't determine database version automatically.")
    version = input("Please enter version number: ")
    cursor.execute("""CREATE TABLE IF NOT EXISTS Meta (
    db_version  VARCHAR(255),
    db_creation DATETIME);""")
    cursor.execute("INSERT INTO Meta(db_version) VALUES (?);", (version,))
    database.commit()

cursor.close()
version = float(version) #FIXME Version numbers aren't actually floats...

if version >= LATEST_VERSION :
    print(f"Already at the latest supported version: {LATEST_VERSION:.1f}")
    exit(0)


# For db versions < 1.3 ========================================================
if version < 1.3 :
    cursor = database.cursor()
    cursor.execute("ALTER TABLE Detections ADD COLUMN pos_z INTEGER;")
    database.commit()
    cursor.close()


# For db versions < 1.4 ========================================================
if version < 1.4 :
    cursor = database.cursor()
    
    # Make sure database has at least one real camera documented ===============
    cursor.execute("SELECT id FROM Camera_configurations;")
    rows = cursor.fetchall() # cursor.rowcount doesn't work with sqlite
    if len(rows) == 0 or (len(rows) == 1 and rows[0] == 0) :
        cursor.execute("""
        INSERT INTO Camera_configurations (description, cam_serial, resolution)
        VALUES ('Xavier securite', '12345678', 'VGA');""") #FIXME
    
    cursor.execute("CREATE INDEX IF NOT EXISTS serial_idx ON Camera_configurations(cam_serial);")
    database.commit()
    cursor.close()


# For db versions < 1.5 ========================================================
if version < 1.5 :
    cursor = database.cursor()

    cursor.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='Sessions';")
    if len(cursor.fetchall()) == 0 :
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Sessions (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,  -- PK: session identifier
            started_at   TIMESTAMP NOT NULL DEFAULT (strftime('%s', 'now')),
            command_args TEXT,  -- Command line arguments used when starting session
            comments     TEXT   -- Optional comment to describe session
        );""")

        cursor.execute("""
        INSERT INTO Sessions (started_at)
        SELECT created_at FROM Frames ORDER BY id LIMIT 1;""")

        cursor.execute("""
        INSERT INTO Sessions (started_at)
        SELECT f2.created_at
        FROM Frames f1 INNER JOIN Frames f2 on f2.id = f1.id + 1
        WHERE f2.created_at > f1.created_at + 600;""")

    database.commit()
    cursor.close()


# For db versions < 3.0 ========================================================
if version < 3.0 :
    cursor = database.cursor()

    cursor.execute("PRAGMA foreign_keys = off;")
    
    cursor.execute("ALTER TABLE Frames RENAME COLUMN 'collisions' to 'duration';")
    cursor.execute("UPDATE Frames SET duration = 1;")
    
    cursor.execute("ALTER TABLE Detections RENAME COLUMN 'no' to 'tracking_id';")
    cursor.execute("ALTER TABLE Detections ADD COLUMN 'category' INTEGER;")
    cursor.execute("ALTER TABLE Detections ADD COLUMN 'min_distance' REAL;")
    
    cursor.execute("PRAGMA foreign_keys = on;")
    
    print("Computing min_distance; Please wait...")
    cursor.execute("""
    SELECT
        Detections.frame,
        Detections.tracking_id,
        MIN(Distances.distance) AS min_distance_per_detection
    FROM Detections LEFT JOIN Distances ON Distances.frame = Detections.frame
        AND (Distances.det_1 = Detections.tracking_id OR Distances.det_2 = Detections.tracking_id)
    GROUP BY Detections.frame, Detections.tracking_id;""")
    for row in cursor.fetchall() :
        cursor.execute("UPDATE Detections SET min_distance = ? WHERE frame = ? AND tracking_id = ?;",
                       (row[2], row[0], row[1]))
    
    cursor.execute("""
    CREATE TABLE Camera_groups (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        description VARCHAR(255)
    );""")
    
    cursor.execute("""
    CREATE TABLE Group_memberships (
        camera_id   INTEGER,
        group_id    INTEGER,
        
        FOREIGN KEY (camera_id) REFERENCES Cameras(id)
            ON UPDATE CASCADE
            ON DELETE CASCADE,
            
        FOREIGN KEY (group_id) REFERENCES Camera_groups(id)
            ON UPDATE CASCADE
            ON DELETE CASCADE
    );""")

    database.commit()
    cursor.close()


# For db versions < 2.0 ========================================================
if version < 2.0 :
    cursor = database.cursor()

    cursor.execute("""
    CREATE VIEW IF NOT EXISTS Latest_detections AS
    SELECT
        datetime(Frames.created_at, 'unixepoch', 'localtime') AS local_time,
        Camera_configurations.description AS camera_desc,
        Frames.id AS frame_id,
        Detections.tracking_id AS detection_id,
        Detections.pos_x, Detections.pos_y, Detections.pos_z,
        Detections.min_distance
    FROM Frames
        INNER JOIN Camera_configurations
            ON Frames.created_by = Camera_configurations.id
        INNER JOIN Detections
            ON Frames.id = Detections.frame
    WHERE Frames.created_at >= (SELECT MAX(started_at) FROM Sessions)
    GROUP BY frame_id, detection_id;""")

    cursor.execute("""
    CREATE VIEW IF NOT EXISTS Heatmap AS
    SELECT
        local_time,
        camera_desc,
        frame_id || '-' || detection_id AS detection_id,
        0.6 * pos_x AS pxl_x, 0.6 * pos_y AS pxl_y, -- scale factor: 60px/100cm => 0.6
        max(1.0 - IFNULL(min_distance / 200.0, 1.0), 0.0) AS collision_intensity
    FROM Latest_detections;""")

    cursor.execute("""
    CREATE VIEW IF NOT EXISTS Check_consistency AS
    WITH
        Distance_check AS (
            SELECT COUNT(*) > 0 AS distance_count
            FROM Distances
            WHERE det_1 >= det_2
        ),
        
        Min_distance_check AS (
            SELECT COUNT(NULLIF(
                IFNULL(Detections.min_distance, 0) <> IFNULL(T0.min_distance, 0)
                , 0)) AS min_distance_count
            FROM Detections INNER JOIN (
                SELECT
                    Detections.frame,
                    Detections.tracking_id,
                    MIN(Distances.distance) AS min_distance
                FROM Detections LEFT JOIN Distances ON Distances.frame = Detections.frame
                    AND (Distances.det_1 = Detections.tracking_id OR Distances.det_2 = Detections.tracking_id)
                GROUP BY Detections.frame, Detections.tracking_id
            ) AS T0 ON Detections.frame = T0.frame AND Detections.tracking_id = T0.tracking_id
        )

    SELECT
        IIF(distance_count > 0, -- Replace IF with IIF for SQLite
            distance_count || ' redundant or invalid distances found',
            'OK'
        ) AS distance_result,
        IIF(min_distance_count > 0, -- Replace IF with IIF for SQLite
            min_distance_count || ' cached min. distances are inconsistent',
            'OK'
        ) AS min_distance_result
    FROM Distance_check, Min_distance_check;""")

    database.commit()
    cursor.close()


# For db versions < 2.2 ========================================================
if version < 2.2 :
    with open('../statistics.sql', 'r') as f :
        database.executescript(f.read())


# Finalize upgrade =============================================================
cursor = database.cursor()
cursor.execute("INSERT INTO Meta(db_version) VALUES (?);", (LATEST_VERSION,))
database.commit()
cursor.close()

print(f"Upgrade to version {LATEST_VERSION:.1f} successful!")
