import requests
import os
from flask import Flask, render_template, request
from datetime import datetime, timedelta

def get_headers():
    token = os.getenv("TOKEN")
    if not token:
        print("\u274c Ошибка: Токен не найден в переменных окружения!")
    return {"Authorization": f"Bearer {token}"}

app = Flask(__name__, template_folder="templates")

SCHOOL_ID = "1006693"
EDU_YEAR = "2024"
STUDENT_GROUP_UUID = "2666df86-ee3e-4d22-aa76-052f3fedf057"
HOMEWORK_URL = f"https://api.bilimclass.kz/api/v4/os/clientoffice/homeworks/monthly/list?schoolId={SCHOOL_ID}&eduYear={EDU_YEAR}&studentGroupUuid={STUDENT_GROUP_UUID}"

def get_homework():
    response = requests.get(HOMEWORK_URL, headers=get_headers())
    try:
        data = response.json()
        if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
            return data["data"]
    except Exception as e:
        print("\u274c Ошибка при разборе JSON (ДЗ):", e)
    return []

def filter_homework_by_date(homeworks, date):
    return [hw for hw in homeworks if hw.get("date") == date]

@app.route("/", methods=["GET", "POST"])
def index():
    homeworks = get_homework()
    if not homeworks:
        return "\u274c Ошибка: API не вернуло домашнее задание!", 500

    subjects = {hw["subjectName"]: True for hw in homeworks if "subjectName" in hw}
    
    today = datetime.today().strftime("%d.%m.%Y")
    yesterday = (datetime.today() - timedelta(days=1)).strftime("%d.%m.%Y")
    
    homeworks_today = filter_homework_by_date(homeworks, today)
    homeworks_yesterday = filter_homework_by_date(homeworks, yesterday)
    
    selected_subject = request.form.get("subject")
    filtered_homeworks = [hw for hw in homeworks if hw.get("subjectName") == selected_subject] if selected_subject else []
    
    return render_template(
        "index.html",
        subjects=subjects,
        selected_subject=selected_subject,
        homeworks=filtered_homeworks,
        homeworks_today=homeworks_today,
        homeworks_yesterday=homeworks_yesterday
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
