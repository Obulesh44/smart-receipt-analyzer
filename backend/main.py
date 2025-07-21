# backend/main.py
from fastapi import FastAPI, UploadFile, File, Query, Body
from backend.parser import extract_text, parse_fields
from backend.db import insert_receipt, initialize_db, get_connection
from backend.models import Receipt
from typing import List, Optional
from backend.models import CorrectedReceipt
from fastapi.responses import JSONResponse
import traceback
from backend.utils import detect_currency
from datetime import date
import os
import uuid


# Initialize FastAPI application
app = FastAPI()

# Ensure database is initialized at startup

initialize_db()

@app.post("/upload/")
# Uploads a receipt file, extracts text using OCR,
async def upload_receipt(file: UploadFile = File(...)):

    file_ext = os.path.splitext(file.filename)[-1]

    temp_filename = f"temp_receipt_{uuid.uuid4().hex}{file_ext}"


    with open(temp_filename, "wb") as f:
        f.write(await file.read())

    text = extract_text(temp_filename)
    print("\n--- OCR TEXT ---\n", text)  #  Show raw OCR text


    data = parse_fields(text)

    currency = detect_currency(text)
    data["currency"] = currency

    print("\n--- PARSED DATA ---\n", data)  #  Show parsed fields

    try:
        inserted_id = insert_receipt(data)
        data["id"] = inserted_id
    except Exception as e:
        print("❌ DB Insert Error:", str(e))  #  Show actual DB error
        raise

    return {"message": "Receipt uploaded and stored successfully.", "data": data}




@app.post("/save-corrected/")

# Updates an existing receipt in the DB with corrected values
#     submitted from the frontend.

def save_corrected(receipt: dict):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE receipts
            SET vendor = %s, date = %s, amount = %s, category = %s, currency = %s
            WHERE id = %s
        """, (
            receipt["vendor"],
            receipt["date"],
            receipt["amount"],
            receipt["category"],
            receipt["currency"],
            receipt["id"]
        ))
        conn.commit()
        return {"status": "success"}
    except Exception as e:
        print("❌ DB UPDATE ERROR:", str(e))
        traceback.print_exc()
        return JSONResponse(content={"status": "fail", "error": str(e)}, status_code=500)




@app.get("/receipts/")
# Fetches all stored receipts from the database.
# Returns a list of receipt records in JSON format.

def get_all_receipts():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, vendor, date, amount, category, currency FROM receipts")
    rows = cur.fetchall()
    receipts = [
        {
            "id": r[0],
            "vendor": r[1],
            "date": str(r[2]),
            "amount": float(r[3]),
            "category": r[4],
            "currency": r[5]
        }

        for r in rows
    ]
    return JSONResponse(content={"data": receipts})



#  Advanced Search + Sort
@app.get("/receipts/search/")
def search_receipts(
    vendor: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    sort_by: Optional[str] = Query(None, description="Sort by vendor/date/amount"),
    sort_order: Optional[str] = Query("asc", description="Sort order: asc or desc")
):
    """
    Search and filter receipts based on vendor, amount range, and date range.
    Also supports sorting by vendor, date, or amount.
    """
    conn = get_connection()
    cur = conn.cursor()

    query = "SELECT * FROM receipts WHERE TRUE"
    params = []

    if vendor:
        query += " AND vendor ILIKE %s"
        params.append(f"%{vendor}%")

    if min_amount:
        query += " AND amount >= %s"
        params.append(min_amount)

    if max_amount:
        query += " AND amount <= %s"
        params.append(max_amount)

    if start_date:
        query += " AND date >= %s"
        params.append(start_date)

    if end_date:
        query += " AND date <= %s"
        params.append(end_date)

    if sort_by in ["vendor", "date", "amount"]:
        query += f" ORDER BY {sort_by} {sort_order.upper()}"

    cur.execute(query, params)
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    results = [dict(zip(columns, row)) for row in rows]

    return {"data": results}


@app.get("/")

# Root endpoint to verify the API is running.
def read_root():
    return {"message": "Smart Receipt Analyzer API is running"}


@app.get("/favicon.ico")

#  Prevents browser from requesting a favicon error.
def favicon():
    return {}
