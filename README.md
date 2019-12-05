# Multiplayer-Game-Server

A web app which supports multiplayer gaming.

<<<<<<< HEAD
### Setting up Virtual Environment and Install Requirements
```bash
sudo pip install virtualenv
python3 -m venv flaskenv
source flaskenv/bin/activate
pip install -r requirements.txt
```
=======
>>>>>>> c0140eef5dbe53475e4804ea15a55dce663ac9a4

### Setting up MySQL 
```bash
sudo mysql_secure_installation
sudo apt install mysql-server-5.7
sudo mysql_secure_installation
mysql -u root -p
#enter your password when prompted
mysql > source db_config.sql 
mysql > quit
exit
```

### Setting up Virtual Environment and Install Requirements
```bash
sudo pip install virtualenv
python3 -m venv myvenv
source myvenv/bin/activate
pip install -r requirements.txt
```

### Running the project
```bash
python server.py
```
