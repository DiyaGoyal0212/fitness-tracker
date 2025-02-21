from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import users_collection
import subprocess  # To run external Python scripts
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Home Route
@app.route("/")
def home():
    if "user" in session:
        return render_template("home.html", username=session["user"])
    
    flash("Please log in first!", "error")
    return redirect(url_for("login"))  # Redirect if session missing

# Login Route
from datetime import timedelta

app.secret_key = "supersecretkey"
app.permanent_session_lifetime = timedelta(days=1)  # Keep session for 1 day

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = users_collection.find_one({"username": username, "password": password})
        if user:
            session.permanent = True  # Keep session active
            session["user"] = username
            return redirect(url_for("home"))
    
    return render_template("login.html")

# Signup Route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if users_collection.find_one({"username": username}):
            flash("Username already exists!", "error")
        else:
            users_collection.insert_one({"username": username, "password": password})
            flash("Account created! Please log in.", "success")
            return redirect(url_for("login"))

    return render_template("signup.html")

# Logout Route
@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully!", "success")
    return redirect(url_for("login"))

# Route to trigger workouts
scripts = {
    "pushups": "Pushup.py",
    "squats": "Squat.py",
    "bicep_curls": "Bicep Curl.py",
    "lunges": "Lunges.py",
    "situps": "Situps.py"
}

@app.route("/start/<exercise>")
def start_exercise(exercise):
    if exercise in scripts:
        script_path = os.path.join(os.getcwd(), scripts[exercise])
        subprocess.Popen(["python", script_path], shell=True)  # Open the script
        return redirect(url_for("home"))  # Redirect back to home

    return "Exercise not found", 404


@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == "__main__":
    app.run(debug=True)