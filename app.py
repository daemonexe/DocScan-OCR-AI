from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv
import cv2
import pytesseract
import os
import json

# Load .env variables (for GROQ_API_KEY)
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

UPLOAD_FOLDER = "uploads"
ALLOWED_EXT = {'jpg', 'jpeg', 'png', 'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ------------------- Groq Integration -----------------------
def call_groq_model(raw_text):
    client = Groq()

    prompt = f"""
    Extract structured information from the following lease text and return it as a valid JSON object.

    Only output the JSON. Do not include any explanations, comments, or extra text.

    Text:
    {raw_text}
    """
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",  
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=1024,
        stream=False
    )

    return completion.choices[0].message.content.strip()


# ------------------- OCR Function --------------------------
def allowed(f):
    return '.' in f and f.rsplit('.', 1)[1].lower() in ALLOWED_EXT


def find_table_and_ocr(img_path):
    print("Processing:", img_path)
    original = cv2.imread(img_path)
    if original is None:
        print("Could not read image")
        return [], ""

    gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
        15, 10
    )

    h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))
    v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 50))
    h_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, h_kernel)
    v_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, v_kernel)
    table_mask = cv2.add(h_lines, v_lines)

    contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return [], ""

    c = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(c)
    table_roi = original[y:y+h, x:x+w]

    df = pytesseract.image_to_data(table_roi, output_type=pytesseract.Output.DATAFRAME)
    df = df.dropna()
    df = df[df["conf"] > 70]

    sorted_df = df.sort_values(by='top')

    rows = []
    current_y = None
    current_row = []
    for _, r in sorted_df.iterrows():
        if current_y is None:
            current_y = r['top']
        if abs(r['top'] - current_y) < 20:
            current_row.append((r['left'], r['text']))
        else:
            current_row.sort(key=lambda z: z[0])
            rows.append([txt for _, txt in current_row])
            current_row = [(r['left'], r['text'])]
            current_y = r['top']
    if current_row:
        current_row.sort(key=lambda z: z[0])
        rows.append([txt for _, txt in current_row])

    # Mask the table
    cv2.rectangle(original, (x, y), (x + w, y + h), (255, 255, 255), thickness=cv2.FILLED)

    # Final OCR (after table masking)
    raw_text = pytesseract.image_to_string(original)

    return rows, raw_text


# ------------------- Upload Endpoint --------------------------
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "no file"}), 400

    f = request.files['file']
    if f.filename == "":
        return jsonify({"error": "empty filename"}), 400

    filename = secure_filename(f.filename)
    savepath = os.path.join(UPLOAD_FOLDER, filename)
    f.save(savepath)

    if filename.lower().endswith(".pdf"):
        from pdf2image import convert_from_path
        pages = convert_from_path(savepath)
        if not pages:
            return jsonify({"error": "pdf read error"}), 400
        img_path = savepath.replace(".pdf", ".jpg")
        pages[0].save(img_path, "JPEG")
        rows, raw_text = find_table_and_ocr(img_path)
    else:
        rows, raw_text = find_table_and_ocr(savepath)

    # Call Groq to get structured data
    groq_response = call_groq_model(raw_text)

    try:
        structured_json = json.loads(groq_response)
    except json.JSONDecodeError as e:
        structured_json = {
            "error": "Groq JSON parsing failed",
            "details": str(e),
            "raw_response": groq_response
        }

    return jsonify({
        "raw_text": raw_text,
        "table": rows,
        "structured_json": structured_json
    })


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
