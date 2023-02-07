/* Run these commands after installing MySQL to create default users on the server;
   See https://www.digitalocean.com/community/tutorials/how-to-create-a-new-user-and-grant-permissions-in-mysql */
   
CREATE USER 'dista'@'%' IDENTIFIED BY 'dista-SQL';
GRANT ALL PRIVILEGES ON `dista%`.* TO 'dista'@'%'; -- yes, those _must be_ backticks

CREATE USER 'logisticam'@'%' IDENTIFIED BY 'logisticam-SQL';
GRANT SELECT ON `dista%`.* TO 'logisticam'@'%';

FLUSH PRIVILEGES;
SHOW GRANTS FOR dista;
SHOW GRANTS FOR logisticam;


/* Then we'll create and prepare two default databases: */
CREATE DATABASE dista-test; -- use this database while testing
USE dista-test;
source schema_mysql.sql;
source statistics.sql;

CREATE DATABASE dista-main; -- and this one for deployments
USE dista-main;
source schema_mysql.sql;
source statistics.sql;

