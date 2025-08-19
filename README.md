# 🧠 AI-Powered Document Extraction System

This project is a full-stack, AI-enhanced system that extracts structured data from lease documents using OCR, table detection, and large language models (LLMs). It is designed to process PDF or image uploads, parse them intelligently, and store the extracted information in a PostgreSQL database.

---

## 🔄 Workflow Overview

1. **User Uploads File**
   - Users upload a lease document (PDF or image) via the frontend interface.
   - The file is sent to the Flask backend via a POST request.

2. **File Handling**
   - If the file is a PDF, the first page is converted into an image using `pdf2image`.
   - If the file is an image (`.jpg`, `.jpeg`, `.png`), it is used directly.

3. **Table Detection (OpenCV)**
   - The image is processed using OpenCV to detect table structures.
   - A region of interest (ROI) is identified where the table exists.
   - Tesseract extracts text from the table and organizes it into rows.

4. **Raw Text Extraction**
   - The table is masked out.
   - `pytesseract` extracts the remaining visible text from the document.

5. **Structured Data via LLM**
   - The raw extracted text is sent to the **Groq LLM API** (LLaMA 3.1).
   - The model returns a structured JSON representation of the key information in the lease (e.g., parties, rent, dates).

6. **Data Storage**
   - The following fields are saved into a PostgreSQL database:
     - `filename`
     - `raw_text` (OCR result)
     - `table_data` (from OpenCV + Tesseract)
     - `structured_json` (from Groq)

7. **View History**
   - A `/history` endpoint allows viewing all previously processed documents and their metadata.

---

## 🛠️ Technologies Used

| Purpose              | Tech/Library           |
|----------------------|------------------------|
| Web Backend          | Flask                  |
| File Upload & CORS   | flask-cors, Werkzeug   |
| OCR                  | pytesseract            |
| Table Detection      | OpenCV                 |
| PDF to Image         | pdf2image              |
| LLM API              | Groq (LLaMA 3.1)       |
| Database             | PostgreSQL             |
| Database Driver      | psycopg2-binary        |
| Containerization     | Docker (Python 3.11)   |

---

## 🌐 API Endpoints

### `POST /upload`
- Uploads a document, extracts text + tables, sends text to Groq API, and stores everything in the database.

### `GET /history`
- Returns metadata and extracted results from all previously uploaded documents.

---

## 💡 Use Cases

- Lease contract parsing  
- Rent agreement automation  
- Property data extraction  
- Intelligent document analysis  
- Legal document simplification

---

## 📦 Output Example

```json
{
  "raw_text": "This Lease Agreement is made...",
  "table": [["Year", "Monthly Rent", "Annual Rent"]],
  "structured_json": {
    "tenant": "John Doe",
    "landlord": "ABC Rentals",
    "start_date": "2024-01-01",
    "monthly_rent": 1800
  }
}
