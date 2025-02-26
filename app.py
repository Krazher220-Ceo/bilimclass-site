import requests
import os
from flask import Flask, render_template, request
from datetime import datetime, timedelta

app = Flask(__name__, template_folder="templates")

# 🔹 API-токен
TOKEN = os.getenv("TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# 🔹 Данные для запроса
SCHOOL_ID = "1006693"
EDU_YEAR = "2024"
STUDENT_GROUP_UUID = "2666df86-ee3e-4d22-aa76-052f3fedf057"  # ✅ Новый UUID

# 🔹 URL для расписания и ДЗ
SCHEDULE_URL = f"https://api.bilimclass.kz/api/v4/os/clientoffice/schedule?schoolId={SCHOOL_ID}&eduYear={EDU_YEAR}&studentGroupUuid={STUDENT_GROUP_UUID}"
HOMEWORK_URL = f"https://api.bilimclass.kz/api/v4/os/clientoffice/homeworks/monthly/list?schoolId={SCHOOL_ID}&eduYear={EDU_YEAR}&studentGroupUuid={STUDENT_GROUP_UUID}"

def get_schedule():
    """🔹 Получает расписание с API BilimClass"""
    response = requests.get(SCHEDULE_URL, headers=HEADERS)
    print(f"🔍 Код ответа API (расписание): {response.status_code}")  
    print(f"🔍 Тело ответа API (расписание): {response.text}")  

    try:
        data = response.json()
        if isinstance(data, dict) and "data" in data and "days" in data["data"]:
            schedule_list = []
            for day in data["data"]["days"]:
                print(f"📅 Дата: {day['dateFormat']} → Уроков: {len(day['schedule'])}")
                for lesson in day["schedule"]:
                    lesson["date"] = day["dateFormat"]
                    schedule_list.append(lesson)
            return schedule_list
    except Exception as e:
        print("❌ Ошибка при разборе JSON (расписание):", e)

    return []

def get_homework():
    """🔹 Получает домашнее задание с API BilimClass"""
    response = requests.get(HOMEWORK_URL, headers=HEADERS)
    try:
        data = response.json()
        print("🔍 Ответ API (ДЗ):", data)  
        if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
            return data["data"]
    except Exception as e:
        print("❌ Ошибка при разборе JSON (ДЗ):", e)
    return []

def match_homework(schedule, homeworks):
    """🔹 Сопоставляет расписание и ДЗ"""
    if not isinstance(schedule, list) or not isinstance(homeworks, list):
        print("❌ Ошибка: `schedule` или `homeworks` не список!")
        return []

    hw_dict = {hw["date"]: hw for hw in homeworks if "date" in hw and "subjectName" in hw}
    today = datetime.today().strftime("%d.%m.%Y")

    for lesson in schedule:
        if not isinstance(lesson, dict):
            print("❌ Ошибка: неверный формат урока", lesson)
            continue
        
        lesson_date = lesson.get("date", "Unknown Date")
        subject = lesson.get("subjectName", "Unknown Subject")

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
    
    if not schedule:
        return "❌ Ошибка: API не вернуло расписание!", 500
    if not homeworks:
        return "❌ Ошибка: API не вернуло домашнее задание!", 500

    schedule_with_hw = match_homework(schedule, homeworks)
    print("🔍 Расписание с ДЗ:", schedule_with_hw)  

    subjects = sorted(set(lesson.get("subjectName", "❌ Без предмета") for lesson in schedule_with_hw if isinstance(lesson, dict)))

    selected_subject = request.form.get("subject")
    filtered_schedule = [lesson for lesson in schedule_with_hw if lesson.get("subjectName") == selected_subject] if selected_subject else schedule_with_hw

    return render_template("index.html", subjects=subjects, schedule=filtered_schedule, selected_subject=selected_subject)
    @app.route("/", methods=["GET"])
    
def index():
    schedule = get_schedule()
    
    if not schedule:
        return "📌 Расписание временно недоступно. Проверь позже!", 200

    return render_template("index.html", schedule=schedule)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)






