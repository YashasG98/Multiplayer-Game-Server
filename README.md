# Multiplayer-Game-Server

A web app which supports multiplayer gaming.

### Setting up MySQL 
```bash
sudo apt update
sudo apt install mysql-server libmysqlclient-dev

#setting your password
sudo mysql
mysql > ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'your_new_password';
mysql > FLUSH PRIVILEGES;
mysql > exit

mysql -u root -p
#enter your password when prompted
mysql > source db_config.sql 
mysql > quit
exit
```

### Setting up Virtual Environment and Install Requirements
```bash
sudo pip install virtualenv
python3 -m venv flaskenv
source flaskenv/bin/activate
pip install -r requirements.txt
```

### Running the project

Change your password at line 12 of server.py

```bash
python3 server.py
```

To login and play, use two different browsers, as we use cookies to save user information.
