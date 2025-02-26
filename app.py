from flask import Flask, render_template, request
import redis
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# Подключение к Redis
redis_client = redis.Redis.from_url("redis://red-cuvlkblds78s73cndhmg:6379")

# API для получения домашнего задания
API_URL = "https://api.bilimclass.kz/api/v4/os/clientoffice/homeworks/monthly/list"
SCHOOL_ID = "1006693"
EDU_YEAR = "2024"
STUDENT_GROUP_UUID = "2666df86-ee3e-4d22-aa76-052f3fedf057"

# Список предметов
SUBJECTS = ["Математика", "Физика", "Химия", "Биология"]

# Функция для получения данных с API
def get_homework_data():
    try:
        response = requests.get(f"{API_URL}?schoolId={SCHOOL_ID}&eduYear={EDU_YEAR}&studentGroupUuid={STUDENT_GROUP_UUID}")
        return response.json()
    except:
        return {"homeworks": []}

# Функция для проверки наличия предмета в расписании
def is_subject_tomorrow(data, subject):
    tomorrow = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    return any(hw["subject"] == subject and hw["date"] == tomorrow for hw in data.get("homeworks", []))

# Функция для получения домашнего задания
def get_homework(data, subject):
    today = datetime.today().strftime("%Y-%m-%d")
    yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    homework_today = [hw["homework"] for hw in data.get("homeworks", []) if hw["subject"] == subject and hw["date"] == today]
    homework_yesterday = [hw["homework"] for hw in data.get("homeworks", []) if hw["subject"] == subject and hw["date"] == yesterday]

    return homework_today, homework_yesterday

@app.route("/", methods=["GET", "POST"])
def index():
    data = get_homework_data()
    
    subject = request.form.get("subject", "Математика")  # По умолчанию Математика
    homework_today, homework_yesterday = get_homework(data, subject)

    # Проверяем, есть ли предмет завтра
    subject_tomorrow = is_subject_tomorrow(data, subject)
    
    # Обновляем список предметов с указанием "Есть завтра" или "Нет завтра"
    subject_options = {subj: is_subject_tomorrow(data, subj) for subj in SUBJECTS}

    # Увеличиваем счётчик просмотров
    redis_client.incr("page_views")
    views = redis_client.get("page_views").decode("utf-8")

    return render_template("index.html", subject=subject, subject_tomorrow=subject_tomorrow, 
                           subject_options=subject_options, homework_today=homework_today, 
                           homework_yesterday=homework_yesterday, views=views)

if __name__ == "__main__":
    app.run(debug=True)










