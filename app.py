import requests
import os
from flask import Flask, render_template, request
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
SCHOOL_ID = os.getenv("SCHOOL_ID", "1006693")
EDU_YEAR = os.getenv("EDU_YEAR", "2024")
STUDENT_GROUP_UUID = os.getenv("STUDENT_GROUP_UUID", "2666df86-ee3e-4d22-aa76-052f3fedf057")

LOGIN_URL = "https://api.bilimclass.kz/api/v2/os/login"
HOMEWORK_URL = f"https://api.bilimclass.kz/api/v4/os/clientoffice/homeworks/monthly/list?schoolId={SCHOOL_ID}&eduYear={EDU_YEAR}&studentGroupUuid={STUDENT_GROUP_UUID}"

app = Flask(__name__, template_folder="templates")

def get_new_token():
    payload = {"login": USERNAME, "password": PASSWORD}
    response = requests.post(LOGIN_URL, json=payload)

    if response.status_code == 200 and response.json().get("success"):
        access_token = response.json()["access_token"]
        os.environ["TOKEN"] = access_token
        print(f"✅ Новый токен получен: {access_token}")
        return access_token
    else:
        print("❌ Ошибка авторизации!")
        return None

def get_headers():
    token = os.environ.get("TOKEN") or get_new_token()
    if not token:
        print("❌ Ошибка: Токен не найден!")
        return {}
    return {"Authorization": f"Bearer {token}"}

def get_homework():
    response = requests.get(HOMEWORK_URL, headers=get_headers())

    if response.status_code == 401:
        print("⚠️ Токен истёк, получаем новый...")
        get_new_token()
        response = requests.get(HOMEWORK_URL, headers=get_headers())

    try:
        data = response.json()
        return data.get("data", [])
    except Exception as e:
        print("❌ Ошибка при разборе JSON (ДЗ):", e)
        return []

def filter_homework_by_date(homeworks, date):
    return [hw for hw in homeworks if hw.get("date") == date]

@app.route("/", methods=["GET", "POST"])
def index():
    homeworks = get_homework()
    if not homeworks:
        return "❌ Ошибка: API не вернуло домашнее задание!", 500

    subjects = sorted(set(hw["subjectName"] for hw in homeworks if "subjectName" in hw))

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


