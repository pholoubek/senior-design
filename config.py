import os
#from dotenv import load_dotenv

#  Store crucial data to the app in ./.env file and add it to the .gitignore
basedir = os.path.abspath(os.path.dirname(__file__))
#load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
   

