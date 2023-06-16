-- See https://tableplus.com/blog/2018/08/mysql-how-to-drop-all-tables.html

SET FOREIGN_KEY_CHECKS = 0;

/* First list all tables with this:
SELECT concat('DROP TABLE IF EXISTS `', table_name, '`;')
FROM information_schema.tables
WHERE table_schema = 'dista_test';
*/

DROP TABLE IF EXISTS `Camera_configurations`;
DROP TABLE IF EXISTS `Cameras`;
DROP TABLE IF EXISTS `Detections`;
DROP TABLE IF EXISTS `Distances`;
DROP TABLE IF EXISTS `Frames`;
DROP TABLE IF EXISTS `Latest_detections`;
DROP TABLE IF EXISTS `Machines`;
DROP TABLE IF EXISTS `Meta`;
DROP TABLE IF EXISTS `Sessions`;

/* You can also list all views with 
 * SHOW FULL TABLES WHERE TABLE_TYPE LIKE 'VIEW';
 */
DROP VIEW IF EXISTS `Camera_configurations`;
DROP VIEW IF EXISTS `Latest_detections`;
DROP VIEW IF EXISTS `Heatmap`;

DROP VIEW IF EXISTS `nb_detections_per_second`;
DROP VIEW IF EXISTS `avg_distance_per_second`;
DROP VIEW IF EXISTS `nb_collisions_per_second`;
DROP VIEW IF EXISTS `avg_closest_neighbor_per_second`;
DROP VIEW IF EXISTS `nb_colliding_detections_per_second`;

SET FOREIGN_KEY_CHECKS = 1;

