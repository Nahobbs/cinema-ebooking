# Cinema-eBooking
Term project for CSCI 6050 at the University of Georgia

Prerequisites:
  1) Python 3.6 or greater
  2) Project Configurations
     1) Create a file called `config.yaml` in `cinema-ebooking` directory.
     2) Copy `config.example.yaml` into `config.yaml` and fill in any missing configurations.
     3) If you plan on pushing to repository, please put `config.yaml` in `.gitignore`.
  3) MySQL Database
     1) Ensure that MySQL Server and Client are installed on your machine.
     2) Initialize the database schema by running `/database_population/cinematables.sql` in your MySQL client.
     3) Ensure that `db_auth` section in `config.yaml` matches the credentials for your local instance.
  
Setting up the project:
  
  1. Virtual Environment  
  `$ cd path/to/cinema-ebooking`  
  `$ pip install virtualenv`  
  `$ virtualenv venv`  
  `$ source venv/bin/activate`
  2. Installing Dependencies  
  `$ pip install -r requirements.txt`


Running the project:   

Unix:

  `$ export FLASK_APP=cinema`    
  `$ export FLASK_ENV=development`  
  `$ flask run`    
  
Windows (Powershell):

  `$ set FLASK_APP=cinema`    
  `$ set FLASK_ENV=development`  
  `$ flask run`    
