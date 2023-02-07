/* This file contains stored procedures which can help compute statistics from the data;
It is also intended to serve as an example from which to build more complex queries. */

DELIMITER $$


/* Utility functions to grab the last frame or session timestamp =========== */
DROP FUNCTION IF EXISTS latest_session;
CREATE FUNCTION latest_session() RETURNS TIMESTAMP DETERMINISTIC
BEGIN
    RETURN (SELECT started_at FROM Sessions ORDER BY id DESC LIMIT 1);
END $$

DROP FUNCTION IF EXISTS latest_frame;
CREATE FUNCTION latest_frame() RETURNS TIMESTAMP DETERMINISTIC
BEGIN
    RETURN (SELECT created_at FROM Frames ORDER BY id DESC LIMIT 1);
END $$


/* Cache prepared statements for better performance ======================== */
SET @stats_template :=
'SELECT
    FROM_UNIXTIME(
        (UNIX_TIMESTAMP(time) DIV ?) * ?
        -- UNIX_TIMESTAMP(time) - MOD(UNIX_TIMESTAMP(time), ?) TODO profile
    ) AS timeslice,
    camera,
    AVG(??) AS ??
FROM ??_per_second
WHERE time >= ?
 -- AND FIND_IN_SET(camera, ?) > 0 (this works but is not worth the performance hit)
GROUP BY timeslice, camera;';

SET @stats_query := REPLACE(@stats_template, '??', 'nb_detections');
PREPARE stmt_nb_detections FROM @stats_query;

SET @stats_query := REPLACE(@stats_template, '??', 'avg_distance');
PREPARE stmt_avg_distance FROM @stats_query;

SET @stats_query := REPLACE(@stats_template, '??', 'nb_collisions');
PREPARE stmt_nb_collisions FROM @stats_query;

SET @stats_query := REPLACE(@stats_template, '??', 'avg_closest_neighbor');
PREPARE stmt_avg_closest_neighbor FROM @stats_query;

SET @stats_query := REPLACE(@stats_template, '??', 'nb_colliding_detections');
PREPARE stmt_nb_colliding_detections FROM @stats_query;


/* Use this function to aggregate data in time "slices" to reduce dataset size.
Note: This is pretty neat, but frankly it would be simpler and more flexible to just
create prepared statements in the client code rather than using this procedure. */
DROP PROCEDURE IF EXISTS latest_statistics;
CREATE PROCEDURE latest_statistics(
    stat_name VARCHAR(255), -- Short name of the view providing the basic statistics
                            --  Example: 'avg_closest_neighbor'
    time_span TIME,         -- Optional: restrict data to a limited timeframe (eg. '1:00:00')
                            --  Default: include all data collected in lastest session
    nb_slices INTEGER       -- Optional: if positive, batch statistics in n time slices
                            --           if negative, batch statistics in fixed length slices
                            --  Default: use fixed length slices of 60 seconds (ie. '-60')
)
BEGIN
    DECLARE start_time TIMESTAMP;
    DECLARE slice_length INTEGER;
    
    SET start_time = IFNULL(SUBTIME(latest_frame(), time_span), latest_session());
    
    SET slice_length = CASE
        WHEN nb_slices > 0
            THEN TIMESTAMPDIFF(SECOND, latest_frame(), start_time) DIV nb_slices
        WHEN nb_slices < 0
            THEN -nb_slices
        ELSE 60
    END;
    
    CASE stat_name
        WHEN 'nb_detections' THEN
            EXECUTE stmt_nb_detections USING @slice_length, @slice_length, @start_time;
        WHEN 'avg_distance' THEN
            EXECUTE stmt_avg_distance USING @slice_length, @slice_length, @start_time;
        WHEN 'nb_collisions' THEN
            EXECUTE stmt_nb_collisions USING @slice_length, @slice_length, @start_time;
        WHEN 'avg_closest_neighbor' THEN
            EXECUTE stmt_avg_closest_neighbor USING @slice_length, @slice_length, @start_time;
        WHEN 'nb_colliding_detections' THEN
            EXECUTE stmt_nb_colliding_detections USING @slice_length, @slice_length, @start_time;
        ELSE
            BEGIN
                SET @stats_query := REPLACE(@stats_template, '??', stat_name);
                PREPARE temp_stmt FROM @stats_query;
                EXECUTE temp_stmt USING @slice_length, @slice_length, @start_time;
                DEALLOCATE PREPARE temp_stmt;
            END;
    END CASE;
END $$

/* To call this procedure, use
CALL latest_statistics('nb_detections_or_some_other_stat', '24:00:00', 1000);
You can use the default parameter values by passing in NULL instead. */


/* Use this function to process the data so it can be used to create a heatmap. */
DROP PROCEDURE IF EXISTS tiled_heatmap;
CREATE PROCEDURE tiled_heatmap(
    time_span TIME,         -- Optional: restrict data to a limited timeframe (eg. '1:00:00')
                            --  Default: include all data collected in lastest session
    nb_slices INTEGER,      -- Optional: if positive, batch statistics in n time slices
                            --           if negative, batch statistics in fixed length slices
                            --  Default: use fixed length slices of 60 seconds (ie. '-60')
    tile_size INTEGER       -- Optional: size of each (square) tile in x,y space (in cm)
                            --  Default: 30 cm (~12 in)
)
BEGIN
    DECLARE start_time TIMESTAMP;
    DECLARE slice_length INTEGER;
    
    SET start_time = IFNULL(SUBTIME(latest_frame(), time_span), latest_session());
    
    SET slice_length = CASE
        WHEN nb_slices > 0
            THEN TIMESTAMPDIFF(SECOND, latest_frame(), start_time) DIV nb_slices
        WHEN nb_slices < 0
            THEN -nb_slices
        ELSE 60
    END;
    
    SET tile_size = IFNULL(tile_size, 30);
    
    SELECT
        FROM_UNIXTIME(
            (UNIX_TIMESTAMP(local_time) DIV slice_length) * slice_length
        ) AS timeslice,
        tile_x, tile_y,
        AVG(nb_detections_per_frame) AS nb_detections,
        IFNULL(200.0 / AVG(avg_min_distance_per_frame), 0.0) AS promiximity_coeff
    FROM (
        SELECT
            frame_id,
            local_time,
            (pos_x DIV tile_size) * tile_size AS tile_x,
            (pos_y DIV tile_size) * tile_size AS tile_y,
            COUNT(detection_no) AS nb_detections_per_frame,
            AVG(min_distance) AS avg_min_distance_per_frame
        FROM Latest_detections
        WHERE local_time >= start_time
        GROUP BY frame_id, local_time, tile_x, tile_y
    ) AS T1
    GROUP BY timeslice, tile_x, tile_y;
END $$

/* To call this procedure, use
CALL tiled_heatmap('24:00:00', 1000, 10);
You can use the default parameter values by passing in NULL instead. */


DELIMITER ;
