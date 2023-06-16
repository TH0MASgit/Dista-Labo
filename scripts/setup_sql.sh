#!/bin/bash
# This script will install sqlite and mysql for use with dista

# SQLite is sometimes installed by default but not always
sudo apt install -y sqlite3 && echo 'alias sqlite=sqlite3' >> ~/.bash_aliases
sudo apt install sqlitebrowser


# Installing MySQL isn't necessary but it can be useful while developing
read -t 10 -p "Would you like to install and configure MariaDB? [y/N] " ; echo
if [[ "$REPLY" =~ ^[Yy]([Ee][Ss])?$ ]]
then
    # See https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-18-04
    sudo apt install -y mariadb-server && sudo mysql_secure_installation
    # (and then follow the interactive prompts)
    
    # To connect to MySQL, run:
    #mysql [-u username (defaults to $USER)] [-h host (defaults to localhost)] -p[assword] database_name
    
    until mysql -u root -p -e "SELECT CURRENT_USER();" ; do
        read -e -r -p "Connection to MySQL failed; try to reset the password: "
        sudo mysql -e "ALTER USER 'root'@'localhost' \
            IDENTIFIED WITH mysql_native_password BY '$REPLY'";
    done
    
    # Setup the default users and database
    cd "$(dirname "$0")"
    mysql -u root -p < ../logisticam/db/init_mysql.sql
    
    # Open the server to external connections and use utf8 encoding by default
    # https://stackoverflow.com/questions/16287559/mysql-adding-user-for-remote-access
    sudo tee -a /etc/mysql/my.cnf <<END
[client]
default-character-set = utf8

[mysql]
default-character-set = utf8

[mysqld]
character-set-server = utf8
collation-server = utf8_unicode_ci
bind-address = 0.0.0.0 # (or use a specific interface's address if desired)
END

    # Restart the mysql daemon to make sure all our changes are active
    # https://stackoverflow.com/questions/1420839/cant-connect-to-mysql-server-error-111
    sudo service mysql restart
fi

