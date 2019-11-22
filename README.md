# Multiplayer-Game-Server

A web app which supports multiplayer gaming.

### Setting up Virtual Environment and Install Requirements
```bash
sudo pip install virtualenv
python3 -m venv myvenv
source myvenv/bin/activate
pip install -r requirements.txt
```

### Setting up MySQL 
```bash
sudo mysql_secure_installation
mysql -u root -p
#enter your password when prompted
mysql > source db_config.sql
mysql > quit
exit
```

### Running the project
```bash
python server.py
```
