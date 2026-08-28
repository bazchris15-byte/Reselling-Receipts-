import os, base64, sqlite3, uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, Response
from werkzeug.utils import secure_filename
from pydantic import BaseModel
from openai import OpenAI

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "receipts")
DB_PATH = os.path.join(BASE_DIR, "receipts.db")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ReceiptData(BaseModel):
    vendor: str
    date: str
    total: float
    tax: float
    category: str
    payment_method: str
    description: str

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS receipts(
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            vendor TEXT,
            receipt_date TEXT,
            total REAL,
            tax REAL,
            category TEXT,
            payment_method TEXT,
            description TEXT,
            image_name TEXT NOT NULL
        )
        """)

@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/manifest.json")
def manifest():
    return send_from_directory(BASE_DIR, "manifest.json", mimetype="application/manifest+json")

@app.route("/sw.js")
def sw():
    return send_from_directory(BASE_DIR, "sw.js", mimetype="application/javascript")

@app.route("/receipts/<path:name>")
def receipt_image(name):
    return send_from_directory(UPLOAD_DIR, name)

@app.route("/api/receipts")
def list_receipts():
    with db() as conn:
        rows = conn.execute("SELECT * FROM receipts ORDER BY created_at DESC").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/summary")
def summary():
    with db() as conn:
        row = conn.execute("""
            SELECT COALESCE(SUM(total),0) total, COUNT(*) count
            FROM receipts
            WHERE substr(created_at,1,7)=substr(datetime('now'),1,7)
        """).fetchone()
    return jsonify(dict(row))

@app.route("/api/scan", methods=["POST"])
def scan():
    if "receipt" not in request.files:
        return jsonify({"error": "No receipt image received"}), 400

    f = request.files["receipt"]
    ext = os.path.splitext(secure_filename(f.filename or "receipt.jpg"))[1].lower() or ".jpg"
    if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
        ext = ".jpg"

    rid = str(uuid.uuid4())
    filename = rid + ext
    path = os.path.join(UPLOAD_DIR, filename)
    f.save(path)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return jsonify({"error": "OPENAI_API_KEY is not set. The photo was saved, but automatic reading is disabled."}), 500

    mime = "image/jpeg"
    if ext == ".png":
        mime = "image/png"
    elif ext == ".webp":
        mime = "image/webp"

    with open(path, "rb") as img:
        b64 = base64.b64encode(img.read()).decode("utf-8")

    client = OpenAI(api_key=api_key)
    system_prompt = """
You extract bookkeeping data from business receipt photos.
Return the most likely values visible on the receipt.
For date, use YYYY-MM-DD if possible, otherwise use an empty string.
For total and tax, return numeric values; use 0 if unreadable.
Choose exactly one category from:
Inventory, Shipping Supplies, Gas, Equipment, Repairs, Meals/Travel, Office, Fees, Other.
If the purchase appears to be merchandise bought for resale, use Inventory.
payment_method should be a short value such as Cash, Debit, Credit, Visa, Mastercard,
Amex, Discover, or Unknown. Do not include full card numbers.
description should be a short plain-English summary of what appears to have been purchased.
"""

    response = client.responses.parse(
        model=os.environ.get("OPENAI_MODEL", "gpt-5.6"),
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": [
                {"type": "input_text", "text": "Read and categorize this receipt."},
                {"type": "input_image", "image_url": f"data:{mime};base64,{b64}"}
            ]}
        ],
        text_format=ReceiptData,
    )
    data = response.output_parsed

    with db() as conn:
        conn.execute("""
            INSERT INTO receipts
            (id, created_at, vendor, receipt_date, total, tax, category, payment_method, description, image_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rid, datetime.now().isoformat(timespec="seconds"),
            data.vendor, data.date, data.total, data.tax, data.category,
            data.payment_method, data.description, filename
        ))

    return jsonify({
        "id": rid,
        "vendor": data.vendor,
        "receipt_date": data.date,
        "total": data.total,
        "tax": data.tax,
        "category": data.category,
        "payment_method": data.payment_method,
        "description": data.description,
        "image_name": filename
    })

@app.route("/api/export.csv")
def export_csv():
    import csv, io
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["Date","Vendor","Category","Description","Total","Tax","Payment Method","Image"])
    with db() as conn:
        rows = conn.execute("""
            SELECT receipt_date,vendor,category,description,total,tax,payment_method,image_name
            FROM receipts ORDER BY receipt_date DESC
        """)
        writer.writerows(rows)
    return Response(out.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=receipts.csv"})

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
