import requests
import os
from flask import Flask, render_template, request
from datetime import datetime, timedelta

app = Flask(__name__, template_folder="templates")

# 🔹 API-токен и заголовки
TOKEN = os.getenv("TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# 🔹 Данные для API
SCHOOL_ID = "1006693"
EDU_YEAR = "2024"
STUDENT_GROUP_UUID = "2666df86-ee3e-4d22-aa76-052f3fedf057"

# 🔹 URL для получения ДЗ
HOMEWORK_URL = f"https://api.bilimclass.kz/api/v4/os/clientoffice/homeworks/monthly/list?schoolId={SCHOOL_ID}&eduYear={EDU_YEAR}&studentGroupUuid={STUDENT_GROUP_UUID}"

def get_homework():
    """🔹 Получает домашнее задание с API BilimClass"""
    response = requests.get(HOMEWORK_URL, headers=HEADERS)
    try:
        data = response.json()
        if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
            return data["data"]
    except Exception as e:
        print("❌ Ошибка при разборе JSON (ДЗ):", e)
    return []

def filter_homework_by_date(homeworks, date):
    """🔹 Фильтрует ДЗ по дате"""
    return [hw for hw in homeworks if hw.get("date") == date]

@app.route("/", methods=["GET", "POST"])
def index():
    homeworks = get_homework()
    
    if not homeworks:
        return "❌ Ошибка: API не вернуло домашнее задание!", 500

    # 🔹 Получаем список предметов
    subjects = sorted(set(hw["subjectName"] for hw in homeworks if "subjectName" in hw))

    # 🔹 Получаем даты
    today = datetime.today().strftime("%d.%m.%Y")
    yesterday = (datetime.today() - timedelta(days=1)).strftime("%d.%m.%Y")

    # 🔹 Фильтруем ДЗ по дате
    homeworks_today = filter_homework_by_date(homeworks, today)
    homeworks_yesterday = filter_homework_by_date(homeworks, yesterday)

    # 🔹 Получаем ДЗ по выбранному предмету
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)








