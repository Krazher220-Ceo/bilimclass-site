from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# 🔑 Твой токен для API
TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI5M2Y5ZGU0ZS1iYzYzLTQ4MGYtYTI4NC03ZTE2NmYwOWI0NjQiLCJqdGkiOiI4YjM3ZjRmMzEyMzNmZDM3NGYzYTA5NGNmYWEzYzMwYzFlYTBkZTZkZGFiZTYwZDI2NTNmMjM0ZjQ4OTI4YmNlNDI2NTdhNDg4MjVhZjdmMSIsImlhdCI6MTc0MDU2NDc3My4wMzU1MTYsIm5iZiI6MTc0MDU2NDc3My4wMzU1MTksImV4cCI6MTc3MjEwMDc3My4wMjExMTYsInN1YiI6Ijg5NTQ2NTU5Iiwic2NvcGVzIjpbXX0.wgcr6MgQv_-XDOKK5EtcodgvoxMddmwAvc2RFFxs8crKIFAQc5aedE5LnR-yWs7hut8ZeP64Y7VpF2jbYEfdTkgfVNO0z1W8RS67fPFSZ4INe4YOmxDDIeopvORQQt7TgmstaYExybAgKEH3MNreTZrtn6G7eUxpFOzHc0psQTAaGrKWpfCLOijVmgRbCvmnhYlBp7bByNKfyKijNxOuTZFjRWysg28j_nx3GLlhK_eVSNzEs6bIzidlZQ8BWvguYDPpncYggIGd2u9bJU3pSUV3p0UZEWsK2kW-OpgK0yxKgxKDB_Y1pa0at9r2RoLCMzhUlwOvCI4GT9tcCCY74azVuiQ4CpsO3fHPfhyhqM9MRO062PVjx4znTx-RSYpw3odBrJ8uPJsMVvI1QqJGhGmbrvA0V5wy2KBB2CWxiALkFIWITzcr5MjxvzNrl0-3K8nhvOrDAob-USMUiP_a2Og0VGZ9rO4RGLNaD6Zx8gK0MT4wWWALDp3OQiijom8YMVDaeV4YQ7OiM-9YY7l5Vs66VUsXWxG4Xg8T9bbCq_7QXuWmvNS0-0Bxpzon6vLVCQmhOkEctbfsZjVmsQDNNkcGOGfPvJja5ITJVpRAHspG7HG48XKGy-KlJzQotScRMtqQ3P_6cOyzCXPJAN40_s-4p1PQAIwvwa6MOElhB_w"

# 📌 URL запроса
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

