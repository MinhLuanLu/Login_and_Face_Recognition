from flask_sqlalchemy import SQLAlchemy
import random
from datetime import datetime,date


db = SQLAlchemy()


class Account(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    id_created = db.Column(db.String(10))
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    password = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(50))
    date_joined = db.Column(db.String(50))
    profile_pic = db.Column(db.String(255))
    

    def __init__(self,profile_pic, id_created, name, email, password, gender, date_joined):
        self.id_created = id_created
        self.name = name
        self.email = email
        self.password = password
        self.gender = gender
        self.date_joined = date_joined
        self.profile_pic = profile_pic


def generate_id():
    randoms = [random.randint(0, 9) for _ in range(6)]
    id = "#" + "".join(map(str, randoms))
    print(id)
    return id

def get_date(): 
    time = datetime.now()
    today = date.today()
    today = today.strftime("%b-%d-%Y")
    time = time.strftime("%H:%M:%S")
    date_and_time = (today +"-"+ time)
    print("date joined: " + date_and_time)
    return date_and_time

