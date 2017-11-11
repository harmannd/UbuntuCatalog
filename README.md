# ubuntuCatalog 50.17.79.37:2200 http://catalogapponline.com/

### Software
   * sudo apt-get install apache2
   * sudo apt-get install libapache2-mod-wsgi
   * sudo apt-get -qqy install python python-pip
   * sudo pip2 install --upgrade pip
   * sudo -H pip2 install flask packaging oauth2client redis passlib flask-httpauth
   * sudo -H pip2 install sqlalchemy flask-sqlalchemy psycopg2 bleach
   * sudo -H pip2 install requests
   * sudo apt-get install git
   * sudo apt-get update
   * sudo apt-get upgrade
   * sudo apt install unattended-upgrades
   * sudo -H unattended-upgrade -d
   
### Third-party Tutorials/References
   * DigitalOcean 
      * https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps
      * https://www.digitalocean.com/community/tutorials/how-to-secure-postgresql-on-an-ubuntu-vps
   * Flask Docs
      * http://flask.pocoo.org/docs/0.12/deploying/mod_wsgi/
   * SQLAlchemy Docs
      * http://docs.sqlalchemy.org/en/latest/core/engines.html
   * PostgreSQL Docs
      * https://www.postgresql.org/docs/8.0/static/sql-createuser.html
   * Udacity Forums 
   * StackOverflow

### Amazon setup
   * 50.17.79.37 public static IP 
   * Ports open: 80, 123, 2200
   
### Grader sudo 
   * sudo touch /etc/sudoers.d/grader
   * sudo nano /etc/sudoers.d/grader
      * grader ALL=(ALL) NOPASSWD:ALL
   
### Server access
   * ubuntu login
      * ssh ubuntu@50.17.79.37 -p 2200 -i ~/.ssh/LightsailKey.pem
      * public key in ubuntu/.ssh/authorized_keys
      * chmod 700 .ssh
      * chmod 644 .ssh/authorized_keys
   * grader login
      * ssh grader@50.17.79.37 -p 2200 -i ~/.ssh/ubuntuserver
      * public key in grader/.ssh/authorized_keys
      * chmod 700 .ssh
      * chmod 644 .ssh/authorized_keys
   * force key authentication
      * sudo nano /etc/ssh/sshd_config
         * Change to no to disable tunnelled clear text passwords
            * PasswordAuthentication no
         * What ports, IPs and protocols we listen for 
            * port 2200

### Ubuntu ufw (firewall)
   * sudo ufw default deny incoming
   * sudo ufw default allow outgoing
   * sudo ufw allow www
   * sudo ufw allow 123/tcp
   * sudo ufw allow 2200/tcp
   * sudo ufw enable
   * sudo ufw status
   
### Apache
   * /etc/apache2/sites-enabled/ubuntuCatalog.conf
      * <VirtualHost *:80>
          ServerName 50.17.79.37
          WSGIScriptAlias / /var/www/ubuntuCatalog/ubuntuCatalog.wsgi
          <Directory /var/www/ubuntuCatalog/>
                  Order allow,deny
                  Allow from all
          </Directory>
          Alias /static /var/www/ubuntuCatalog/ubuntuCatalog/static
          <Directory /var/www/ubuntuCatalog/ubuntuCatalog/static/>
                  Order allow,deny
                  Allow from all
          </Directory>
          ErrorLog ${APACHE_LOG_DIR}/error.log
          LogLevel warn
          CustomLog ${APACHE_LOG_DIR}/access.log combined
      </VirtualHost>
   * /var/www/ubuntuCatalog/ubuntuCatalog.wsgi
      #!/usr/bin/python
      import sys
      import logging
      logging.basicConfig(stream=sys.stderr)
      sys.path.insert(0,"/var/www/ubuntuCatalog")

      from ubuntuCatalog import app as application
      application.secret_key = 'super_secret_key'
   * sudo a2ensite ubuntuCatalog
   * sudo service apache2 restart
      
### PostgreSQL
   * setup postgres user with password
      * sudo -u postgres psql template1
      * alter user postgres with encrypted password 'xxxxxxxx';
      * sudo nano /etc/postgresql/9.5/main/pg_hba.conf
         * local all postgres md5
      * sudo /etc/init.d/postgresql restart
   * setup catalog user
      * create user catalog with password 'catalog';
      * \du
   * setup database
      * create database catalogdb with owner catalog;
      * \c catalogdb
      * revoke all on schema public from public;
      * grant all on schema public to catalog;
      * engine = create_engine('postgresql://catalog:catalog@localhost/catalogdb')
      * sudo python database_setup.py
      * sudo python fill_database.py
      
### Error checking
   * sudo nano /var/log/apache2/error.log
   * systemctl status apache2.service
