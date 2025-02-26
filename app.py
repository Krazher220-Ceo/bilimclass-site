from flask import Flask, render_template, request
import requests

app = Flask(__name__)

import os

TOKEN = os.getenv("TOKEN")

URL = "https://api.bilimclass.kz/api/v4/os/clientoffice/homeworks/monthly/list"
PARAMS = {
    "schoolId": 1006693,
    "eduYear": 2024,
    "studentGroupUuid": "2666df86-ee3e-4d22-aa76-052f3fedf057"
}
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def get_schedule():
    response = requests.get(URL, headers=HEADERS, params=PARAMS)
    if response.status_code == 200:
        data = response.json().get("data", [])
        subjects = sorted(set(task.get("subjectName", "Неизвестный предмет") for task in data))
        return subjects, data
    return [], []

@app.route("/", methods=["GET", "POST"])
def index():
    subjects, data = get_schedule()
    selected_subject = None
    schedule = []

    if request.method == "POST":
        selected_subject = request.form.get("subject")
        schedule = [task for task in data if task.get("subjectName") == selected_subject]

    return render_template("index.html", subjects=subjects, selected_subject=selected_subject, schedule=schedule)

if __name__ == "__main__":
    app.run(debug=True)

