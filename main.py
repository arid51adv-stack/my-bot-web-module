from flask import Flask, request, jsonify, send_from_directory
from psd_tools import PSDImage
from PIL import Image, ImageDraw, ImageFont
import os, uuid, requests
from io import BytesIO

app = Flask(__name__)

TEMPLATES_DIR = "templates"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    template_id = data.get("template_id")
    name = data.get("name")
    surname = data.get("surname")
    photo_url = data.get("photo_url")

    psd_path = os.path.join(TEMPLATES_DIR, f"{template_id}.psd")
    if not os.path.exists(psd_path):
        return jsonify({"error": "Template not found"})

    # Загружаем PSD
    psd = PSDImage.open(psd_path)
    base_image = psd.composite()
    image = base_image.convert("RGBA")

    # Добавляем текст
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", 50)
    draw.text((100, 100), f"{name} {surname}", font=font, fill=(255,255,255,255))

    # Добавляем фото пользователя
    response = requests.get(photo_url)
    user_img = Image.open(BytesIO(response.content)).convert("RGBA")
    user_img = user_img.resize((200, 200))
    image.paste(user_img, (300, 300), user_img)

    # Сохраняем PNG
    filename = f"{uuid.uuid4()}.png"
    output_path = os.path.join(OUTPUT_DIR, filename)
    image.save(output_path)

    return jsonify({"url": f"/files/{filename}"})

@app.route("/files/<filename>")
def files(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
