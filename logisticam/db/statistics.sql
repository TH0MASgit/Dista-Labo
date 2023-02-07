/* This file contains stored procedures which can help compute statistics from the data;
It is also intended to serve as an example from which to build more complex queries. */

-- TODO This 'constants' table is a bit of a hack, we should be using prepared 
-- statements instead of the views below, but that will come in the next version.
CREATE TABLE IF NOT EXISTS Constants (
    id INTEGER PRIMARY KEY, -- placeholder id to allow SQLite / MySQL compatibility
    collision_threshold DOUBLE DEFAULT 200.0 -- collisions happen under 2m (200cm)
);

REPLACE INTO Constants(id) VALUES (0);


/* Basic statistics (averaged per second) ================================== */

/* Total number of people detected (ie. 'detections'). */
CREATE VIEW nb_detections_per_second AS
SELECT
    T1.created_at AS time,
    T1.created_by AS camera,
    AVG(nb_detections_per_frame) AS nb_detections
FROM (
    SELECT
        Frames.id,
        Frames.created_at,
        Frames.created_by,
        COUNT(Detections.tracking_id) AS nb_detections_per_frame
    FROM Frames LEFT JOIN Detections ON Detections.frame = Frames.id
    GROUP BY Frames.id, Frames.created_at, Frames.created_by
) AS T1
GROUP BY time, camera;


/* Average of all distances between all detections. */
CREATE VIEW avg_distance_per_second AS
SELECT
    T1.created_at AS time,
    T1.created_by AS camera,
    AVG(avg_distance_per_frame) AS avg_distance
FROM (
    SELECT
        Frames.id,
        Frames.created_at,
        Frames.created_by,
        AVG(Distances.distance) AS avg_distance_per_frame
    FROM Frames LEFT JOIN Distances ON Distances.frame = Frames.id
    GROUP BY Frames.id, Frames.created_at, Frames.created_by
) AS T1
GROUP BY time, camera;


/* Total number of collisions (distances under 2m) between all detections. */
CREATE VIEW nb_collisions_per_second AS
SELECT
    T1.created_at AS time,
    T1.created_by AS camera,
    AVG(nb_collisions_per_frame) AS nb_collisions
FROM (
    SELECT
        Frames.id,
        Frames.created_at,
        Frames.created_by,
        COUNT(T0.distance) AS nb_collisions_per_frame
    FROM Frames LEFT JOIN (
        SELECT * FROM Distances
        WHERE Distances.distance < (SELECT collision_threshold FROM Constants LIMIT 1)
    ) AS T0 ON T0.frame = Frames.id
    GROUP BY Frames.id, Frames.created_at, Frames.created_by
) AS T1
GROUP BY time, camera;


/* Not so basic statistics ================================================= */

/* Average distance to each detection's closest neighbor. */
CREATE VIEW avg_closest_neighbor_per_second AS
SELECT
    T1.created_at AS time,
    T1.created_by AS camera,
    AVG(avg_closest_neighbor_per_frame) AS avg_closest_neighbor
FROM (
    SELECT
        Frames.id,
        Frames.created_at,
        Frames.created_by,
        AVG(T0.min_distance_per_detection) AS avg_closest_neighbor_per_frame
    FROM Frames LEFT JOIN (
        SELECT
            Detections.frame,
            Detections.tracking_id,
            MIN(Distances.distance) AS min_distance_per_detection
        FROM Detections INNER JOIN Distances ON Distances.frame = Detections.frame
            AND (Distances.det_1 = Detections.tracking_id OR Distances.det_2 = Detections.tracking_id)
        GROUP BY Detections.frame, Detections.tracking_id
    ) AS T0 ON T0.frame = Frames.id
    GROUP BY Frames.id, Frames.created_at, Frames.created_by
) AS T1
GROUP BY time, camera;


/* Number of people involved in at least one collision (closest neighbor under 2m). */
CREATE VIEW nb_colliding_detections_per_second AS
SELECT
    T1.created_at AS time,
    T1.created_by AS camera,
    AVG(nb_colliding_detections_per_frame) AS nb_colliding_detections
FROM (
    SELECT
        Frames.id,
        Frames.created_at,
        Frames.created_by,
        COUNT(T0.tracking_id) AS nb_colliding_detections_per_frame
     -- You could also compute a couple more stats here from this data, such as:
     -- AVG(T0.nb_collisions_per_detection) AS avg_nb_collisions_when_colliding
     -- AVG(T0.avg_collision_distance_per_detection) AS avg_distance_when_colliding
    FROM Frames LEFT JOIN (
        SELECT
            Detections.frame,
            Detections.tracking_id,
            COUNT(Distances.distance) AS nb_collisions_per_detection,
            AVG(Distances.distance) AS avg_collision_distance_per_detection
        FROM Detections INNER JOIN Distances ON Distances.frame = Detections.frame
            AND (Distances.det_1 = Detections.tracking_id OR Distances.det_2 = Detections.tracking_id)
        WHERE Distances.distance < (SELECT collision_threshold FROM Constants LIMIT 1)
        GROUP BY Detections.frame, Detections.tracking_id
    ) AS T0 ON T0.frame = Frames.id
    GROUP BY Frames.id, Frames.created_at, Frames.created_by
) AS T1
GROUP BY time, camera;
