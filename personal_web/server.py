from flask import Flask, render_template
import random
import datetime
import requests

today = datetime.date.today()

year = today.year

app = Flask(__name__)

@app.route("/")
def home():
    random_number = random.randint(1, 10)
    return render_template('index.html',num=random_number, year=year)

@app.route("/guess/<name>")
def guess(name):
    gender_url = f'https://api.genderize.io?name={name}'
    gender_response = requests.get(gender_url)
    gender_data = gender_response.json() # Convert the response to JSON
    gender = gender_data['gender']
    age_url = f'https://api.agify.io?name={name}'
    age_response = requests.get(age_url)
    age_data = age_response.json() # Convert the response to JSON
    age = age_data['age']
    #age = gender_data['age']
    return render_template("guess.html", person_name=name, gender=gender,age=age)



if __name__ == "__main__":
    app.run()