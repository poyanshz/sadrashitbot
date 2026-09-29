from flask import Flask, render_template, request, send_file
import requests
import io
import base64

app = Flask(__name__)

# کلید API SenseNova رو اینجا بذار
SENSENOVA_API_KEY = "sk-HaXvqQ9XaO2aCfmO3whcBNSsMjVvCZtp"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    # دریافت عکس آپلود شده
    if "photo" not in request.files:
        return "عکسی آپلود نشده", 400
    
    photo = request.files["photo"]
    photo_bytes = photo.read()
    
    # تبدیل عکس به base64
    photo_base64 = base64.b64encode(photo_bytes).decode("utf-8")
    
    # پرامپت برای SenseNova
    prompt = (
        "Create a 4-panel character reference sheet on a clean white background. "
        "Panel 1: CLOSE-UP of the FACE (head and shoulders, front-facing). "
        "Panel 2: FULL BODY FRONT view. "
        "Panel 3: FULL BODY SIDE view. "
        "Panel 4: FULL BODY BACK view. "
        "Preserve the person's EXACT facial features, skin tone, hair color, "
        "hairstyle, and clothing across all four panels. "
        "White background. No text, no labels."
    )
    
    # درخواست به SenseNova
    headers = {
        "Authorization": f"Bearer {SENSENOVA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "sensenova-u1.5-lite",
        "prompt": prompt,
        "image": f"data:image/jpeg;base64,{photo_base64}"
    }
    
    response = requests.post(
        "https://api.sensenova.ai/v1/images/edits",
        headers=headers,
        json=data
    )
    
    if response.status_code != 200:
        return f"خطا در ساخت تصویر: {response.text}", 500
    
    result = response.json()
    image_url = result.get("data", [{}])[0].get("url", "")
    
    return f'<img src="{image_url}" style="max-width:100%">'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
