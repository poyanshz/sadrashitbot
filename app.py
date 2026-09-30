from flask import Flask, render_template, request
import requests
import base64
import os

app = Flask(__name__)

AVALAI_API_KEY = os.environ.get("AVALAI_API_KEY", "")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    if "photo" not in request.files:
        return "عکسی آپلود نشده", 400
    
    photo = request.files["photo"]
    photo_bytes = photo.read()
    
    user_ip = request.remote_addr
    if not check_rate_limit(user_ip):
        return "<p style='color:red; text-align:center; padding:20px;'>❌ محدودیت روزانه! امروز ۳ بار استفاده کردی. فردا دوباره امتحان کن.</p>", 429
    
    filename = photo.filename.lower()
    if filename.endswith(".png"):
        mime = "image/png"
    elif filename.endswith(".webp"):
        mime = "image/webp"
    else:
        mime = "image/jpeg"
    
    photo_base64 = base64.b64encode(photo_bytes).decode("utf-8")
    
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
    
    headers = {
        "Authorization": f"Bearer {AVALAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-image-2.5-flare",
        "prompt": prompt,
        "images": [
            {
                "image_url": f"data:{mime};base64,{photo_base64}"
            }
        ]
    }
    
    try:
        response = requests.post(
            "https://api.avalai.ir/v1/images/edits",
            headers=headers,
            json=data,
            timeout=120
        )
        
        if response.status_code != 200:
            return f"<p style='color:red;'>خطا در ساخت تصویر (کد {response.status_code}):<br>{response.text}</p>", 500
        
        result = response.json()
        image_url = result.get("data", [{}])[0].get("url", "")
        
        if not image_url:
            return f"<p style='color:red;'>پاسخ نامعتبر:<br>{result}</p>", 500
        
        return f'<img src="{image_url}" style="max-width:100%; border-radius:10px;">'
    
    except Exception as e:
        return f"<p style='color:red;'>خطا: {str(e)}</p>", 500

    data = {
   "model": "gpt-image-2.5-flare",
    "prompt": prompt,
    "images": [
        {
            "image_url": f"data:{mime};base64,{photo_base64}"
        }
    ]
}

    try:
        response = requests.post(
            "https://api.avalai.ir/v1/images/edits",
            headers=headers,
            json=data,
            timeout=120
        )

        if response.status_code != 200:
            return f"<p style='color:red;'>خطا در ساخت تصویر (کد {response.status_code}):<br>{response.text}</p>", 500

        result = response.json()
        image_url = result.get("data", [{}])[0].get("url", "")

        if not image_url:
            return f"<p style='color:red;'>پاسخ نامعتبر:<br>{result}</p>", 500

        return f'<img src="{image_url}" style="max-width:100%; border-radius:10px;">'

    except Exception as e:
        return f"<p style='color:red;'>خطا: {str(e)}</p>", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
