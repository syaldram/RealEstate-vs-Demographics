# save this as app.py
from flask import Flask

app = Flask(__name__)

def make_bold(function):
    def wrapper1():
        return "<b>" + function() + "</b>"
    return wrapper1

def make_emphasis(function):
    def wrapper2():
        return "<em>" + function() + "</em>"
    return wrapper2

def make_underlined(function):
    def wrapper3():
        return "<u>" + function() + "</u>"
    return wrapper3


@app.route("/")
def hello():
    return '<h1 style="text-align: center">Hello, World!</h1>'\
            '<p>This is a paragraph</p>'\
            '<img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbDJxbDEyc20xcm5lNjNvcGZ0dDE2NmdxdHdhMmlkZnprdXV0azhjcCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/dg0hVakNxI0LaIQDQm/giphy-downsized-large.gif" width=600>'
            


@app.route("/bye")
@make_bold
@make_emphasis
@make_underlined
def say_bye():
    return "bye"

@app.route("/username/<name>/<int:number>")
def greet(name, number):
    return f"hello {name}, you are {number} years old!"
