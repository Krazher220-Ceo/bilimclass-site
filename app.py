from flask import Flask, render_template, request
import requests
import os
from datetime import datetime, timedelta

app = Flask(__name__, template_folder="templates")

TOKEN = os.getenv("TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

SCHOOL_ID = "1006693"
EDU_YEAR = "2024"
STUDENT_GROUP_UUID = "2666df86-ee3e-4d22-aa76-052f3fedf057"

SCHEDULE_URL = f"https://api.bilimclass.kz/api/v4/os/clientoffice/schedule?schoolId={SCHOOL_ID}&eduYear={EDU_YEAR}&studentGroupUuid={STUDENT_GROUP_UUID}"
HOMEWORK_URL = f"https://api.bilimclass.kz/api/v4/os/clientoffice/homeworks/monthly/list?schoolId={SCHOOL_ID}&eduYear={EDU_YEAR}&studentGroupUuid={STUDENT_GROUP_UUID}"


def get_schedule():
    """🔹 Получает расписание с API BilimClass"""
    response = requests.get(SCHEDULE_URL, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []


def get_homework():
    """🔹 Получает домашнее задание с API BilimClass"""
    response = requests.get(HOMEWORK_URL, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []


def match_homework(schedule, homeworks):
    """🔹 Сопоставляет расписание и ДЗ"""
    hw_dict = {hw["date"]: hw for hw in homeworks}  # ДЗ по дате
    today = datetime.today().strftime("%d.%m.%Y")  # Текущая дата

    for lesson in schedule:
        lesson_date = lesson["date"]
        subject = lesson["subjectName"]

        previous_date = (datetime.strptime(lesson_date, "%d.%m.%Y") - timedelta(days=1)).strftime("%d.%m.%Y")

        next_date = (datetime.strptime(lesson_date, "%d.%m.%Y") + timedelta(days=1)).strftime("%d.%m.%Y")

        if previous_date in hw_dict and hw_dict[previous_date]["subjectName"] == subject:
            lesson["homework"] = hw_dict[previous_date]["body"]
        elif lesson_date == today and next_date in hw_dict and hw_dict[next_date]["subjectName"] == subject:
            lesson["homework"] = hw_dict[next_date]["body"]
        else:
            lesson["homework"] = "📌 Нет ДЗ"

    return schedule


@app.route("/", methods=["GET", "POST"])
def index():
    schedule = get_schedule()
    homeworks = get_homework()
    schedule_with_hw = match_homework(schedule, homeworks)

    subjects = sorted(set(lesson["subjectName"] for lesson in schedule_with_hw))

    selected_subject = request.form.get("subject")
    filtered_schedule = [lesson for lesson in schedule_with_hw if lesson["subjectName"] == selected_subject] if selected_subject else schedule_with_hw

    return render_template("index.html", subjects=subjects, schedule=filtered_schedule, selected_subject=selected_subject)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
