from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
session = requests.Session()

EMAIL = "DAVIDPOVARSKI1@GMAIL.COM"
PASSWORD = "sefaria"

def login():
    login_url = "https://www.sefaria.org.il/login"
    r = session.get(login_url)
    csrf_token = r.text.split('name="csrfmiddlewaretoken" value="')[1].split('"')[0]
    payload = {
        "csrfmiddlewaretoken": csrf_token,
        "email": EMAIL,
        "password": PASSWORD,
        "next": "/texts"
    }
    headers = {
        "Referer": login_url
    }
    session.post(login_url, data=payload, headers=headers)
    return csrf_token

csrf_token = login()

@app.route("/")
def home():
    return "Sefaria Note Server is running!"

@app.route("/note", methods=["POST"])
def send_note():
    data = request.json
    if not data or "text" not in data or "refs" not in data:
        return jsonify({"error": "Missing 'text' or 'refs'"}), 400

    note_url = "https://www.sefaria.org.il/api/notes/"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "*/*",
        "X-CSRFToken": csrf_token,
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.sefaria.org.il/"
    }
    payload = {
        "json": str({
            "text": data["text"],
            "refs": data["refs"],
            "type": "note",
            "public": False
        })
    }

    response = session.post(note_url, data=payload, headers=headers)
    return jsonify(response.json()), response.status_code