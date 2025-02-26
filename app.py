import requests
import os
from flask import Flask, render_template, request, session
from datetime import datetime, timedelta

app = Flask(__name__, template_folder="templates")
app.secret_key = "supersecretkey"  # Для сессий

# 🔹 API-токен и заголовки
TOKEN = os.getenv("TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# 🔹 Данные для API
SCHOOL_ID = "1006693"
EDU_YEAR = "2024"
STUDENT_GROUP_UUID = "2666df86-ee3e-4d22-aa76-052f3fedf057"

# 🔹 URL для получения ДЗ и расписания
HOMEWORK_URL = f"https://api.bilimclass.kz/api/v4/os/clientoffice/homeworks/monthly/list?schoolId={SCHOOL_ID}&eduYear={EDU_YEAR}&studentGroupUuid={STUDENT_GROUP_UUID}"
SCHEDULE_URL = f"https://api.bilimclass.kz/api/v4/os/clientoffice/timetable/daily/list?schoolId={SCHOOL_ID}&eduYear={EDU_YEAR}&studentGroupUuid={STUDENT_GROUP_UUID}"

def get_homework():
    """🔹 Получает домашнее задание с API BilimClass"""
    response = requests.get(HOMEWORK_URL, headers=HEADERS)

    print("📌 Ответ API (ДЗ):", response.text)  # ВАЖНО: смотрим, что реально приходит
    
    try:
        data = response.json()
        return data.get("data", [])  # Получаем список заданий
    except Exception as e:
        print("❌ Ошибка при разборе JSON:", e)
        return []

def get_schedule(date):
    """🔹 Получает расписание уроков на указанную дату"""
    try:
        response = requests.get(SCHEDULE_URL + f"&date={date}", headers=HEADERS)
        data = response.json()
        if isinstance(data, dict) and "data" in data:
            return [lesson["subjectName"] for lesson in data["data"]]
    except Exception as e:
        print("❌ Ошибка при разборе JSON (расписание):", e)
    return []

@app.route("/", methods=["GET", "POST"])
def index():
    homeworks = get_homework()

    if not homeworks:
        return "❌ Ошибка: API не вернуло домашнее задание!", 500

    # 🔹 Получаем список предметов с ДЗ
    subjects = sorted(set(hw["subjectName"] for hw in homeworks if "subjectName" in hw))

    # 🔹 Даты для фильтрации
    today = datetime.today().strftime("%d.%m.%Y")
    yesterday = (datetime.today() - timedelta(days=1)).strftime("%d.%m.%Y")
    tomorrow = (datetime.today() + timedelta(days=1)).strftime("%d.%m.%Y")

    # 🔹 Фильтрация ДЗ
    homeworks_today = [hw["content"] for hw in homeworks if hw.get("date") == today]
    homeworks_yesterday = [hw["content"] for hw in homeworks if hw.get("date") == yesterday]

    # 🔹 Проверка, есть ли ДЗ на завтра
    subjects_tomorrow = {hw["subjectName"]: hw["date"] == tomorrow for hw in homeworks}

    # 🔹 Фильтрация ДЗ по выбранному предмету
    selected_subject = request.form.get("subject")
    filtered_homeworks = [
        hw["content"] for hw in homeworks if hw.get("subjectName") == selected_subject
    ] if selected_subject else []

    # 🔹 Получаем расписание на завтра
    schedule_tomorrow = get_schedule(tomorrow)

    # 🔹 Считаем просмотры
    session["views"] = session.get("views", 0) + 1

    return render_template(
        "index.html",
        subjects=subjects_tomorrow,
        selected_subject=selected_subject,
        homeworks=filtered_homeworks,
        homeworks_today=homeworks_today,
        homeworks_yesterday=homeworks_yesterday,
        schedule_tomorrow=schedule_tomorrow,
        views=session["views"]
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)











