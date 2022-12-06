/* This script can generate an empty sqlite database ready for use with Dista.
   
   You can generate a db diagram with https://dbdiagram.io/d
   (or using the built-in diagram tool of DBeaver)
   
   Version history:
   3.2 Added archive tables
   3.1 Minor updates to heatmap view and frames on update
   3.0 New format with cached data
   2.3 Refactored basic statistics views into a separate file and updated heatmap
   2.2 Major schema update to Machines, Cameras and Sessions to better fit new code paths
   2.1 Minor adjustments to facilitate SQLite compatibility
   2.0 Migrated to MySQL 14 (while remaining compatible with earlier SQLite dbs)
   1.6 Backport of version 2.0 (MySQL) to maintain retro-compability with SQLite
   1.5 Changed timestamp format from julianday to unixepoch and added Sessions
   1.4 Separated cameras and machines
   1.3 Updated for 3d coordinates
   1.2 Added stricter constraints
   1.1 Implemented proper FK constraints
   1.0 Created initial table structure
 */


/* This table helps keep track of which database revision we're dealing with. */
CREATE TABLE Meta (
    db_version VARCHAR(255),
    db_creation DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO Meta(db_version) VALUES ('3.1');


CREATE TABLE Machines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    address VARCHAR(1024) NOT NULL, -- network address (ip or hostname)
    name VARCHAR(255), -- friendly identifier (eg. Xavier3)
    location VARCHAR(255) -- physical location of the machine
);

CREATE INDEX address_idx ON Machines(address);

/*
INSERT INTO Machines(address, name)
VALUES ('127.0.0.1', 'localhost');      -- 'Self' (host) machine
*/


CREATE TABLE Placements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pos_x INTEGER DEFAULT 0, -- 'absolute' position of camera
    pos_y INTEGER DEFAULT 0, -- (expressed in cm)
    pos_z INTEGER DEFAULT 0, -- (where z is height)
    rot_x DOUBLE DEFAULT 0, -- 'absolute' angle of camera
    rot_y DOUBLE DEFAULT 0, -- (expressed in degrees)
    rot_z DOUBLE DEFAULT 0, -- (relative to each axis)
    vflip BOOL DEFAULT 0 -- is the camera mounted upside-down?
);

/*
INSERT INTO Placements(id) VALUES (0);  -- Identity transform (ie. no placement data)
*/
CREATE TABLE Cameras ( -- TODO many of the properties below should be links to constants
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model VARCHAR(255), -- camera type (Zed2, Nanocam, custom...)
    serial VARCHAR(255) NOT NULL, -- serial number (or calibration file name)
    protocol VARCHAR(255), -- communication mode (eg. Zed or OpenCV)
    resolution VARCHAR(255), -- either named or numeric resolution
    location VARCHAR(255), -- physical location of the camera
    placement INTEGER NULL, -- camera placement information (if available)
    machine INTEGER NULL, -- host machine id (if networked)
    port_no SMALLINT(5), -- port number or device id assigned to this camera
    FOREIGN KEY (placement) REFERENCES Placements(id),
    FOREIGN KEY (machine) REFERENCES Machines(id)
);

CREATE INDEX serial_idx ON Cameras(serial);

/*
INSERT INTO Cameras(serial) VALUES ('dummy'); -- Default camera for testing and debugging
*/


/* These tables are meant to allow grouping cameras together (for usability). */
CREATE TABLE Camera_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description VARCHAR(255)
);

CREATE TABLE Group_memberships (
    camera_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    PRIMARY KEY (camera_id,group_id),
    
    FOREIGN KEY (camera_id) REFERENCES Cameras(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    
    FOREIGN KEY (group_id) REFERENCES Camera_groups(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);


/* This is a substitute for a legacy table from versions <1.4, but we keep using it... */
CREATE VIEW Camera_configurations AS
SELECT
    Cameras.id AS id, -- PRIMARY KEY
    COALESCE(Cameras.model, Machines.name, 'cam') || ' ' 
        || COALESCE(Cameras.location, Machines.location, Cameras.serial)
        AS description, -- NOT NULL
    Cameras.serial AS cam_serial, -- NOT NULL
    -- TODO Add groups here (in a single field)
    Machines.address || ':' || Cameras.port_no AS ip_address,
    Cameras.resolution AS resolution,
    Placements.pos_x, Placements.pos_y, Placements.pos_z,
    Placements.rot_x, Placements.rot_y, Placements.rot_z
FROM Cameras
    LEFT JOIN Machines ON Cameras.machine = Machines.id
    LEFT JOIN Placements ON Cameras.placement = Placements.id;


/* This is a meta-information table to help group data in sessions if needed. */
CREATE TABLE Sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- PK: session identifier
    started_at TIMESTAMP NOT NULL DEFAULT (strftime('%s', 'now')),
    command_args TEXT NOT NULL, -- Command line arguments used when starting session
    compute_stereo BOOL DEFAULT 1, -- Are we computing the depthmap using stereoscopy?
    obj_categories VARCHAR(255), -- Efficient_det object categories for detection
    net_scale TINYINT(2), -- Efficient_det compound coefficient (0, 1, etc.)
    comments TEXT -- Optional comment to describe session
);


CREATE TABLE Frames (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- PK: frame identifier
    created_by INTEGER, -- In versions 1.4 to 2.1, this field was the cam_serial instead
    created_at TIMESTAMP NOT NULL DEFAULT (strftime('%s', 'now')),
        -- Despite being displayed as a date, this is internally an INT(11) field (or more in later versions)
    duration SMALLINT(3) DEFAULT 1, -- Duration of the frame in ms
    image_path VARCHAR(1024), -- Path to saved frame image, if any
    
    FOREIGN KEY (created_by) REFERENCES Cameras(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);


CREATE TABLE Detections (
    frame INTEGER, -- FK: id of the parent frame
    tracking_id INTEGER, -- 'tracked id' of the detection
    category TINYINT(2), -- efficient det category identifier
    pos_x INTEGER, -- 'absolute' position of detection
    pos_y INTEGER, -- (expressed in cm)
    pos_z INTEGER NULL, -- (optional)
    min_distance INTEGER NULL, -- cached field: distance to nearest neighbor
    
    PRIMARY KEY (frame,tracking_id),
    
    FOREIGN KEY (frame) REFERENCES Frames(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);


/* Distance measurements are optional, since they can be re-computed. */
CREATE TABLE Distances (
    frame INTEGER, -- FK: id of the parent frame
    det_1 INTEGER, -- FK: id of the first detection involved
    det_2 INTEGER, -- FK: id of the second detection involved
    distance INTEGER NOT NULL, -- distance between a pair of detections (in cm)
    
    FOREIGN KEY (frame,det_1) REFERENCES Detections(frame,tracking_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    
    FOREIGN KEY (frame,det_2) REFERENCES Detections(frame,tracking_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);


/* This view helps monitor the latest detections recorded in the current session. */
CREATE VIEW Latest_detections AS
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
GROUP BY frame_id, detection_id;


/* SQLite doesn't support stored procedures, so this view is used to create the heatmap;
   This version of the heatmap view reports the position of every person at every frame. */
CREATE VIEW Heatmap AS
SELECT
    local_time,
    camera_desc,
    frame_id || '-' || detection_id AS detection_id,
    pos_x/100.0 AS pos_X, pos_y/100.0 AS pos_Y, -- Display positions in m
    max(1.0 - IFNULL(min_distance / 200.0, 1.0), 0.0) AS collision_intensity
FROM Latest_detections;


/* There's no trigger checking these constraints, so you can run this to verify they're respected. */
/* TODO Add checks for frame duration (compared to timestamps -- less than). */
CREATE VIEW Check_consistency AS
WITH
    Distance_check AS (
        SELECT COUNT(*) > 0 AS distance_count
        FROM Distances
        WHERE det_1 >= det_2
    ),
    
    Min_distance_check AS (
        SELECT COUNT(NULLIF(
            IFNULL(Detections.min_distance, 0) <> IFNULL(T0.min_distance, 0),
            0)) AS min_distance_count
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
    IIF(distance_count > 0,
        distance_count || ' redundant or invalid distances found',
        'OK'
    ) AS distance_result,
    IIF(min_distance_count > 0,
        min_distance_count || ' cached min. distances are inconsistent',
        'OK'
    ) AS min_distance_result
FROM Distance_check, Min_distance_check;

