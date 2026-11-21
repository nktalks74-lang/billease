import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from tkinter import colorchooser
import sqlite3
import os
import hashlib
import hmac
import secrets
import json
import csv
import shutil
import tempfile
import io
from datetime import date, datetime, timedelta
import urllib.request
import webbrowser
import urllib.error
import threading
import socket
import base64
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit
from email.parser import BytesParser
from email.policy import default as email_policy
import html
import re
import smtplib
from email.message import EmailMessage
from urllib.parse import urlencode

# ==========================================
# BILLEASE AI - PRODUCT & DASHBOARD SYSTEM
# ==========================================

DB_NAME = "billease.db"


def configure_database_path():
    """Keep BillEase data in the user's local app-data folder across launches."""
    global DB_NAME
    local_root = os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), ".local", "share")
    data_dir = os.path.join(local_root, "BillEase")
    try:
        os.makedirs(data_dir, exist_ok=True)
    except OSError:
        # A portable/local fallback still keeps the app usable if app-data is unavailable.
        DB_NAME = os.path.abspath("billease.db")
        return

    target = os.path.join(data_dir, "billease.db")
    if not os.path.exists(target):
        source_candidates = (
            os.path.abspath("billease.db"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "billease.db"),
        )
        for source_path in source_candidates:
            if os.path.isfile(source_path) and os.path.normcase(source_path) != os.path.normcase(target):
                try:
                    # SQLite's backup API includes committed data even when WAL is enabled.
                    with sqlite3.connect(source_path, timeout=30) as source_conn:
                        with sqlite3.connect(target, timeout=30) as target_conn:
                            source_conn.backup(target_conn)
                    break
                except sqlite3.Error:
                    try:
                        os.remove(target)
                    except OSError:
                        pass
                    # Keep looking for another legacy copy if the first one is damaged.
    DB_NAME = target

BG = "#F5F7FB"
WHITE = "#FFFFFF"
BLUE = "#2563EB"
PURPLE = "#7C3AED"
DARK = "#1F2937"
MUTED = "#6B7280"
BORDER = "#E5E7EB"
GREEN = "#16A34A"
WARNING = "#F59E0B"
RED = "#DC2626"
SIDEBAR = "#111827"
SIDEBAR_TEXT = "#D1D5DB"
SIDEBAR_ACTIVE = BLUE
LIGHT_BLUE = "#EEF2FF"
LIGHT_PURPLE = "#F3E8FF"
COLORS = {"primary":BLUE,"secondary":PURPLE,"background":BG,"white":WHITE,
          "sidebar":SIDEBAR,"text":DARK,"muted":MUTED,"border":BORDER,
          "success":GREEN,"warning":WARNING,"danger":RED}
PADDING = {"main":24,"card":20,"form":20,"button_x":18,"button_y":10,"section":22}

# Starter catalogue: 20 quick-pick items in each of 10 common categories.
PRODUCT_CATALOG = {
    "Grocery": ("Rice", "Wheat Flour", "Sugar", "Salt", "Cooking Oil", "Toor Dal", "Moong Dal", "Chana Dal", "Tea Powder", "Coffee Powder", "Milk", "Curd", "Butter", "Bread", "Eggs", "Biscuits", "Pasta", "Noodles", "Spice Mix", "Packaged Water"),
    "Electronics": ("Smartphone", "Feature Phone", "Tablet", "Laptop", "Desktop Computer", "Computer Monitor", "Keyboard", "Mouse", "Printer", "Router", "Power Bank", "USB Cable", "Phone Charger", "Headphones", "Bluetooth Speaker", "Webcam", "Memory Card", "Pen Drive", "Hard Drive", "UPS"),
    "Clothing": ("Men T-Shirt", "Men Shirt", "Men Jeans", "Men Trousers", "Men Jacket", "Women Top", "Women Kurti", "Women Saree", "Women Jeans", "Women Dress", "Kids T-Shirt", "Kids Jeans", "School Uniform", "Socks", "Belt", "Cap", "Scarf", "Raincoat", "Shorts", "Sportswear"),
    "Home & Furniture": ("Plastic Chair", "Office Chair", "Dining Table", "Study Table", "Bookshelf", "Wardrobe", "Sofa", "Bed Frame", "Mattress", "Pillow", "Bedsheet", "Curtains", "Floor Mat", "Table Lamp", "Wall Clock", "Storage Box", "Laundry Basket", "Mirror", "Door Mat", "Cushion"),
    "Stationery": ("Ball Pen", "Gel Pen", "Pencil", "Eraser", "Sharpener", "Notebook", "Long Notebook", "Drawing Book", "Printer Paper", "File Folder", "Document Folder", "Stapler", "Staples", "Paper Clips", "Marker", "Highlighter", "Whiteboard", "Glue Stick", "Scissors", "Ruler"),
    "Beauty & Personal Care": ("Shampoo", "Conditioner", "Bath Soap", "Face Wash", "Moisturizer", "Sunscreen", "Hair Oil", "Toothpaste", "Toothbrush", "Mouthwash", "Deodorant", "Perfume", "Face Cream", "Lip Balm", "Body Lotion", "Hair Brush", "Shaving Cream", "Razor", "Hand Sanitizer", "Nail Polish"),
    "Hardware": ("Hammer", "Screwdriver Set", "Pliers", "Adjustable Wrench", "Spanner Set", "Measuring Tape", "Drill Machine", "Drill Bit Set", "Hacksaw", "Hand Saw", "Paint Brush", "Paint Roller", "Nails Pack", "Screws Pack", "Wall Plug Pack", "Electrical Tape", "PVC Pipe", "Garden Hose", "Padlock", "Safety Gloves"),
    "Kitchen": ("Cooking Pot", "Pressure Cooker", "Frying Pan", "Saucepan", "Water Bottle", "Lunch Box", "Dinner Plate", "Soup Bowl", "Drinking Glass", "Tea Cup", "Cutlery Set", "Kitchen Knife", "Chopping Board", "Spatula", "Colander", "Measuring Cup", "Storage Container", "Kettle", "Mixer Grinder", "Toaster"),
    "Sports & Fitness": ("Cricket Bat", "Cricket Ball", "Football", "Basketball", "Volleyball", "Badminton Racket", "Shuttlecock Pack", "Tennis Ball", "Skipping Rope", "Yoga Mat", "Dumbbell Pair", "Resistance Band", "Water Bottle Sports", "Cycling Helmet", "Knee Support", "Sports Shoes", "Gym Gloves", "Table Tennis Paddle", "Carrom Board", "Chess Set"),
    "Toys & Gifts": ("Building Blocks", "Toy Car", "Doll", "Soft Toy Bear", "Puzzle Set", "Board Game", "Action Figure", "Toy Train", "Remote Control Car", "Art Kit", "Coloring Book", "Crayons Set", "Baby Rattle", "Stacking Rings", "Toy Kitchen Set", "Science Kit", "Musical Toy", "Gift Wrap", "Greeting Card", "Party Balloons"),
}

GSTIN_PATTERN = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$")


def valid_gstin_format(value):
    """Check GSTIN structure only; this does not verify registration with GSTN."""
    normalized = re.sub(r"\s+", "", str(value or "")).upper()
    return bool(GSTIN_PATTERN.fullmatch(normalized))


# ==========================================
# DATABASE
# ==========================================

def connect_db():
    conn = sqlite3.connect(DB_NAME, timeout=30)
    conn.execute("PRAGMA busy_timeout=30000")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def upload_backup_to_dropbox(local_path, remote_folder="/BillEaseBackups"):
    """Upload one SQLite snapshot using a user-provided Dropbox OAuth token."""
    token=os.environ.get("BILLEASE_DROPBOX_TOKEN","").strip()
    if not token:raise RuntimeError("Set BILLEASE_DROPBOX_TOKEN in Windows environment variables first.")
    size=os.path.getsize(local_path)
    if size>150*1024*1024:
        raise RuntimeError("This backup is over 150 MB. Dropbox chunked uploads are not enabled in this build.")
    folder="/"+"/".join(part for part in str(remote_folder or "").replace("\\","/").split("/") if part)
    if folder!="/":
        create_req=urllib.request.Request("https://api.dropboxapi.com/2/files/create_folder_v2",data=json.dumps({"path":folder,"autorename":False}).encode(),headers={"Authorization":f"Bearer {token}","Content-Type":"application/json"},method="POST")
        try:
            with urllib.request.urlopen(create_req,timeout=30):pass
        except urllib.error.HTTPError as exc:
            response_text=exc.read().decode("utf-8",errors="replace")
            if exc.code!=409 or "path/conflict/folder" not in response_text:raise RuntimeError(f"Dropbox folder setup failed ({exc.code}): {response_text[:300]}") from exc
    remote_path=("" if folder=="/" else folder)+"/"+os.path.basename(local_path)
    api_arg=json.dumps({"path":remote_path,"mode":"add","autorename":True,"mute":True},separators=(",",":"))
    with open(local_path,"rb") as backup_file:data=backup_file.read()
    req=urllib.request.Request("https://content.dropboxapi.com/2/files/upload",data=data,headers={"Authorization":f"Bearer {token}","Dropbox-API-Arg":api_arg,"Content-Type":"application/octet-stream"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=120) as response:
            result=json.loads(response.read().decode("utf-8"))
        return result.get("path_display",remote_path)
    except urllib.error.HTTPError as exc:
        response_text=exc.read().decode("utf-8",errors="replace")
        raise RuntimeError(f"Dropbox upload failed ({exc.code}): {response_text[:400]}") from exc


def initialize_database():
    configure_database_path()
    conn = sqlite3.connect(DB_NAME, timeout=30)
    cursor = conn.cursor()
    cursor.execute("PRAGMA busy_timeout=30000")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sku TEXT UNIQUE,
            category TEXT,
            price REAL DEFAULT 0,
            cost REAL DEFAULT 0,
            stock INTEGER DEFAULT 0,
            low_stock INTEGER DEFAULT 5
        )
    """)

    cursor.execute("PRAGMA table_info(products)")
    existing_columns = [
        row[1] for row in cursor.fetchall()
    ]

    required_columns = {
        "name": "TEXT",
        "sku": "TEXT",
        "category": "TEXT",
        "price": "REAL DEFAULT 0",
        "cost": "REAL DEFAULT 0",
        "stock": "INTEGER DEFAULT 0",
        "low_stock": "INTEGER DEFAULT 5"
    }

    for column, definition in required_columns.items():
        if column not in existing_columns:
            cursor.execute(
                f"ALTER TABLE products ADD COLUMN {column} {definition}"
            )

    cursor.execute("""CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, phone TEXT UNIQUE, address TEXT DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS bills (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_id INTEGER NOT NULL, bill_date TEXT DEFAULT CURRENT_TIMESTAMP, total REAL NOT NULL DEFAULT 0, paid REAL NOT NULL DEFAULT 0, FOREIGN KEY(customer_id) REFERENCES customers(id))""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS bill_items (id INTEGER PRIMARY KEY AUTOINCREMENT, bill_id INTEGER NOT NULL, product_id INTEGER, product_name TEXT NOT NULL, quantity INTEGER NOT NULL, unit_price REAL NOT NULL, line_total REAL NOT NULL, FOREIGN KEY(bill_id) REFERENCES bills(id), FOREIGN KEY(product_id) REFERENCES products(id))""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS customer_payments (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_id INTEGER NOT NULL, amount REAL NOT NULL, payment_date TEXT DEFAULT CURRENT_TIMESTAMP, note TEXT DEFAULT '', FOREIGN KEY(customer_id) REFERENCES customers(id))""")
    migrations = {
        "customers": {"email": "TEXT DEFAULT ''", "gstin": "TEXT DEFAULT ''", "assigned_employee": "TEXT DEFAULT ''"},
        "products": {"unit": "TEXT DEFAULT 'pcs'", "tax_rate": "REAL DEFAULT 0", "is_service": "INTEGER DEFAULT 0", "brand": "TEXT DEFAULT ''", "image_url": "TEXT DEFAULT ''"},
        "bills": {"invoice_no": "TEXT", "due_date": "TEXT", "subtotal": "REAL DEFAULT 0", "discount": "REAL DEFAULT 0", "tax_total": "REAL DEFAULT 0", "status": "TEXT DEFAULT 'unpaid'", "template_name": "TEXT DEFAULT 'Classic'", "template_font": "TEXT DEFAULT 'Helvetica'", "template_font_size": "INTEGER DEFAULT 10", "template_accent": "TEXT DEFAULT '#2563EB'", "employee_id": "INTEGER"},
        "customer_payments": {"payment_mode": "TEXT DEFAULT 'Cash'", "bill_id": "INTEGER"},
    }
    for table, columns in migrations.items():
        present = {row[1] for row in cursor.execute(f"PRAGMA table_info({table})")}
        for column, definition in columns.items():
            if column not in present:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_bills_invoice_no ON bills(invoice_no) WHERE invoice_no IS NOT NULL")
    cursor.execute("""CREATE TABLE IF NOT EXISTS app_settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS business_payments (id INTEGER PRIMARY KEY AUTOINCREMENT, bill_id INTEGER NOT NULL, customer_id INTEGER NOT NULL, amount REAL NOT NULL, payment_mode TEXT NOT NULL DEFAULT 'Cash', payment_date TEXT DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(bill_id) REFERENCES bills(id), FOREIGN KEY(customer_id) REFERENCES customers(id))""")
    payment_columns={row[1] for row in cursor.execute("PRAGMA table_info(business_payments)")}
    if "employee_id" not in payment_columns:
        cursor.execute("ALTER TABLE business_payments ADD COLUMN employee_id INTEGER")
    cursor.execute("""CREATE TABLE IF NOT EXISTS invoice_lines (id INTEGER PRIMARY KEY AUTOINCREMENT, bill_id INTEGER NOT NULL, product_id INTEGER, description TEXT NOT NULL, quantity REAL NOT NULL, unit TEXT DEFAULT 'pcs', rate REAL NOT NULL, discount REAL DEFAULT 0, tax_rate REAL DEFAULT 0, tax_amount REAL DEFAULT 0, line_total REAL NOT NULL, FOREIGN KEY(bill_id) REFERENCES bills(id), FOREIGN KEY(product_id) REFERENCES products(id))""")
    cursor.execute("CREATE TABLE IF NOT EXISTS employees (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'Staff', phone TEXT DEFAULT '', email TEXT DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
    employee_columns={row[1] for row in cursor.execute("PRAGMA table_info(employees)")}
    employee_migrations={"address":"TEXT DEFAULT ''","department":"TEXT DEFAULT ''","joining_date":"TEXT DEFAULT ''","salary":"REAL DEFAULT 0","emergency_contact":"TEXT DEFAULT ''","notes":"TEXT DEFAULT ''","photo_path":"TEXT DEFAULT ''","id_document_path":"TEXT DEFAULT ''","resume_path":"TEXT DEFAULT ''"}
    for column,definition in employee_migrations.items():
        if column not in employee_columns:
            cursor.execute(f"ALTER TABLE employees ADD COLUMN {column} {definition}")
    cursor.execute("INSERT OR IGNORE INTO app_settings(key,value) VALUES ('invoice_prefix','INV'),('business_name','BillEase'),('business_address',''),('business_logo','')")
    sample_seeded=cursor.execute("SELECT 1 FROM app_settings WHERE key='sample_employees_seeded'").fetchone()
    if not sample_seeded:
        first_names=("Asha","Ravi","Priya","Arjun","Meera","Kiran","Ananya","Vikram","Kavya","Rohan")
        surnames=("Patel","Kumar","Sharma","Nair","Joshi","Reddy","Singh","Iyer","Das","Rao")
        roles=("Manager","Sales Staff","Cashier","Inventory Staff","Billing Staff")
        existing={row[0]:row[1] for row in cursor.execute("SELECT name,id FROM employees")}
        number=0
        for first in first_names:
            for surname in surnames:
                number+=1
                name=f"{first} {surname}"
                phone=f"DEMO-EMP-{number:03d}"
                email=f"employee{number:03d}@example.com"
                if name in existing:
                    cursor.execute("UPDATE employees SET phone=CASE WHEN COALESCE(phone,'')='' THEN ? ELSE phone END,email=CASE WHEN COALESCE(email,'')='' THEN ? ELSE email END WHERE id=?",(phone,email,existing[name]))
                elif len(existing)<100:
                    cursor.execute("INSERT INTO employees(name,role,phone,email) VALUES (?,?,?,?)",(name,roles[(number-1)%len(roles)],phone,email))
                    existing[name]=None
        cursor.execute("INSERT OR REPLACE INTO app_settings(key,value) VALUES ('sample_employees_seeded','1')")
    customer_samples_seeded=cursor.execute("SELECT 1 FROM app_settings WHERE key='sample_customers_seeded'").fetchone()
    if not customer_samples_seeded:
        customer_first=("Aarav","Diya","Ishaan","Anika","Kabir","Saanvi","Dev","Ira","Neil","Tara")
        customer_surnames=("Shah","Verma","Mehta","Kapoor","Pillai","Gupta","Bose","Kulkarni","Malhotra","Menon")
        sample_customers=[]
        number=0
        for first in customer_first:
            for surname in customer_surnames:
                number+=1
                sample_customers.append((f"{first} {surname}",f"DEMO-CUST-{number:03d}",f"customer{number:03d}@example.com"))
        cursor.executemany("INSERT OR IGNORE INTO customers(name,phone,email) VALUES (?,?,?)",sample_customers)
        cursor.execute("INSERT OR REPLACE INTO app_settings(key,value) VALUES ('sample_customers_seeded','1')")
    cursor.execute("CREATE TABLE IF NOT EXISTS audit_log (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, action TEXT NOT NULL, invoice_id INTEGER, detail TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
    cursor.execute("CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY AUTOINCREMENT, expense_date TEXT NOT NULL, category TEXT NOT NULL DEFAULT 'General', description TEXT DEFAULT '', amount REAL NOT NULL CHECK(amount >= 0), created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
    cursor.execute("CREATE TABLE IF NOT EXISTS invoice_delivery_log (id INTEGER PRIMARY KEY AUTOINCREMENT, bill_id INTEGER NOT NULL, recipient TEXT NOT NULL, channel TEXT NOT NULL, status TEXT NOT NULL, detail TEXT DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
    cursor.execute("CREATE TABLE IF NOT EXISTS provider_payment_links (id INTEGER PRIMARY KEY AUTOINCREMENT, bill_id INTEGER NOT NULL, provider TEXT NOT NULL, provider_id TEXT NOT NULL UNIQUE, short_url TEXT NOT NULL, amount REAL NOT NULL, status TEXT DEFAULT 'created', created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(expense_date)")
    cursor.executemany("INSERT OR IGNORE INTO app_settings(key,value) VALUES (?,?)", (("auto_backup_enabled", "1"), ("backup_directory", ""), ("auto_backup_last_date", ""), ("cloud_backup_enabled", "0"), ("dropbox_backup_path", "/BillEaseBackups")))
    cursor.execute("CREATE TABLE IF NOT EXISTS payment_requests (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT NOT NULL, phone TEXT NOT NULL, amount REAL NOT NULL, payment_mode TEXT NOT NULL, reference TEXT DEFAULT '', submitted_at TEXT DEFAULT CURRENT_TIMESTAMP, status TEXT DEFAULT 'Pending')")
    payment_cols={row[1] for row in cursor.execute("PRAGMA table_info(payment_requests)")}
    for col,definition in {"payer_name":"TEXT DEFAULT ''","paid_at":"TEXT DEFAULT ''","ai_note":"TEXT DEFAULT ''","receipt_blob":"BLOB","receipt_mime":"TEXT DEFAULT ''"}.items():
        if col not in payment_cols:cursor.execute(f"ALTER TABLE payment_requests ADD COLUMN {col} {definition}")
    cursor.execute("CREATE TABLE IF NOT EXISTS portal_uploads (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_id INTEGER, kind TEXT NOT NULL, file_path TEXT NOT NULL, mime_type TEXT NOT NULL, uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(customer_id) REFERENCES customers(id))")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(name COLLATE NOCASE)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_name ON products(name COLLATE NOCASE)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category COLLATE NOCASE)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bills_customer_date ON bills(customer_id,bill_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bill_items_product ON bill_items(product_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoice_lines_product ON invoice_lines(product_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_customer_date ON business_payments(customer_id,payment_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_customer_payments_customer_date ON customer_payments(customer_id,payment_date)")
    conn.commit()
    conn.close()


def ai_extract_customer_details(text):
    """Extract contact fields from pasted text using Groq chat completions."""
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Set the GROQ_API_KEY environment variable to enable AI features.")
    payload = {"model": "llama-3.3-70b-versatile", "response_format": {"type": "json_object"},
               "messages": [{"role": "system", "content": "Extract customer name, phone, email, address, and GSTIN/tax ID if explicitly present. Return only a JSON object with string keys name, phone, email, address, gstin. Use empty strings for missing values; never guess or create a tax ID."},
                            {"role": "user", "content": text}]}
    request = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"AI request failed ({exc.code}): {details[:500]}") from exc

    text_output = result.get("choices", [{}])[0].get("message", {}).get("content")
    if not text_output:
        raise RuntimeError("AI returned no customer details. Try clearer text.")
    details = json.loads(text_output)
    return {
        key: str(details.get(key, "")).strip()
        for key in ("name", "phone", "email", "address", "gstin")
    }


def ai_report_request(question):
    """Map a natural language report request to supported local report controls."""
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Set the GROQ_API_KEY environment variable to enable AI reports.")
    payload = {"model": "llama-3.3-70b-versatile", "response_format": {"type": "json_object"},
               "messages": [{"role": "system", "content": "Return JSON with period and report. period must be Daily, Weekly, Monthly, or Yearly. report must be sales, products, customers, invoice_status, stock, tax, or profit. Infer the closest match from the user's question."},
                            {"role": "user", "content": question}]}
    request = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions", data=json.dumps(payload).encode("utf-8"), headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            result = json.loads(response.read().decode("utf-8"))
        return json.loads(result["choices"][0]["message"]["content"])
    except Exception as exc:
        raise RuntimeError(f"Groq report request failed: {exc}") from exc


def extract_upi_receipt(image_bytes, mime_type):
    api_key=os.environ.get("GROQ_API_KEY","").strip()
    if not api_key:raise RuntimeError("Set GROQ_API_KEY to extract payment screenshots.")
    image_url=f"data:{mime_type};base64,{base64.b64encode(image_bytes).decode('ascii')}"
    payload={"model":"qwen/qwen3.8-27b","response_format":{"type":"json_object"},"messages":[{"role":"user","content":[{"type":"text","text":"Read this UPI/bank payment receipt. Return JSON keys amount (number or 0), reference (UTR/transaction ID or empty), payer_name (or empty), paid_at (date/time text or empty), payee_name (or empty). Do not infer missing values."},{"type":"image_url","image_url":{"url":image_url}}]}]}
    req=urllib.request.Request("https://api.groq.com/openai/v1/chat/completions",data=json.dumps(payload).encode(),headers={"Authorization":f"Bearer {api_key}","Content-Type":"application/json"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=60) as response:data=json.loads(response.read().decode())
        result=json.loads(data["choices"][0]["message"]["content"])
        return result
    except Exception as exc:raise RuntimeError(f"Could not read payment screenshot: {exc}") from exc


def extract_payment_receipt_upload(file_bytes, mime_type):
    """Extract reviewable payment fields from an image or a text-based PDF receipt."""
    if not mime_type == "application/pdf":
        return extract_upi_receipt(file_bytes, mime_type)
    try:
        from pypdf import PdfReader
        reader=PdfReader(io.BytesIO(file_bytes))
        receipt_text="\n".join((page.extract_text() or "") for page in reader.pages[:8])[:18000]
    except ImportError as exc:
        raise RuntimeError("PDF receipt reading needs pypdf. Install it with: pip install pypdf") from exc
    except Exception as exc:
        raise RuntimeError(f"Could not read the PDF receipt: {exc}") from exc
    if not receipt_text.strip():
        raise RuntimeError("This PDF has no selectable text. Save a page as an image and scan it, or use a text-based PDF receipt.")
    api_key=os.environ.get("GROQ_API_KEY","").strip()
    if not api_key:raise RuntimeError("Set GROQ_API_KEY to extract payment receipt details.")
    payload={"model":"qwen/qwen3.8-27b","response_format":{"type":"json_object"},"messages":[{"role":"user","content":"Extract only clearly stated payment receipt fields from the text. Return JSON keys amount (number or 0), reference, payer_name, paid_at, payee_name. Do not infer missing values.\n\n"+receipt_text}]}
    req=urllib.request.Request("https://api.groq.com/openai/v1/chat/completions",data=json.dumps(payload).encode(),headers={"Authorization":f"Bearer {api_key}","Content-Type":"application/json"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=60) as response:data=json.loads(response.read().decode())
        return json.loads(data["choices"][0]["message"]["content"])
    except Exception as exc:raise RuntimeError(f"Could not extract payment PDF details: {exc}") from exc


def lookup_public_product_catalogue(barcode):
    """Look up label metadata from public product catalogues; never imports prices or stock."""
    barcode=re.sub(r"\D", "", str(barcode or ""))
    if not barcode:raise ValueError("Scan or enter a barcode first.")
    product=None
    hosts=("world.openfoodfacts.org","world.openproductsfacts.org","world.openbeautyfacts.org","world.openpetfoodfacts.org")
    fields="product_name,brands,categories,quantity,code,image_url,image_front_url"
    for host in hosts:
        url=f"https://{host}/api/v2/product/{barcode}?fields={fields}"
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"BillEaseAI/1.1 (desktop inventory lookup)"})
            with urllib.request.urlopen(req,timeout=8) as response:data=json.loads(response.read().decode("utf-8"))
            if data.get("status")==1:
                product=data.get("product",{});break
        except Exception:
            continue
    if not product:raise LookupError("No matching product was found in public catalogues. You can enter its details manually.")
    name=(product.get("product_name") or "").strip()
    if not name:raise LookupError("The catalogue entry has no product name.")
    category=(product.get("categories"," ").split(",")[0].strip().replace("en:","").replace("-"," ").title())
    brand=(product.get("brands") or "").split(",")[0].strip()
    image_url=(product.get("image_front_url") or product.get("image_url") or "").strip()
    quantity=(product.get("quantity") or "").strip()
    return {"name":name,"sku":barcode,"category":category,"unit":"pcs","brand":brand,"image_url":image_url,"catalogue_quantity":quantity}


def ai_extract_supplier_invoice(image_bytes, mime_type):
    """Read visible supplier-invoice line items from image or text-based PDF; review is required."""
    api_key=os.environ.get("GROQ_API_KEY","").strip()
    if not api_key:raise RuntimeError("Set GROQ_API_KEY to scan supplier invoice images.")
    prompt="Read visible supplier invoice details. Return JSON only: {supplier_name,invoice_date,items:[{name,sku,category,quantity,unit,unit_cost,tax_rate}]}. Use empty string for missing text and 0 for missing numbers. Do not guess, add rows, or treat a grand total as an item. Keep item unit_cost as the rate shown for one unit, before tax when possible."
    if mime_type=="application/pdf":
        try:
            from pypdf import PdfReader
            invoice_text="\n".join((page.extract_text() or "") for page in PdfReader(io.BytesIO(image_bytes)).pages[:10])[:24000]
        except ImportError as exc:raise RuntimeError("PDF scanning needs pypdf. Install it with: pip install pypdf") from exc
        if not invoice_text.strip():raise RuntimeError("This PDF has no selectable text. Use a clear image or text-based PDF.")
        user_content=prompt+"\n\nInvoice text:\n"+invoice_text
    else:
        image_url=f"data:{mime_type};base64,{base64.b64encode(image_bytes).decode('ascii')}"
        user_content=[{"type":"text","text":prompt},{"type":"image_url","image_url":{"url":image_url}}]
    payload={"model":"qwen/qwen3.8-27b","response_format":{"type":"json_object"},"messages":[{"role":"user","content":user_content}]}
    req=urllib.request.Request("https://api.groq.com/openai/v1/chat/completions",data=json.dumps(payload).encode(),headers={"Authorization":f"Bearer {api_key}","Content-Type":"application/json"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=60) as response:data=json.loads(response.read().decode())
        parsed=json.loads(data["choices"][0]["message"]["content"])
        items=parsed.get("items",[])
        if not isinstance(items,list):raise ValueError("AI returned an invalid item list.")
        clean=[]
        for item in items[:100]:
            if not isinstance(item,dict) or not str(item.get("name","")).strip():continue
            clean.append({
                "name":str(item.get("name","")).strip(),"sku":str(item.get("sku","")).strip(),
                "category":str(item.get("category","")).strip(),"quantity":max(0,float(item.get("quantity") or 0)),
                "unit":str(item.get("unit","")).strip() or "pcs","unit_cost":max(0,float(item.get("unit_cost") or 0)),
                "tax_rate":max(0,float(item.get("tax_rate") or 0)),
                "_invoice_date":str(parsed.get("invoice_date","")).strip(),"_supplier":str(parsed.get("supplier_name","")).strip(),
            })
        return clean
    except Exception as exc:raise RuntimeError(f"Could not scan supplier invoice: {exc}") from exc

# ==========================================
# MAIN APPLICATION
# ==========================================

class BillEaseApp:

    def __init__(self, root, role="admin", username="admin"):
        self.root = root
        self.role = role
        self.username = username
        self.root.title("BillEase AI")
        self.root.geometry("1440x900")
        self.root.minsize(1100, 700)
        self.root.configure(bg=BG)

        self.selected_id = None
        self.form_vars = {}

        self.create_styles()
        self.create_layout()
        self.show_dashboard()
        self.root.after(1800, self.run_automatic_backup)

    # ======================================
    # STYLES
    # ======================================

    def create_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=WHITE,
            foreground=DARK,
            rowheight=38,
            fieldbackground=WHITE,
            font=("Segoe UI", 10),
            borderwidth=0
        )
        style.configure("Product.Treeview",background=WHITE,foreground=DARK,fieldbackground=WHITE,
                         rowheight=44,font=("Segoe UI",11),borderwidth=0)
        style.configure("Product.Treeview.Heading",background=LIGHT_BLUE,foreground=DARK,
                         font=("Segoe UI",11,"bold"),relief="flat",padding=(10,8))
        style.map("Product.Treeview",background=[("selected","#DBEAFE")],foreground=[("selected",DARK)])
        style.configure("Employee.Treeview",background=WHITE,foreground=DARK,fieldbackground=WHITE,
                         rowheight=42,font=("Segoe UI",10),borderwidth=0)
        style.configure("Employee.Treeview.Heading",background=LIGHT_BLUE,foreground=DARK,
                         font=("Segoe UI",10,"bold"),relief="flat",padding=(9,8))
        style.map("Employee.Treeview",background=[("selected","#DBEAFE")],foreground=[("selected",DARK)])

        style.configure(
            "Treeview.Heading",
            background=LIGHT_BLUE,
            foreground=DARK,
            font=("Segoe UI", 10, "bold"),
            relief="flat"
        )

        style.configure("TCombobox",fieldbackground=WHITE,background=WHITE,foreground=DARK,arrowcolor=BLUE,padding=8)
        style.configure("Vertical.TScrollbar",background=BORDER,troughcolor=BG,arrowcolor=MUTED)
        style.configure("Horizontal.TScrollbar",background=BORDER,troughcolor=BG,arrowcolor=MUTED)

        style.map(
            "Treeview",
            background=[("selected", "#DBEAFE")],
            foreground=[("selected", DARK)]
        )

    # ======================================
    # MAIN LAYOUT
    # ======================================

    def create_layout(self):

        self.sidebar = tk.Frame(
            self.root, bg=SIDEBAR, width=236
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.main = tk.Frame(self.root, bg=BG)
        self.main.pack(side="right", fill="both", expand=True)

        self.create_sidebar()
        self.create_header()

        self.content = tk.Frame(self.main, bg=BG)
        self.content.pack(
            fill="both", expand=True,
            padx=PADDING["main"], pady=20
        )

    # ======================================
    # SIDEBAR
    # ======================================

    def create_sidebar(self):

        tk.Label(
            self.sidebar,
            text="▣  BillEase AI",
            bg=SIDEBAR,
            fg=WHITE,
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=18, pady=(26,30))

        tk.Label(
            self.sidebar,
            text="MAIN MENU",
            bg=SIDEBAR,
            fg="#9CA3AF",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", padx=18, pady=10)

        self.menu_buttons = {}

        menu = [
            ("▦", "Dashboard"),
            ("▤", "Products"),
            ("♧", "Customers"),
            ("♙", "Employees"),
            ("₹", "Bills"),
            ("◉", "Payments"),
            ("↗", "Customer Form"),
            ("▥", "Reports"),
            ("⚙", "Business Setup")
        ]

        for icon, name in menu:

            btn = tk.Button(
                self.sidebar,
                text=f"  {icon}    {name}",
                bg=SIDEBAR,
                fg=SIDEBAR_TEXT,
                font=("Segoe UI", 11, "bold"),
                anchor="w",
                relief="flat",
                bd=0,
                padx=14,
                pady=11,
                cursor="hand2",
                command=lambda p=name: self.navigate(p)
            )

            btn.pack(fill="x", padx=10, pady=3)
            self.menu_buttons[name] = btn

        tk.Label(
            self.sidebar,
            text="INVENTORY MANAGEMENT",
            bg=SIDEBAR,
            fg="#9CA3AF",
            font=("Segoe UI", 8, "bold")
        ).pack(side="bottom", anchor="w", padx=18, pady=20)

    # ======================================
    # HEADER
    # ======================================

    def create_header(self):

        header = tk.Frame(
            self.main, bg=WHITE, height=72
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        self.page_title = tk.Label(
            header,
            text="Dashboard",
            bg=WHITE,
            fg=DARK,
            font=("Segoe UI", 19, "bold")
        )
        self.page_title.pack(side="left", padx=24)
        with connect_db() as conn:
            business_name=conn.execute("SELECT value FROM app_settings WHERE key='business_name'").fetchone()
        tk.Label(header,text=(business_name[0] if business_name else "BillEase Business"),bg=WHITE,fg=MUTED,
                 font=("Segoe UI",10,"bold")).pack(side="right",padx=24)

    # ======================================
    # NAVIGATION
    # ======================================

    def navigate(self, page):

        current_page=self.page_title.cget("text")
        if page!=current_page:
            self._authorized_sensitive_page=None
        if page in ("Products","Business Setup") and getattr(self,"_authorized_sensitive_page",None)!=page:
            if not self.authorize_sensitive_page(page):
                return

        for name, button in self.menu_buttons.items():
            button.configure(
                bg=SIDEBAR_ACTIVE if name == page else SIDEBAR,
                fg=WHITE if name == page else SIDEBAR_TEXT
            )

        self.page_title.configure(text=page)

        if page == "Dashboard":
            self.show_dashboard()
        elif page == "Products":
            self.show_products()
        elif page == "Employees":
            self.show_employee_directory()
        elif page == "Customers":
            self.show_customers()
        elif page == "Bills":
            self.show_bills()
        elif page == "Payments":
            self.show_payments()
        elif page == "Customer Form":
            self.show_customer_form_page()
        elif page == "Reports":
            self.show_reports()
        elif page == "Business Setup":
            self.show_business_setup()

    def clear_content(self):

        for widget in self.content.winfo_children():
            widget.destroy()

    def authorize_sensitive_page(self,page):
        """Require a configured security PIN before opening protected pages."""
        if getattr(self,"_authorized_sensitive_page",None)==page:
            return True
        with connect_db() as conn:
            enabled=conn.execute("SELECT 1 FROM app_settings WHERE key='security_pin_hash'").fetchone() is not None
        if not enabled:
            if not messagebox.askyesno("Set a security PIN",f"Set a security PIN before opening {page}?",parent=self.root):
                return False
            self.set_security_pin()
            with connect_db() as conn:
                enabled=conn.execute("SELECT 1 FROM app_settings WHERE key='security_pin_hash'").fetchone() is not None
            if not enabled:
                return False
        elif not self.request_security_pin(f"open {page}"):
            return False
        self._authorized_sensitive_page=page
        return True

    def request_page_pin(self,page,action):
        """Reuse this page visit's PIN check for its edit/save actions."""
        if getattr(self,"_authorized_sensitive_page",None)==page:
            return True
        return self.authorize_sensitive_page(page)

    def add_table_scroll_controls(self, parent, table):
        controls = tk.Frame(parent, bg=parent.cget("bg"))
        controls.pack(side="right", padx=(6, 2))
        for label, delta in (("↑", -5), ("↓", 5)):
            tk.Button(controls, text=label, width=3, bg=LIGHT_BLUE, fg=DARK, relief="flat",
                      cursor="hand2", font=("Segoe UI", 10, "bold"),
                      command=lambda amount=delta, target=table: target.yview_scroll(amount, "units")).pack(side="left", padx=2)
        return controls

    # ======================================
    # DATABASE FUNCTIONS
    # ======================================

    def get_products(self):

        with connect_db() as conn:
            return conn.execute("""
                SELECT id, name, sku, category,
                       price, cost, stock, low_stock
                FROM products
                ORDER BY id DESC
            """).fetchall()

    # ======================================
    # DASHBOARD
    # ======================================

    def show_dashboard(self):

        self.clear_content()

        products = self.get_products()

        total_products = len(products)
        total_stock = sum(p[6] for p in products)
        inventory_value = sum(p[4] * p[6] for p in products)
        low_stock = sum(
            1 for p in products if p[6] <= p[7]
        )

        with connect_db() as conn:
            billed, bill_paid, invoice_count = conn.execute("SELECT COALESCE(SUM(total),0),COALESCE(SUM(paid),0),COUNT(*) FROM bills").fetchone()
            account_paid = conn.execute("SELECT COALESCE(SUM(amount),0) FROM customer_payments").fetchone()[0]
            open_count = conn.execute("SELECT COUNT(*) FROM bills WHERE paid<total").fetchone()[0]
            recent_customers = conn.execute("SELECT name,COALESCE(phone,'') FROM customers ORDER BY id DESC LIMIT 200").fetchall()
            sold_30_days = dict(conn.execute("SELECT product_id,SUM(quantity) FROM invoice_lines l JOIN bills b ON b.id=l.bill_id WHERE product_id IS NOT NULL AND b.bill_date>=datetime('now','-30 days') GROUP BY product_id").fetchall())
            recent_payments = conn.execute("""
                SELECT name, amount, payment_mode, payment_date FROM (
                    SELECT c.name, p.amount, p.payment_mode, p.payment_date
                    FROM business_payments p JOIN customers c ON c.id=p.customer_id
                    UNION ALL
                    SELECT c.name, p.amount, p.payment_mode, p.payment_date
                    FROM customer_payments p JOIN customers c ON c.id=p.customer_id
                ) ORDER BY payment_date DESC LIMIT 5
            """).fetchall()
        collected = bill_paid + account_paid
        outstanding = max(0, billed - collected)

        dashboard_title_row = tk.Frame(self.content, bg=BG)
        dashboard_title_row.pack(fill="x", pady=(0, 2))
        tk.Label(dashboard_title_row,text="▦  Business overview",bg=BG,fg=DARK,font=("Segoe UI",20,"bold")).pack(side="left",anchor="w")
        tk.Button(dashboard_title_row, text="＋  Add Product", bg=BLUE, fg=WHITE, relief="flat", cursor="hand2",
                  font=("Segoe UI", 10, "bold"), padx=15, pady=8,
                  command=lambda: self.navigate("Products")).pack(side="right")
        tk.Label(self.content,text="A quick view of sales, collections, balances, and inventory.",bg=BG,fg=MUTED,font=("Segoe UI",10)).pack(anchor="w",pady=(0,14))

        # SUMMARY CARDS

        cards = tk.Frame(self.content, bg=BG)
        cards.pack(fill="x", pady=(0, 20))

        card_data = [
            ("Total billed", f"₹{billed:,.2f}", BLUE, "All recorded invoices"),
            ("Amount collected", f"₹{collected:,.2f}", GREEN, "Payments received"),
            ("Outstanding", f"₹{outstanding:,.2f}", WARNING, f"{open_count} invoices still due"),
            ("Low stock items", low_stock, RED, f"Across {total_products} products")
        ]

        for title, value, color, note in card_data:

            card = tk.Frame(
                cards,
                bg=WHITE,
                highlightbackground=BORDER,
                highlightthickness=1
            )
            card.pack(
                side="left",
                fill="both",
                expand=True,
                padx=7
            )

            tk.Frame(card,bg=color,width=5).pack(side="left",fill="y")
            card_body=tk.Frame(card,bg=WHITE)
            card_body.pack(side="left",fill="both",expand=True)

            tk.Label(
                card_body,
                text=title,
                bg=WHITE,
                fg=MUTED,
                font=("Segoe UI", 9, "bold")
            ).pack(anchor="w", padx=18, pady=(15, 4))

            tk.Label(
                card_body,
                text=str(value),
                bg=WHITE,
                fg=color,
                font=("Segoe UI", 20, "bold")
            ).pack(anchor="w", padx=18)
            tk.Label(card_body,text=note,bg=WHITE,fg=MUTED,font=("Segoe UI",9)).pack(anchor="w",padx=18,pady=(2,14))

        # CHART AND LOW STOCK

        middle = tk.Frame(self.content, bg=BG)
        middle.pack(fill="both", expand=True)

        chart_card = tk.Frame(
            middle,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        chart_card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 10)
        )

        tk.Label(
            chart_card,
            text="▤  Inventory by Category",
            bg=WHITE,
            fg=DARK,
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", padx=20, pady=18)

        chart = tk.Canvas(
            chart_card,
            bg=WHITE,
            highlightthickness=0,
            height=270
        )
        chart.pack(fill="both", expand=True, padx=15, pady=10)

        chart.bind(
            "<Configure>",
            lambda event: self.draw_inventory_chart(
                chart, self.get_products()
            )
        )

        self.draw_inventory_chart(chart, products)

        # LOW STOCK PANEL

        stock_card = tk.Frame(
            middle,
            bg=WHITE,
            width=270,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        stock_card.pack(
            side="right",
            fill="y",
            padx=(10, 0)
        )
        stock_card.pack_propagate(False)

        tk.Label(
            stock_card,
            text="Stock forecast · 30-day sales",
            bg=WHITE,
            fg=DARK,
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", padx=18, pady=18)

        low_products = [
            p for p in products if p[6] <= p[7]
        ]

        if not low_products:
            tk.Label(
                stock_card,
                text="No low-stock products",
                bg=WHITE,
                fg=GREEN,
                font=("Segoe UI", 10)
            ).pack(anchor="w", padx=18, pady=15)

        for p in low_products[:6]:

            row = tk.Frame(stock_card, bg=WHITE)
            row.pack(fill="x", padx=15, pady=5)

            tk.Label(
                row,
                text=p[1],
                bg=WHITE,
                fg=DARK,
                font=("Segoe UI", 9, "bold"),
                wraplength=160,
                justify="left"
            ).pack(anchor="w")

            daily_sales=float(sold_30_days.get(p[0],0) or 0)/30
            days_left=int(p[6]/daily_sales) if daily_sales>0 else None
            target_stock=int(daily_sales*14+0.9999)
            restock=max(0,target_stock-p[6])
            forecast=f"Stock {p[6]} · alert {p[7]} · "
            forecast+=f"~{days_left} days left" if days_left is not None else "no recent sales"
            if restock:
                forecast+=f" · restock {restock}"
            tk.Label(
                row,
                text=forecast,
                bg=WHITE,
                fg=RED,
                font=("Segoe UI", 9)
            ).pack(anchor="w")

        tk.Button(
            stock_card,
            text="Manage Products",
            bg=BLUE,
            fg=WHITE,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=8,
            command=lambda: self.navigate("Products")
        ).pack(anchor="w", padx=18, pady=15)

        # Compact name lists make the dashboard useful for daily work as well as totals.
        quick_row = tk.Frame(self.content, bg=BG)
        quick_row.pack(fill="x", pady=(14, 0))
        quick_cards = []
        for title, accent in (("Employees · up to 200", BLUE), ("Products · up to 200", GREEN), ("Recent payments", WARNING)):
            panel = tk.Frame(quick_row, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
            panel.pack(side="left", fill="both", expand=True, padx=5)
            quick_cards.append(panel)
            header = tk.Frame(panel, bg=WHITE)
            header.pack(fill="x", padx=13, pady=(10, 5))
            tk.Frame(header, bg=accent, width=4, height=16).pack(side="left", padx=(0, 8))
            tk.Label(header, text=title, bg=WHITE, fg=DARK, font=("Segoe UI", 10, "bold")).pack(side="left")
            for widget in (panel, header):
                widget.bind("<Enter>", lambda _event, target=panel: self.animate_card_border(target, True))
                widget.bind("<Leave>", lambda _event, target=panel: self.animate_card_border(target, False))
        customer_panel, product_panel, payment_panel = quick_cards

        def add_scrollable_names(panel, rows, formatter, empty_text):
            list_area = tk.Frame(panel, bg=WHITE)
            list_area.pack(fill="both", expand=True, padx=10, pady=(0, 4))
            names = tk.Listbox(list_area, height=5, bg=WHITE, fg=DARK, relief="flat", bd=0,
                               highlightthickness=0, activestyle="none", font=("Segoe UI", 9),
            selectbackground="#DBEAFE", selectforeground=DARK)
            scrollbar = ttk.Scrollbar(list_area, orient="vertical", command=names.yview)
            names.configure(yscrollcommand=scrollbar.set)
            names.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            for row in rows[:200]:
                names.insert("end", formatter(row))
            if not rows:
                names.insert("end", empty_text)

        add_scrollable_names(customer_panel, recent_customers,
                             lambda row: f"{row[0]}   ·   {row[1]}" if row[1] else row[0], "No employees yet")
        tk.Button(customer_panel, text="Manage employees", bg=LIGHT_BLUE, fg=DARK, relief="flat", cursor="hand2",
                  font=("Segoe UI", 9, "bold"), padx=10, pady=5,
                  command=lambda: self.navigate("Employees")).pack(anchor="e", padx=12, pady=(2, 9))
        add_scrollable_names(product_panel, products,
                             lambda row: f"{row[1]}   ·   stock {row[6]}", "No products yet")
        for payment in recent_payments or [None]:
            label = f"{payment[0]}   ·   ₹{payment[1]:,.0f} · {payment[2]}" if payment else "No payments yet"
            tk.Label(payment_panel, text=label, bg=WHITE, fg=DARK if payment else MUTED,
                     font=("Segoe UI", 9), anchor="w").pack(fill="x", padx=17, pady=2)
        tk.Button(product_panel, text="＋ Add product", bg=BLUE, fg=WHITE, relief="flat",
                  font=("Segoe UI", 9, "bold"), padx=10, pady=5,
                  command=lambda: self.navigate("Products")).pack(anchor="e", padx=12, pady=(4, 9))

    def animate_card_border(self, card, active):
        """A tiny three-step border pulse for dashboard cards."""
        shades = ("#C5D9E2", "#8CBCCB", BLUE) if active else ("#8CBCCB", "#C5D9E2", BORDER)
        for step, shade in enumerate(shades):
            try:
                def apply_border(color=shade, target=card):
                    try:
                        target.configure(highlightbackground=color)
                    except tk.TclError:
                        pass
                card.after(step * 35, apply_border)
            except tk.TclError:
                return

    # ======================================
    # INVENTORY GRAPH
    # ======================================

    def draw_inventory_chart(self, canvas, products):

        canvas.delete("all")

        width = canvas.winfo_width()
        height = canvas.winfo_height()

        if width < 150 or height < 150:
            return

        categories = {}

        for product in products:

            category = product[3] or "Other"

            categories[category] = (
                categories.get(category, 0) + product[6]
            )

        if not categories:

            canvas.create_text(
                width / 2,
                height / 2,
                text="No product data yet\nAdd products to view inventory graph",
                fill=MUTED,
                font=("Segoe UI", 12),
                justify="center"
            )
            return

        colors = [
            BLUE, GREEN, PURPLE,
            WARNING, RED, PURPLE,
            "#63748B"
        ]

        max_value = max(categories.values()) or 1

        left = 120
        right = width - 65
        top = 25
        bottom = height - 35

        chart_height = bottom - top

        rows = len(categories)
        row_height = min(48, chart_height / max(rows, 1))

        for i, (category, quantity) in enumerate(categories.items()):

            y = top + i * row_height

            if y + row_height > bottom + 5:
                break

            canvas.create_text(
                left - 10,
                y + 12,
                text=category[:15],
                anchor="e",
                fill=DARK,
                font=("Segoe UI", 9)
            )

            bar_width = (quantity / max_value) * (
                right - left - 40
            )

            canvas.create_rectangle(
                left,
                y + 3,
                left + bar_width,
                y + 23,
                fill=colors[i % len(colors)],
                outline=""
            )

            canvas.create_text(
                left + bar_width + 8,
                y + 13,
                text=str(quantity),
                anchor="w",
                fill=MUTED,
                font=("Segoe UI", 9, "bold")
            )

    # ======================================
    # PRODUCTS PAGE
    # ======================================

    def show_products(self):

        self.clear_content()
        with connect_db() as conn:
            saved_categories = [row[0] for row in conn.execute("SELECT DISTINCT category FROM products WHERE TRIM(COALESCE(category,''))<>'' ORDER BY category")]
            saved_units = [row[0] for row in conn.execute("SELECT DISTINCT unit FROM products WHERE TRIM(COALESCE(unit,''))<>'' ORDER BY unit")]
        self.catalog_category_by_name = {name.casefold(): category for category, names in PRODUCT_CATALOG.items() for name in names}
        catalog_names = [name for names in PRODUCT_CATALOG.values() for name in names]
        saved_products = [row[1] for row in self.get_products()]
        self.product_name_options = sorted(set(catalog_names + saved_products), key=str.casefold)

        # FORM

        form_card = tk.Frame(
            self.content,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        form_card.pack(fill="x", pady=(0, 15))

        tk.Label(
            form_card,
            text="▣  Product Information",
            bg=WHITE,
            fg=DARK,
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", padx=20, pady=15)

        fields = [
            ("Product Name", "name"),
            ("SKU / Barcode", "sku"),
            ("Category", "category"),
            ("Brand", "brand"),
            ("Product Image URL", "image_url"),
            ("Unit", "unit"),
            ("Selling Price", "price"),
            ("Tax Rate %", "tax_rate"),
            ("Purchase Cost", "cost"),
            ("Available Stock", "stock"),
            ("Low Stock Alert", "low_stock")
        ]

        self.form_vars = {}

        field_area = tk.Frame(form_card, bg=WHITE)
        field_area.pack(fill="x", padx=15)

        for i, (label, key) in enumerate(fields):

            r = i // 4
            c = i % 4

            field = tk.Frame(field_area, bg=WHITE)
            field.grid(
                row=r, column=c,
                sticky="ew",
                padx=7, pady=7
            )

            tk.Label(
                field,
                text=label,
                bg=WHITE,
                fg=MUTED,
                font=("Segoe UI", 9, "bold")
            ).pack(anchor="w", pady=(0, 5))

            var = tk.StringVar()
            self.form_vars[key] = var

            if key == "name":
                entry = ttk.Combobox(
                    field,
                    textvariable=var,
                    values=self.product_name_options,
                    state="normal",
                )
                self.product_name_combo = entry
                entry.bind("<<ComboboxSelected>>", self.on_catalog_product_selected)
            elif key in ("category", "unit"):
                if key == "category":
                    values = sorted(
                        set(tuple(PRODUCT_CATALOG) + tuple(saved_categories)),
                        key=str.casefold,
                    )
                else:
                    standard_units = ("pcs", "kg", "g", "mg", "L", "ml", "m", "cm", "box", "pack", "hour", "day", "service")
                    values = sorted(set(standard_units + tuple(saved_units)), key=str.casefold)
                entry = ttk.Combobox(field, textvariable=var, values=values, state="normal")
                if key == "category":
                    self.product_category_combo = entry
                    entry.bind("<<ComboboxSelected>>", self.filter_product_catalog)
                else:
                    self.product_unit_combo = entry
            else:
                entry = tk.Entry(
                    field,
                    textvariable=var,
                    font=("Segoe UI", 10),
                    relief="solid",
                    bd=1,
                )
                if key=="sku":
                    self.product_sku_entry=entry
                    entry.bind("<Return>",self.handle_product_barcode_scan)

            entry.pack(fill="x", ipady=7)

        tk.Label(field_area, text="Choose from 200 starter products, or type your own product, category, or unit.",
                 bg=WHITE, fg=MUTED, font=("Segoe UI", 8)).grid(row=3, column=0, columnspan=4, sticky="w", padx=7, pady=(0, 7))

        for c in range(4):
            field_area.columnconfigure(c, weight=1)

        # BUTTONS

        buttons = tk.Frame(form_card, bg=WHITE)
        buttons.pack(fill="x", padx=20, pady=15)

        self.make_button(
            buttons, "Add Product", GREEN,
            self.add_product
        )

        self.ai_invoice_scan_button=tk.Button(buttons,text="AI scan supplier invoice",bg=LIGHT_BLUE,fg=DARK,
                font=("Segoe UI",9,"bold"),relief="flat",padx=10,pady=9,cursor="hand2",
                command=self.scan_supplier_invoice_with_ai)
        self.ai_invoice_scan_button.pack(side="left",padx=5)
        tk.Button(buttons,text="Barcode lookup",bg=LIGHT_BLUE,fg=DARK,font=("Segoe UI",9,"bold"),
                  relief="flat",padx=10,pady=9,cursor="hand2",command=self.lookup_product_catalogue).pack(side="left",padx=5)
        tk.Button(buttons,text="View product image",bg=LIGHT_BLUE,fg=DARK,font=("Segoe UI",9,"bold"),
                  relief="flat",padx=10,pady=9,cursor="hand2",command=self.open_product_image).pack(side="left",padx=5)

        self.make_button(
            buttons, "Update Product", BLUE,
            self.update_product
        )

        self.make_button(
            buttons, "Delete Product", RED,
            self.delete_product
        )

        self.make_button(
            buttons, "Clear Form", MUTED,
            self.clear_form
        )

        # SEARCH

        search_frame = tk.Frame(self.content, bg=BG)
        search_frame.pack(fill="x", pady=(0, 10))
        title_area = tk.Frame(search_frame, bg=BG)
        title_area.pack(side="left", fill="x", expand=True)
        tk.Label(title_area, text="▤  Inventory List", bg=BG, fg=DARK,
                 font=("Segoe UI", 15, "bold")).pack(anchor="w")
        tk.Label(title_area, text="Use a USB barcode scanner in the SKU field; saved items load instantly and new barcodes fetch catalogue details automatically.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 0))
        tk.Button(title_area,text="Import products CSV",bg=LIGHT_BLUE,fg=DARK,relief="flat",cursor="hand2",
                  command=lambda:self.import_records_csv("products")).pack(anchor="w",pady=(5,0))

        self.search_var = tk.StringVar()
        search_card = tk.Frame(search_frame, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        search_card.pack(side="right", padx=(12, 0))
        tk.Label(search_card, text="⌕", bg=WHITE, fg=BLUE, font=("Segoe UI", 17, "bold")).pack(side="left", padx=(10, 3))
        search_entry = tk.Entry(search_card, textvariable=self.search_var, width=27,
                                font=("Segoe UI", 10), relief="flat", bd=0)
        search_entry.pack(side="left", ipady=10, padx=(2, 7))
        search_entry.bind("<Return>", self.handle_inventory_scan)
        tk.Button(search_card, text="▦ Scan", bg=LIGHT_BLUE, fg=DARK, relief="flat", cursor="hand2",
                  font=("Segoe UI", 9, "bold"), padx=10, pady=6,
                  command=lambda: search_entry.focus_set()).pack(side="left", padx=3, pady=4)
        tk.Button(search_card, text="Clear", bg=WHITE, fg=MUTED, relief="flat", cursor="hand2",
                  command=lambda: self.search_var.set("")).pack(side="left", padx=(2, 7))
        tk.Button(search_card, text="Search", bg=BLUE, fg=WHITE, relief="flat", cursor="hand2",
                  font=("Segoe UI", 9, "bold"), padx=10, pady=6,
                  command=self.refresh_product_table).pack(side="left", padx=(0, 7), pady=4)
        self.inventory_scan_status = tk.Label(search_frame, text="", bg=BG, fg=GREEN, font=("Segoe UI", 9, "bold"))
        self.inventory_scan_status.pack(side="right", padx=(0, 10))

        self.search_var.trace_add(
            "write",
            lambda *args: self.refresh_product_table()
        )

        category_filter = tk.Frame(self.content, bg=BG)
        category_filter.pack(fill="x", pady=(0, 8))
        tk.Label(category_filter, text="Browse category", bg=BG, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=(2, 8))
        self.inventory_category_var = tk.StringVar(value="All categories")
        category_values = ["All categories"] + sorted(set(tuple(PRODUCT_CATALOG) + tuple(saved_categories)), key=str.casefold)
        self.inventory_category_combo = ttk.Combobox(category_filter, textvariable=self.inventory_category_var,
                values=category_values, state="readonly", width=24)
        self.inventory_category_combo.pack(side="left")
        self.inventory_category_combo.bind("<<ComboboxSelected>>", lambda _event: self.refresh_product_table())
        tk.Label(category_filter, text="Choose a category to see its saved items; choose a catalogue name in the form to start a new item.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 8)).pack(side="left", padx=10)

        # TABLE

        table_card = tk.Frame(
            self.content,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        table_card.pack(fill="both", expand=True)

        columns = ("id","name","sku","category","price","cost","stock","low_stock","units_sold","sales_total","stock_status")

        self.table = ttk.Treeview(
            table_card,
            columns=columns,
            show="headings",
            style="Product.Treeview",
            height=16
        )
        self.table.tag_configure("low_stock",foreground=RED)
        self.add_table_scroll_controls(category_filter, self.table)

        headings = {
            "id": "ID",
            "name": "PRODUCT NAME",
            "sku": "SKU",
            "category": "CATEGORY",
            "price": "SELLING PRICE",
            "cost": "COST",
            "stock": "STOCK",
            "low_stock": "LOW STOCK",
            "units_sold": "UNITS SOLD",
            "sales_total": "SALES TOTAL",
            "stock_status": "STOCK STATUS"
        }

        widths = {
            "id": 45,
            "name": 190,
            "sku": 110,
            "category": 120,
            "price": 110,
            "cost": 110,
            "stock": 85,
            "low_stock": 90,
            "units_sold": 95,
            "sales_total": 125,
            "stock_status": 115
        }

        for col in columns:

            self.table.heading(
                col, text=headings[col]
            )

            self.table.column(
                col,
                width=widths[col],
                anchor="center"
            )

        self.table.pack(
            fill="both", expand=True,
            padx=12, pady=12
        )

        self.table.bind(
            "<<TreeviewSelect>>",
            self.select_product
        )

        self.table.bind("<Double-1>", self.select_product)

        self.refresh_product_table()
        # USB barcode scanners behave like keyboards and usually send Enter after the code.
        # Focus the SKU field so scanning immediately triggers catalogue/product lookup.
        try:
            self.product_sku_entry.focus_set()
            self.inventory_scan_status.configure(text="Ready · scan a barcode into the SKU field to load product details", fg=BLUE)
        except (AttributeError, tk.TclError):
            pass

    def handle_inventory_scan(self, _event=None):
        """Barcode scanners type the SKU and send Return; match and load that item."""
        scanned_code = self.search_var.get().strip()
        if not scanned_code:
            return "break"
        with connect_db() as conn:
            product = conn.execute(
                "SELECT id, sku FROM products WHERE UPPER(TRIM(COALESCE(sku,'')))=UPPER(?) LIMIT 1",
                (scanned_code,),
            ).fetchone()
        if not product:
            if hasattr(self, "inventory_scan_status") and self.inventory_scan_status.winfo_exists():
                self.inventory_scan_status.configure(text="Not in inventory · looking up barcode details…", fg=WARNING)
            self.form_vars["sku"].set(scanned_code)
            self.lookup_product_catalogue(barcode=scanned_code,automatic=True)
            return "break"
        self.search_var.set(product[1] or scanned_code)
        self.refresh_product_table()
        for item in self.table.get_children():
            values = self.table.item(item, "values")
            if values and int(values[0]) == int(product[0]):
                self.table.selection_set(item)
                self.table.focus(item)
                self.table.see(item)
                self.select_product()
                break
        with connect_db() as conn:
            details = conn.execute("SELECT name,price,stock,unit FROM products WHERE id=?", (product[0],)).fetchone()
        if details and hasattr(self, "inventory_scan_status") and self.inventory_scan_status.winfo_exists():
            self.inventory_scan_status.configure(
                text=f"✓ {details[0]} · ₹{details[1]:,.2f} · stock {details[2]} {details[3]}", fg=GREEN
            )
        return "break"

    def handle_product_barcode_scan(self,_event=None):
        """Load a saved product by barcode, or fill known catalogue details for review."""
        scanned_code=self.form_vars["sku"].get().strip()
        if not scanned_code:return "break"
        with connect_db() as conn:
            product=conn.execute("SELECT id,sku,name,price,stock,unit FROM products WHERE UPPER(TRIM(COALESCE(sku,'')))=UPPER(?) LIMIT 1",(scanned_code,)).fetchone()
        if product:
            self.search_var.set(product[1] or scanned_code)
            self.inventory_category_var.set("All categories")
            self.refresh_product_table()
            for item in self.table.get_children():
                values=self.table.item(item,"values")
                if values and int(values[0])==int(product[0]):
                    self.table.selection_set(item);self.table.focus(item);self.table.see(item);self.select_product();break
            self.inventory_scan_status.configure(text=f"✓ {product[2]} · ₹{product[3]:,.2f} · stock {product[4]} {product[5]}",fg=GREEN)
            return "break"
        self.inventory_scan_status.configure(text="Not in inventory · looking up barcode details…",fg=WARNING)
        self.lookup_product_catalogue(barcode=scanned_code,automatic=True)
        return "break"

    def import_records_csv(self,kind):
        if kind not in ("products","customers"):return
        if not self.request_security_pin(f"import {kind}"):
            return
        path=filedialog.askopenfilename(title=f"Import {kind} from CSV",filetypes=(("CSV files","*.csv"),))
        if not path:return
        imported=skipped=0
        try:
            with open(path,"r",newline="",encoding="utf-8-sig") as input_file:
                reader=csv.DictReader(input_file)
                if not reader.fieldnames:raise ValueError("The CSV needs a header row.")
                normalized={str(name).strip().casefold():name for name in reader.fieldnames if name}
                def cell(row,*keys):
                    for key in keys:
                        source=normalized.get(key.casefold())
                        if source is not None:return str(row.get(source) or "").strip()
                    return ""
                with connect_db() as conn:
                    for row in reader:
                        try:
                            name=cell(row,"name","product name","customer name")
                            if not name:raise ValueError
                            if kind=="products":
                                sku=cell(row,"sku","code","barcode")
                                if not sku:raise ValueError
                                category=cell(row,"category")
                                unit=cell(row,"unit") or "pcs"
                                price=float(cell(row,"price","selling price") or 0)
                                cost=float(cell(row,"cost","purchase cost") or 0)
                                stock=int(float(cell(row,"stock","quantity") or 0))
                                low_stock=int(float(cell(row,"low stock","low_stock","reorder level") or 5))
                                tax=float(cell(row,"tax rate","tax_rate","gst rate") or 0)
                                if min(price,cost,stock,low_stock,tax)<0 or tax>100:raise ValueError
                                conn.execute("INSERT INTO products(name,sku,category,price,cost,stock,low_stock,unit,tax_rate) VALUES (?,?,?,?,?,?,?,?,?) ON CONFLICT(sku) DO UPDATE SET name=excluded.name,category=excluded.category,price=excluded.price,cost=excluded.cost,stock=excluded.stock,low_stock=excluded.low_stock,unit=excluded.unit,tax_rate=excluded.tax_rate",(name,sku,category,price,cost,stock,low_stock,unit,tax))
                            else:
                                phone=cell(row,"phone","mobile","phone number") or None
                                email=cell(row,"email");address=cell(row,"address");gstin=cell(row,"gstin","tax id")
                                if len(re.sub(r"\s+","",gstin))==15 and not valid_gstin_format(gstin):raise ValueError
                                if phone:
                                    conn.execute("INSERT INTO customers(name,phone,email,address,gstin) VALUES (?,?,?,?,?) ON CONFLICT(phone) DO UPDATE SET name=excluded.name,email=excluded.email,address=excluded.address,gstin=excluded.gstin",(name,phone,email,address,gstin))
                                else:
                                    conn.execute("INSERT INTO customers(name,phone,email,address,gstin) VALUES (?,NULL,?,?,?)",(name,email,address,gstin))
                            imported+=1
                        except (ValueError,TypeError,sqlite3.Error):skipped+=1
        except (OSError,UnicodeError,csv.Error,ValueError) as exc:
            messagebox.showerror("CSV import",f"Could not import this file: {exc}");return
        if kind=="products":
            self.refresh_product_table();self.refresh_product_catalog_choices()
        else:self.refresh_customer_table()
        headers=("name, sku, category, price, cost, stock, low_stock, unit, tax_rate" if kind=="products" else "name, phone, email, address, gstin")
        messagebox.showinfo("Import complete",f"{imported} {kind} row(s) imported or updated. {skipped} row(s) skipped.\n\nCSV columns: {headers}")

    def open_product_image(self):
        image_url=self.form_vars.get("image_url",tk.StringVar()).get().strip()
        if not image_url:
            messagebox.showinfo("Product image","No image URL is saved. Try Barcode lookup first.")
            return
        if not image_url.lower().startswith(("https://","http://")):
            messagebox.showwarning("Invalid image URL","The saved image URL is not a web address.")
            return
        try:
            webbrowser.open(image_url)
        except Exception as exc:
            messagebox.showerror("Product image",f"Could not open image link: {exc}")

    def lookup_product_catalogue(self,barcode=None,automatic=False):
        barcode=(barcode or "").strip()
        if not barcode:
            barcode=self.form_vars.get("sku",tk.StringVar()).get().strip()
        if not barcode and hasattr(self,"search_var"):
            barcode=self.search_var.get().strip()
        if not barcode:
            if not automatic:messagebox.showinfo("Barcode lookup","Scan or enter a barcode in Inventory List or the SKU field first.")
            return
        def worker():
            try:
                item=lookup_public_product_catalogue(barcode)
                self.root.after(0,lambda:self.apply_catalogue_product(item,automatic))
            except Exception as exc:
                error=str(exc)
                self.root.after(0,lambda:self.finish_barcode_lookup(error,automatic))
        threading.Thread(target=worker,daemon=True).start()

    def apply_catalogue_product(self,item,automatic=False):
        # Fill all available catalogue fields in the Products form immediately after a scan.
        for key,value in item.items():
            if key in self.form_vars:
                self.form_vars[key].set(value)
        if hasattr(self,"inventory_scan_status") and self.inventory_scan_status.winfo_exists():
            brand_note=(f" · Brand: {item.get('brand')}" if item.get('brand') else "")
            image_note=(" · image link loaded" if item.get("image_url") else " · image unavailable")
            self.inventory_scan_status.configure(
                text=f"✓ Product details loaded: {item.get('name') or item.get('sku')}{brand_note}{image_note} · enter price, cost & stock, then Add Product",
                fg=GREEN
            )
        # Put focus back on barcode input to allow the next product to be scanned.
        try:
            self.product_sku_entry.focus_set()
        except (AttributeError, tk.TclError):
            pass
        if not automatic:
            messagebox.showinfo("Catalogue details loaded","Product name, barcode, brand (if available), category, unit and image link have been filled. Review them, enter your selling price, purchase cost and stock, then save.")

    def finish_barcode_lookup(self,error,automatic=False):
        if automatic and hasattr(self,"inventory_scan_status") and self.inventory_scan_status.winfo_exists():
            self.inventory_scan_status.configure(text="Barcode not found online · enter product details manually",fg=RED)
        else:
            messagebox.showerror("Barcode lookup",error)

    def filter_product_catalog(self, _event=None):
        category = self.form_vars.get("category", tk.StringVar()).get().strip()
        if category:
            names = list(PRODUCT_CATALOG.get(category, ()))
            names.extend(product[1] for product in self.get_products() if (product[3] or "").casefold() == category.casefold())
        else:
            names = self.product_name_options
        if hasattr(self, "product_name_combo") and self.product_name_combo.winfo_exists():
            self.product_name_combo.configure(values=sorted(set(names), key=str.casefold))

    def scan_supplier_invoice_with_ai(self):
        path=filedialog.askopenfilename(title="Choose supplier invoice",filetypes=(("Invoice image or PDF","*.png *.jpg *.jpeg *.webp *.pdf"),))
        if not path:return
        try:
            with open(path,"rb") as invoice_file:image_bytes=invoice_file.read(8*1024*1024+1)
            if len(image_bytes)>8*1024*1024:
                messagebox.showerror("Image too large","Choose an image smaller than 8 MB.");return
        except OSError as exc:
            messagebox.showerror("Could not read image",str(exc));return
        mime={".png":"image/png",".jpg":"image/jpeg",".jpeg":"image/jpeg",".webp":"image/webp",".pdf":"application/pdf"}.get(os.path.splitext(path)[1].lower())
        if not mime:
            messagebox.showerror("Unsupported file","Choose a PNG, JPG, WEBP image, or text-based PDF invoice.");return
        self.ai_invoice_scan_button.configure(state="disabled",text="Scanning…")
        def worker():
            try:
                items=ai_extract_supplier_invoice(image_bytes,mime)
                self.root.after(0,lambda:self.show_supplier_invoice_scan(items))
            except Exception as exc:
                error=str(exc)
                self.root.after(0,lambda:self.finish_supplier_invoice_scan(error))
        threading.Thread(target=worker,daemon=True).start()

    def finish_supplier_invoice_scan(self,error):
        self.ai_invoice_scan_button.configure(state="normal",text="AI scan supplier invoice")
        messagebox.showerror("Invoice scan",error)

    def show_supplier_invoice_scan(self,items):
        self.ai_invoice_scan_button.configure(state="normal",text="AI scan supplier invoice")
        if not items:
            messagebox.showinfo("Invoice scan","No readable product rows were found. Try a clearer image.");return
        window=tk.Toplevel(self.root);window.title("Review scanned supplier items");window.geometry("900x460");window.configure(bg=BG)
        tk.Label(window,text="Review extracted items",bg=BG,fg=DARK,font=("Segoe UI",15,"bold")).pack(anchor="w",padx=16,pady=(13,3))
        first=items[0]
        scanned_meta="  ·  ".join(value for value in (first.get("_supplier",""),first.get("_invoice_date","")) if value)
        tk.Label(window,text=(f"Supplier / invoice date: {scanned_meta}  ·  " if scanned_meta else "")+"AI may misread printed invoices. Review every row; selling prices are not guessed.",bg=BG,fg=MUTED,font=("Segoe UI",9)).pack(anchor="w",padx=16,pady=(0,8))
        cols=("name","sku","category","quantity","unit","cost","tax")
        table=ttk.Treeview(window,columns=cols,show="headings",height=12)
        for col,label,width in (("name","PRODUCT",230),("sku","SKU",115),("category","CATEGORY",135),("quantity","QTY",70),("unit","UNIT",70),("cost","UNIT COST",100),("tax","TAX %",75)):
            table.heading(col,text=label);table.column(col,width=width,anchor="center")
        table.pack(fill="both",expand=True,padx=14,pady=5)
        for index,item in enumerate(items):
            table.insert("","end",iid=str(index),values=(item["name"],item["sku"],item["category"],item["quantity"],item["unit"],item["unit_cost"],item["tax_rate"]))
        def use_selected(_event=None):
            selected=table.selection()
            if not selected:return
            values=table.item(selected[0],"values")
            existing=None
            if values[1]:
                with connect_db() as conn:existing=conn.execute("SELECT id,stock,price FROM products WHERE sku=? COLLATE NOCASE LIMIT 1",(values[1],)).fetchone()
            current_stock=int(existing[1] or 0) if existing else 0
            suggested_stock=current_stock+int(float(values[3] or 0))
            for key,value in (("name",values[0]),("sku",values[1]),("category",values[2]),("stock",suggested_stock),("unit",values[4]),("cost",values[5]),("tax_rate",values[6])):
                self.form_vars[key].set(str(value))
            self.form_vars["price"].set(str(existing[2]) if existing else "")
            self.selected_id=existing[0] if existing else None
            self.filter_product_catalog()
            window.destroy()
        table.bind("<Double-1>",use_selected)
        actions=tk.Frame(window,bg=BG);actions.pack(fill="x",padx=14,pady=9)
        tk.Button(actions,text="Use selected in product form",bg=BLUE,fg=WHITE,relief="flat",command=use_selected).pack(side="right")

    def on_catalog_product_selected(self, _event=None):
        product_name = self.form_vars.get("name", tk.StringVar()).get().strip()
        category = self.catalog_category_by_name.get(product_name.casefold(), "")
        existing = next((product for product in self.get_products() if product[1].casefold() == product_name.casefold()), None)
        if existing and existing[3]:
            category = existing[3]
        if category:
            self.form_vars["category"].set(category)
            self.filter_product_catalog()

    def refresh_product_catalog_choices(self):
        with connect_db() as conn:
            categories = [row[0] for row in conn.execute("SELECT DISTINCT category FROM products WHERE TRIM(COALESCE(category,''))<>'' ORDER BY category")]
            units = [row[0] for row in conn.execute("SELECT DISTINCT unit FROM products WHERE TRIM(COALESCE(unit,''))<>'' ORDER BY unit")]
        product_names = [row[1] for row in self.get_products()]
        self.product_name_options = sorted(set(product_names + [name for names in PRODUCT_CATALOG.values() for name in names]), key=str.casefold)
        if hasattr(self, "product_name_combo") and self.product_name_combo.winfo_exists():
            self.product_name_combo.configure(values=self.product_name_options)
        if hasattr(self, "product_category_combo") and self.product_category_combo.winfo_exists():
            self.product_category_combo.configure(values=sorted(set(tuple(PRODUCT_CATALOG) + tuple(categories)), key=str.casefold))
        if hasattr(self, "inventory_category_combo") and self.inventory_category_combo.winfo_exists():
            self.inventory_category_combo.configure(values=["All categories"] + sorted(set(tuple(PRODUCT_CATALOG) + tuple(categories)), key=str.casefold))
        if hasattr(self, "product_unit_combo") and self.product_unit_combo.winfo_exists():
            self.product_unit_combo.configure(values=sorted(set(("pcs", "kg", "g", "mg", "L", "ml", "m", "cm", "box", "pack", "hour", "day", "service") + tuple(units)), key=str.casefold))

    # ======================================
    # BUTTON DESIGN
    # ======================================

    def make_button(self, parent, text, color, command):

        tk.Button(
            parent,
            text=text,
            bg=color,
            fg=WHITE,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=PADDING["button_x"],
            pady=PADDING["button_y"],
            cursor="hand2",
            command=command
        ).pack(side="left", padx=5)

    # ======================================
    # FORM FUNCTIONS
    # ======================================

    def clear_form(self):

        for var in self.form_vars.values():
            var.set("")

        self.selected_id = None

        if hasattr(self, "table"):
            for item in self.table.selection():
                self.table.selection_remove(item)

    def get_form_data(self):

        name = self.form_vars["name"].get().strip()
        sku = self.form_vars["sku"].get().strip()
        category = self.form_vars["category"].get().strip()

        if not name:
            messagebox.showwarning(
                "Validation", "Enter product name."
            )
            return None

        if not sku:
            messagebox.showwarning(
                "Validation", "Enter SKU or barcode."
            )
            return None

        try:
            price = float(self.form_vars["price"].get() or 0)
            tax_rate = float(self.form_vars["tax_rate"].get() or 0)
            cost = float(self.form_vars["cost"].get() or 0)
            stock = int(self.form_vars["stock"].get() or 0)
            low_stock = int(
                self.form_vars["low_stock"].get() or 5
            )

            if price < 0 or tax_rate < 0 or tax_rate > 100 or cost < 0 or stock < 0 or low_stock < 0:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid Details",
                "Enter valid non-negative numbers for price, cost, stock and low-stock alert."
            )
            return None

        return (
            name, sku, category, price, cost, stock, low_stock,
            self.form_vars["unit"].get().strip() or "pcs", tax_rate,
            self.form_vars.get("brand", tk.StringVar()).get().strip(),
            self.form_vars.get("image_url", tk.StringVar()).get().strip()
        )

    # ======================================
    # ADD PRODUCT
    # ======================================
    def add_product(self):

        data = self.get_form_data()

        if data is None:
            return

        try:
            conn= connect_db()
            cursor = conn.cursor()

            cursor.execute("""
             INSERT INTO products
             (name, sku, category, price, cost, stock, low_stock, unit, tax_rate, brand, image_url)
             VALUES (?,?,?,?,?,?,?,?,?,?,?)
""",data)
            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Success",
                "Products added successfully"
            )

            self.refresh_product_catalog_choices()
            self.clear_form()
            self.refresh_product_table()
            self.refresh_dashboard_if_needed()

        except sqlite3.IntegrityError as e:
                messagebox.showerror(
                    "DataError",
                    f"SKU already exists or database constraint failed.\n\n{e}"
                )
        except Exception as e:
                messagebox.showerror(
                    "Error Adding product",
                    str(e)
                )
            # ======================================
    # SELECT PRODUCT
    # ======================================

    def select_product(self, event=None):

        selected = self.table.selection()

        if not selected:
            return

        product_id = int(self.table.item(selected[0], "values")[0])
        with connect_db() as conn:
            product = conn.execute(
                "SELECT name,sku,category,price,cost,stock,low_stock,unit,tax_rate,brand,image_url FROM products WHERE id=?",
                (product_id,),
            ).fetchone()
        if not product:
            return
        self.selected_id = product_id
        for key, value in zip(("name", "sku", "category", "price", "cost", "stock", "low_stock", "unit", "tax_rate", "brand", "image_url"), product):
            self.form_vars[key].set("" if value is None else str(value))

    # ======================================
    # UPDATE PRODUCT
    # ======================================
    def update_product(self):

        if self.selected_id is None:
            messagebox.showwarning(
                "Select Product",
                "Select a product from the table first."
            )
            return
        if not self.request_page_pin("Products","change product details or stock"):
            return

        data = self.get_form_data()

        if data is None:
            return

        try:
            with connect_db() as conn:

                conn.execute("""
                    UPDATE products
                    SET name=?, sku=?, category=?,
                        price=?, cost=?, stock=?, low_stock=?, unit=?, tax_rate=?, brand=?, image_url=?
                    WHERE id=?
                """, data + (self.selected_id,))

            messagebox.showinfo(
                "Updated", "Product updated successfully."
            )

            self.refresh_product_catalog_choices()
            self.clear_form()
            self.refresh_product_table()
            self.refresh_dashboard_if_needed()

        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Duplicate SKU",
                "Another product already uses this SKU."
            )

    # ======================================
    # DELETE PRODUCT
    # ======================================

    def delete_product(self):

        if self.role != "admin":
            messagebox.showerror("Permission denied", "Only an administrator can delete products.")
            return
        if not self.request_page_pin("Products","delete a product"):
            return

        if self.selected_id is None:
            messagebox.showwarning(
                "Select Product",
                "Select a product to delete."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this product?"
        )

        if not confirm:
            return

        with connect_db() as conn:
            conn.execute(
                "DELETE FROM products WHERE id=?",
                (self.selected_id,)
            )

        messagebox.showinfo(
            "Deleted", "Product deleted successfully."
        )

        self.clear_form()
        self.refresh_product_table()
        self.refresh_dashboard_if_needed()

    # ======================================
    # REFRESH TABLE
    # ======================================
    def refresh_product_table(self):

        if not hasattr(self, "table"):
            return

        for item in self.table.get_children():
            self.table.delete(item)

        with connect_db() as conn:
            sales_rows=conn.execute("SELECT product_id,COALESCE(SUM(quantity),0),COALESCE(SUM(line_total),0) FROM bill_items WHERE product_id IS NOT NULL GROUP BY product_id").fetchall()
        sales_by_product={row[0]:(row[1],row[2]) for row in sales_rows}

        search = self.search_var.get().strip().lower()
        selected_category = getattr(self, "inventory_category_var", tk.StringVar(value="All categories")).get().strip()

        for p in self.get_products():

            if selected_category and selected_category != "All categories" and (p[3] or "Other").casefold() != selected_category.casefold():
                continue

            searchable = " ".join([
                str(p[1]), str(p[2]), str(p[3])
            ]).lower()

            if search and search not in searchable:
                continue

            sold_units,sales_total=sales_by_product.get(p[0],(0,0))
            stock_status="Low stock" if p[6]<=p[7] else "In stock"
            self.table.insert(
                "",
                "end",
                values=(
                    p[0], p[1], p[2], p[3],
                    f"₹{p[4]:,.2f}",
                    f"₹{p[5]:,.2f}",
                    p[6], p[7], sold_units, f"₹{sales_total:,.2f}", stock_status
                ),tags=("low_stock" if stock_status=="Low stock" else "",)
            )

    # ======================================
    # REPORTS
    # ======================================
    def show_reports(self):
        self.clear_content()
        self.show_billing_graphs()
        return

    def show_billing_graphs(self):
        self.render_compact_reports()

    def _show_billing_graphs_legacy(self):
        """Show four medium-sized charts controlled by one shared time range."""
        report_host=self.content
        report_canvas=tk.Canvas(report_host,bg=BG,highlightthickness=0)
        report_scroll=ttk.Scrollbar(report_host,orient="vertical",command=report_canvas.yview)
        report_canvas.configure(yscrollcommand=report_scroll.set)
        report_scroll.pack(side="right",fill="y")
        report_canvas.pack(side="left",fill="both",expand=True)
        report_body=tk.Frame(report_canvas,bg=BG)
        report_window=report_canvas.create_window((0,0),window=report_body,anchor="nw")
        report_body.bind("<Configure>",lambda _event,c=report_canvas:c.configure(scrollregion=c.bbox("all")))
        report_canvas.bind("<Configure>",lambda event,c=report_canvas,w=report_window:c.itemconfigure(w,width=event.width))
        report_canvas.bind("<MouseWheel>",lambda event,c=report_canvas:c.yview_scroll(int(-1*(event.delta/120)),"units"))
        self.content=report_body
        header=tk.Frame(self.content,bg=BG);header.pack(fill="x",pady=(0,5))
        tk.Label(header,text="Billing Overview",bg=BG,fg=DARK,font=("Segoe UI",18,"bold")).pack(side="left")
        tk.Button(header,text="＋ Add expense",bg=GREEN,fg=WHITE,relief="flat",cursor="hand2",command=self.open_expense_manager).pack(side="right",padx=(5,0))
        tk.Button(header,text="Export PDF",bg=BLUE,fg=WHITE,relief="flat",cursor="hand2",command=self.export_reports_pdf).pack(side="right",padx=5)
        tk.Button(header,text="Accounting CSV",bg=PURPLE,fg=WHITE,relief="flat",cursor="hand2",command=self.export_accounting_csv).pack(side="right",padx=5)
        tk.Button(header,text="Export Excel / CSV",bg=DARK,fg=WHITE,relief="flat",cursor="hand2",command=self.export_reports_csv).pack(side="right",padx=5)
        selector_row=tk.Frame(self.content,bg=BG);selector_row.pack(fill="x",pady=(0,5))
        self.summary_period_var=tk.StringVar(value=getattr(self,"selected_report_period","Monthly"))
        self.report_period_var=self.summary_period_var
        tk.Label(selector_row,text="Period",bg=BG,fg=MUTED).pack(side="left",padx=(4,8))
        for period in ("Daily","Weekly","Monthly","Yearly"):
            tk.Radiobutton(selector_row,text=period,value=period,variable=self.summary_period_var,command=lambda p=period:self.set_report_period(p),bg=BG,fg=DARK,selectcolor=WHITE,indicatoron=False,relief="flat",padx=12,pady=5).pack(side="left",padx=3)
        assistant=tk.Frame(self.content,bg=WHITE,highlightbackground=BORDER,highlightthickness=1)
        assistant.pack(fill="x",pady=(0,8))
        tk.Label(assistant,text="AI Business Assistant",bg=WHITE,fg=DARK,font=("Segoe UI",10,"bold")).pack(side="left",padx=(10,5))
        self.report_question_var=tk.StringVar()
        ask_entry=tk.Entry(assistant,textvariable=self.report_question_var,relief="flat",bd=0,font=("Segoe UI",9))
        ask_entry.pack(side="left",fill="x",expand=True,ipady=7,padx=5)
        ask_entry.insert(0,"Ask about sales, profit, products, customers, stock, tax…")
        ask_entry.bind("<FocusIn>",lambda _event,e=ask_entry: e.delete(0,"end") if e.get().startswith("Ask about sales") else None)
        ask_entry.bind("<Return>",lambda _event:self.run_ai_report_query())
        self.ai_report_button=tk.Button(assistant,text="Ask AI",bg=LIGHT_BLUE,fg=DARK,relief="flat",cursor="hand2",command=self.run_ai_report_query)
        self.ai_report_button.pack(side="right",padx=8,pady=4)
        self.report_kpi_labels={}
        kpi_row=tk.Frame(self.content,bg=BG);kpi_row.pack(fill="x",pady=(0,7))
        for key,label,color in (("revenue","Total revenue",BLUE),("collected","Collected",GREEN),("profit","Estimated profit",PURPLE),("outstanding","Outstanding",RED),("expenses","Expenses",WARNING)):
            card=tk.Frame(kpi_row,bg=WHITE,highlightbackground=BORDER,highlightthickness=1)
            card.pack(side="left",fill="both",expand=True,padx=4)
            tk.Label(card,text=label,bg=WHITE,fg=MUTED,font=("Segoe UI",8,"bold")).pack(anchor="w",padx=10,pady=(8,1))
            value_label=tk.Label(card,text="₹0.00",bg=WHITE,fg=color,font=("Segoe UI",13,"bold"))
            value_label.pack(anchor="w",padx=10,pady=(0,8))
            self.report_kpi_labels[key]=value_label
        with connect_db() as conn:
            project_counts=(conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0],
                conn.execute("SELECT COUNT(*) FROM products").fetchone()[0],
                conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0],
                conn.execute("SELECT COUNT(*) FROM bills").fetchone()[0],
                conn.execute("SELECT COUNT(*) FROM business_payments").fetchone()[0]+conn.execute("SELECT COUNT(*) FROM customer_payments").fetchone()[0],
                conn.execute("SELECT COUNT(*) FROM products WHERE COALESCE(is_service,0)=0 AND stock<=low_stock").fetchone()[0])
        snapshot=tk.Frame(self.content,bg=BG);snapshot.pack(fill="x",pady=(0,7))
        for label,value in zip(("Customers","Products","Employees","Bills","Payments","Low stock items"),project_counts):
            tile=tk.Frame(snapshot,bg=WHITE,highlightbackground=BORDER,highlightthickness=1);tile.pack(side="left",fill="both",expand=True,padx=3)
            tk.Label(tile,text=label,bg=WHITE,fg=MUTED,font=("Segoe UI",8,"bold")).pack(anchor="w",padx=9,pady=(6,0))
            tk.Label(tile,text=f"{value:,}",bg=WHITE,fg=RED if label=="Low stock items" and value else BLUE,font=("Segoe UI",13,"bold")).pack(anchor="w",padx=9,pady=(0,6))
        grid=tk.Frame(self.content,bg=BG); grid.pack(fill="x",expand=False)
        panels=(("Bills · trend", "bills", "line"),("Payments · activity", "payments", "dot"),("Customers · billed", "customers", "bar"),("Products · sales mix", "products", "donut"))
        self.summary_chart_widgets={}
        for i,(title,key,kind) in enumerate(panels):
            shadow=tk.Frame(grid,bg="#D7DFEA")
            shadow.grid(row=i//2,column=i%2,sticky="nsew",padx=7,pady=7)
            panel=tk.Frame(shadow,bg=WHITE,highlightbackground=BORDER,highlightthickness=1)
            panel.pack(fill="both",expand=True,padx=(0,4),pady=(0,4))
            head=tk.Frame(panel,bg=WHITE);head.pack(fill="x",padx=12,pady=7)
            tk.Label(head,text=title,bg=WHITE,fg=DARK,font=("Segoe UI",12,"bold")).pack(side="left")
            chart=tk.Canvas(panel,bg=WHITE,height=130,highlightthickness=0)
            chart.pack(fill="both",expand=True,padx=8,pady=5)
            self.summary_chart_widgets[key]=(chart,kind)
        grid.columnconfigure(0,weight=1); grid.columnconfigure(1,weight=1)
        grid.rowconfigure(0,weight=1); grid.rowconfigure(1,weight=1)
        best_panel=tk.Frame(self.content,bg=WHITE,highlightbackground=BORDER,highlightthickness=1)
        best_panel.pack(fill="both",expand=True,pady=(7,0))
        tk.Label(best_panel,text="Best-selling products",bg=WHITE,fg=DARK,font=("Segoe UI",11,"bold")).pack(anchor="w",padx=10,pady=(7,3))
        self.best_sellers_table=ttk.Treeview(best_panel,columns=("product","units","sales","profit"),show="headings",height=3)
        for col,label,width in (("product","PRODUCT",280),("units","UNITS SOLD",100),("sales","SALES",140),("profit","EST. PROFIT",140)):
            self.best_sellers_table.heading(col,text=label);self.best_sellers_table.column(col,width=width,anchor="center")
        self.best_sellers_table.pack(fill="both",expand=True,padx=8,pady=(0,7))
        staff_panel=tk.Frame(self.content,bg=WHITE,highlightbackground=BORDER,highlightthickness=1)
        staff_panel.pack(fill="x",pady=(8,0))
        tk.Label(staff_panel,text="Employee activity · bills and collections",bg=WHITE,fg=DARK,font=("Segoe UI",11,"bold")).pack(anchor="w",padx=10,pady=(7,3))
        self.employee_report_table=ttk.Treeview(staff_panel,columns=("employee","bills","billed","collected"),show="headings",height=4)
        for col,label,width in (("employee","EMPLOYEE",230),("bills","BILLS",100),("billed","BILLED",160),("collected","COLLECTED",160)):
            self.employee_report_table.heading(col,text=label);self.employee_report_table.column(col,width=width,anchor="center")
        self.employee_report_table.pack(fill="x",padx=8,pady=(0,7))
        stock_panel=tk.Frame(self.content,bg=WHITE,highlightbackground=BORDER,highlightthickness=1)
        stock_panel.pack(fill="x",pady=(8,0))
        tk.Label(stock_panel,text="Inventory · low stock watch",bg=WHITE,fg=DARK,font=("Segoe UI",11,"bold")).pack(anchor="w",padx=10,pady=(7,3))
        self.report_low_stock_table=ttk.Treeview(stock_panel,columns=("product","category","stock","threshold"),show="headings",height=4)
        for col,label,width in (("product","PRODUCT",250),("category","CATEGORY",190),("stock","CURRENT STOCK",130),("threshold","REORDER AT",130)):
            self.report_low_stock_table.heading(col,text=label);self.report_low_stock_table.column(col,width=width,anchor="center")
        self.report_low_stock_table.pack(fill="x",padx=8,pady=(0,7))
        with connect_db() as conn:
            low_stock_rows=conn.execute("SELECT name,COALESCE(category,'Other'),stock,low_stock FROM products WHERE COALESCE(is_service,0)=0 AND stock<=low_stock ORDER BY stock ASC,name COLLATE NOCASE LIMIT 100").fetchall()
        for row in low_stock_rows:self.report_low_stock_table.insert("","end",values=row)
        self.refresh_all_summary_charts()
        self.content=report_host

    def render_compact_reports(self):
        """Build a compact live report view from customer, staff, inventory, and payment records."""
        host=self.content
        canvas=tk.Canvas(host,bg=BG,highlightthickness=0)
        scrollbar=ttk.Scrollbar(host,orient="vertical",command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right",fill="y")
        canvas.pack(side="left",fill="both",expand=True)
        body=tk.Frame(canvas,bg=BG)
        window_id=canvas.create_window((0,0),window=body,anchor="nw")
        body.bind("<Configure>",lambda _event,c=canvas:c.configure(scrollregion=c.bbox("all")))
        canvas.bind("<Configure>",lambda event,c=canvas,w=window_id:c.itemconfigure(w,width=event.width))
        canvas.bind("<MouseWheel>",lambda event,c=canvas:c.yview_scroll(int(-1*(event.delta/120)),"units"))
        self.content=body
        header=tk.Frame(body,bg=BG);header.pack(fill="x",pady=(0,5))
        tk.Label(header,text="Business Reports",bg=BG,fg=DARK,font=("Segoe UI",19,"bold")).pack(side="left")
        self.report_chart_order=getattr(self,"report_chart_order",["customers","customer_balances","employees","products","payments"])
        self.summary_period_var=tk.StringVar(value=getattr(self,"selected_report_period","Monthly"))
        self.report_period_var=self.summary_period_var
        periods=tk.Frame(body,bg=BG);periods.pack(fill="x",pady=(0,8))
        tk.Label(periods,text="Period",bg=BG,fg=MUTED,font=("Segoe UI",9,"bold")).pack(side="left",padx=(3,8))
        self.report_period_buttons={}
        for period in ("Daily","Weekly","Monthly","Yearly"):
            btn=tk.Button(periods,text=period,relief="flat",bd=0,cursor="hand2",
                padx=14,pady=7,font=("Segoe UI",9,"bold"),
                command=lambda p=period:self.set_report_period(p))
            btn.pack(side="left",padx=3)
            self.report_period_buttons[period]=btn
        self.refresh_report_period_button_styles()
        self.report_kpi_labels={}
        money_row=tk.Frame(body,bg=BG);money_row.pack(fill="x",pady=(0,5))
        for key,label,color in (("revenue","Billed",BLUE),("collected","Collected",GREEN),("outstanding","Outstanding",RED),("overdue","Overdue",WARNING)):
            tile=tk.Frame(money_row,bg=WHITE,highlightbackground=BORDER,highlightthickness=1);tile.pack(side="left",fill="both",expand=True,padx=3)
            tk.Label(tile,text=label,bg=WHITE,fg=MUTED,font=("Segoe UI",8,"bold")).pack(anchor="w",padx=10,pady=(7,0))
            value=tk.Label(tile,text="₹0.00",bg=WHITE,fg=color,font=("Segoe UI",13,"bold"));value.pack(anchor="w",padx=10,pady=(0,7))
            self.report_kpi_labels[key]=value
        with connect_db() as conn:
            counts={"customers":conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0],
                "employees":conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0],
                "products":conn.execute("SELECT COUNT(*) FROM products").fetchone()[0],
                "low_stock":conn.execute("SELECT COUNT(*) FROM products WHERE COALESCE(is_service,0)=0 AND stock<=low_stock").fetchone()[0],
                "customers_due":conn.execute("""SELECT COUNT(*) FROM (SELECT c.id FROM customers c LEFT JOIN bills b ON b.customer_id=c.id GROUP BY c.id HAVING COALESCE(SUM(b.total),0)-COALESCE(SUM(b.paid),0)-COALESCE((SELECT SUM(p.amount) FROM customer_payments p WHERE p.customer_id=c.id),0)>0)""").fetchone()[0]}
        self.project_kpi_labels={}
        count_row=tk.Frame(body,bg=BG);count_row.pack(fill="x",pady=(0,8))
        for key,label,color in (("customers","Customers",BLUE),("customers_due","Customers with balance",WARNING),("employees","Employees",PURPLE),("products","Products",GREEN),("low_stock","Low stock",RED)):
            tile=tk.Frame(count_row,bg=WHITE,highlightbackground=BORDER,highlightthickness=1);tile.pack(side="left",fill="both",expand=True,padx=3)
            tk.Label(tile,text=label,bg=WHITE,fg=MUTED,font=("Segoe UI",8,"bold")).pack(anchor="w",padx=10,pady=(6,0))
            value=tk.Label(tile,text=str(counts[key]),bg=WHITE,fg=color,font=("Segoe UI",13,"bold"));value.pack(anchor="w",padx=10,pady=(0,6))
            self.project_kpi_labels[key]=value
        chart_grid=tk.Frame(body,bg=BG);chart_grid.pack(fill="x",expand=False)
        chart_specs=(("Customers · sales by customer","customers"),("Customers · outstanding by customer","customer_balances"),("Employees · staff by role","employees"),("Products · products by category","products"),("Payments · collected by mode","payments"))
        self.report_chart_frames={};self.report_chart_move_buttons={};self.summary_chart_widgets={}
        chart_titles=dict(chart_specs)
        for key in self.report_chart_order:
            title=chart_titles.get(key,key.title())
            panel=tk.Frame(chart_grid,bg=WHITE,highlightbackground=BORDER,highlightthickness=1)
            self.report_chart_frames[key]=panel
            head=tk.Frame(panel,bg=WHITE);head.pack(fill="x",padx=10,pady=(8,2))
            tk.Label(head,text=title,bg=WHITE,fg=DARK,font=("Segoe UI",11,"bold")).pack(side="left")
            chart=tk.Canvas(panel,bg=WHITE,height=145,highlightthickness=0)
            chart.pack(fill="both",expand=True,padx=7,pady=(2,7))
            self.summary_chart_widgets[key]=(chart,"bar-money" if key in ("customers","customer_balances","payments") else "bar-count")
        chart_grid.columnconfigure(0,weight=1);chart_grid.columnconfigure(1,weight=1)
        self.apply_report_chart_layout()
        self.refresh_all_summary_charts()
        self.content=host

    def apply_report_chart_layout(self):
        frames=getattr(self,"report_chart_frames",{})
        for index,key in enumerate(getattr(self,"report_chart_order",[])):
            panel=frames.get(key)
            if panel and panel.winfo_exists():
                panel.grid(row=index//2,column=index%2,sticky="nsew",padx=5,pady=5)

    def refresh_report_period_button_styles(self):
        active=getattr(self,"summary_period_var",None)
        selected=active.get() if active else getattr(self,"selected_report_period","Monthly")
        for period,button in getattr(self,"report_period_buttons",{}).items():
            if period==selected:
                button.configure(bg=BLUE,fg=WHITE,activebackground=BLUE,activeforeground=WHITE)
            else:
                button.configure(bg=WHITE,fg=DARK,activebackground=LIGHT_BLUE,activeforeground=DARK)

    def set_report_period(self, period):
        self.selected_report_period=period
        if hasattr(self,"summary_period_var"):
            self.summary_period_var.set(period)
        self.refresh_report_period_button_styles()
        self.refresh_all_summary_charts()

    def refresh_report_kpis(self):
        if not getattr(self,"report_kpi_labels",None):
            return
        period=self.summary_period_var.get()
        modifier={"Daily":"-1 day","Weekly":"-7 days","Monthly":"-1 month","Yearly":"-12 months"}.get(period,"-1 month")
        with connect_db() as conn:
            revenue=conn.execute("SELECT COALESCE(SUM(total),0) FROM bills WHERE bill_date>=datetime('now',?)",(modifier,)).fetchone()[0]
            collected=conn.execute("SELECT COALESCE(SUM(amount),0) FROM (SELECT amount,payment_date FROM business_payments UNION ALL SELECT amount,payment_date FROM customer_payments) WHERE payment_date>=datetime('now',?)",(modifier,)).fetchone()[0]
            profit=conn.execute("SELECT COALESCE(SUM((l.rate-COALESCE(p.cost,0))*l.quantity-l.discount),0) FROM invoice_lines l JOIN bills b ON b.id=l.bill_id LEFT JOIN products p ON p.id=l.product_id WHERE b.bill_date>=datetime('now',?)",(modifier,)).fetchone()[0]
            expenses=conn.execute("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE expense_date>=date('now',?)",(modifier,)).fetchone()[0]
            outstanding=conn.execute("SELECT MAX(0,COALESCE((SELECT SUM(total-paid) FROM bills),0)-COALESCE((SELECT SUM(amount) FROM customer_payments),0))").fetchone()[0]
            overdue=conn.execute("SELECT COALESCE(SUM(total-paid),0) FROM bills WHERE due_date<date('now') AND paid<total AND bill_date>=datetime('now',?)",(modifier,)).fetchone()[0]
        values={"revenue":revenue,"collected":collected,"outstanding":outstanding,"overdue":overdue}
        for key,label in self.report_kpi_labels.items():
            label.configure(text=f"₹{values[key]:,.2f}")

    def refresh_best_sellers(self):
        if not hasattr(self,"best_sellers_table") or not self.best_sellers_table.winfo_exists():
            return
        for item in self.best_sellers_table.get_children():self.best_sellers_table.delete(item)
        modifier={"Daily":"-1 day","Weekly":"-7 days","Monthly":"-1 month","Yearly":"-12 months"}.get(self.summary_period_var.get(),"-1 month")
        with connect_db() as conn:
            rows=conn.execute("SELECT l.description,SUM(l.quantity),SUM(l.line_total),SUM((l.rate-COALESCE(p.cost,0))*l.quantity-l.discount) FROM invoice_lines l JOIN bills b ON b.id=l.bill_id LEFT JOIN products p ON p.id=l.product_id WHERE b.bill_date>=datetime('now',?) GROUP BY l.description ORDER BY SUM(l.quantity) DESC LIMIT 5",(modifier,)).fetchall()
        for row in rows:self.best_sellers_table.insert("","end",values=(row[0],f"{row[1]:g}",f"₹{row[2]:,.2f}",f"₹{row[3]:,.2f}"))

    def refresh_employee_activity_report(self):
        if not hasattr(self,"employee_report_table") or not self.employee_report_table.winfo_exists():return
        self.employee_report_table.delete(*self.employee_report_table.get_children())
        modifier={"Daily":"-1 day","Weekly":"-7 days","Monthly":"-1 month","Yearly":"-12 months"}.get(self.summary_period_var.get(),"-1 month")
        with connect_db() as conn:
            rows=conn.execute("""SELECT e.name,COUNT(b.id),COALESCE(SUM(b.total),0),COALESCE((SELECT SUM(p.amount) FROM business_payments p WHERE p.employee_id=e.id AND p.payment_date>=datetime('now',?)),0)
                FROM employees e LEFT JOIN bills b ON b.employee_id=e.id AND b.bill_date>=datetime('now',?) GROUP BY e.id ORDER BY 3 DESC,e.name LIMIT 100""",(modifier,modifier)).fetchall()
        for row in rows:
            if row[1] or row[2] or row[3]:self.employee_report_table.insert("","end",values=(row[0],row[1],f"₹{row[2]:,.2f}",f"₹{row[3]:,.2f}"))

    def open_expense_manager(self):
        window=tk.Toplevel(self.root)
        window.title("Business expenses")
        window.geometry("790x500")
        window.configure(bg=BG)
        tk.Label(window,text="Business expenses",bg=BG,fg=DARK,font=("Segoe UI",16,"bold")).pack(anchor="w",padx=16,pady=(14,8))
        form=tk.Frame(window,bg=WHITE,highlightbackground=BORDER,highlightthickness=1)
        form.pack(fill="x",padx=14,pady=(0,10))
        date_var=tk.StringVar(value=date.today().isoformat())
        category_var=tk.StringVar(value="General")
        description_var=tk.StringVar()
        amount_var=tk.StringVar()
        for col,(label,var,width) in enumerate((("Date (YYYY-MM-DD)",date_var,13),("Category",category_var,17),("Description",description_var,28),("Amount (₹)",amount_var,13))):
            tk.Label(form,text=label,bg=WHITE,fg=MUTED,font=("Segoe UI",8,"bold")).grid(row=0,column=col,sticky="w",padx=7,pady=(8,3))
            field=ttk.Combobox(form,textvariable=var,values=("General","Rent","Utilities","Payroll","Transport","Supplies","Repairs","Other"),width=width) if col==1 else tk.Entry(form,textvariable=var,width=width,relief="solid",bd=1)
            field.grid(row=1,column=col,sticky="ew",padx=7,pady=(0,9),ipady=5)
            form.columnconfigure(col,weight=1)
        table=ttk.Treeview(window,columns=("date","category","description","amount"),show="headings",height=12)
        for col,label,width in (("date","DATE",130),("category","CATEGORY",150),("description","DESCRIPTION",360),("amount","AMOUNT",130)):
            table.heading(col,text=label);table.column(col,width=width,anchor="center")
        table.pack(fill="both",expand=True,padx=14,pady=5)
        actions=tk.Frame(window,bg=BG);actions.pack(fill="x",padx=14,pady=10)
        tk.Button(actions,text="＋ Add expense",bg=GREEN,fg=WHITE,relief="flat",command=lambda:self.save_expense(date_var,category_var,description_var,amount_var,table)).pack(side="left")
        tk.Button(actions,text="Delete selected",bg=RED,fg=WHITE,relief="flat",command=lambda:self.delete_expense(table)).pack(side="right")
        self.refresh_expense_table(table)

    def refresh_expense_table(self, table):
        for item in table.get_children():table.delete(item)
        with connect_db() as conn:
            rows=conn.execute("SELECT id,expense_date,category,description,amount FROM expenses ORDER BY expense_date DESC,id DESC").fetchall()
        for row in rows:table.insert("","end",iid=str(row[0]),values=(row[1],row[2],row[3],f"₹{row[4]:,.2f}"))

    def save_expense(self, date_var, category_var, description_var, amount_var, table):
        try:
            expense_date=date.fromisoformat(date_var.get().strip()).isoformat()
            amount=float(amount_var.get())
            if amount<=0:raise ValueError
        except ValueError:
            messagebox.showerror("Expense details","Enter a valid date and an amount greater than zero.")
            return
        with connect_db() as conn:
            conn.execute("INSERT INTO expenses(expense_date,category,description,amount) VALUES (?,?,?,?)",(expense_date,category_var.get().strip() or "General",description_var.get().strip(),amount))
        amount_var.set("");description_var.set("")
        self.refresh_expense_table(table)
        self.refresh_report_kpis()

    def delete_expense(self, table):
        selected=table.selection()
        if not selected:return
        if not self.request_security_pin("delete an expense"):
            return
        if not messagebox.askyesno("Delete expense","Remove the selected expense record?"):return
        with connect_db() as conn:conn.execute("DELETE FROM expenses WHERE id=?",(int(selected[0]),))
        self.refresh_expense_table(table)
        self.refresh_report_kpis()

    def refresh_summary_chart(self,key):
        chart,kind=self.summary_chart_widgets[key]
        period=self.summary_period_var.get()
        configs={"Daily":("%Y-%m-%d","-30 days"),"Weekly":("%Y-%W","-84 days"),"Monthly":("%Y-%m","-12 months"),"Yearly":("%Y","-5 years")}
        date_format,modifier=configs.get(period,configs["Monthly"])
        with connect_db() as conn:
            if key=="customers":
                rows=conn.execute("SELECT c.name,SUM(b.total) FROM customers c JOIN bills b ON b.customer_id=c.id WHERE b.bill_date>=datetime('now',?) GROUP BY c.id ORDER BY 2 DESC LIMIT 10",(modifier,)).fetchall()
                if not rows:
                    rows=conn.execute("SELECT name,1 FROM customers ORDER BY created_at DESC,id DESC LIMIT 10").fetchall()
            elif key=="customer_balances":
                rows=conn.execute("""SELECT c.name,MAX(0,COALESCE(SUM(b.total),0)-COALESCE(SUM(b.paid),0)-COALESCE((SELECT SUM(p.amount) FROM customer_payments p WHERE p.customer_id=c.id),0))
                    FROM customers c LEFT JOIN bills b ON b.customer_id=c.id GROUP BY c.id HAVING COALESCE(SUM(b.total),0)-COALESCE(SUM(b.paid),0)-COALESCE((SELECT SUM(p.amount) FROM customer_payments p WHERE p.customer_id=c.id),0)>0 ORDER BY 2 DESC LIMIT 10""").fetchall()
            elif key=="employees":
                rows=conn.execute("SELECT COALESCE(NULLIF(TRIM(role),''),'Staff'),COUNT(*) FROM employees GROUP BY COALESCE(NULLIF(TRIM(role),''),'Staff') ORDER BY 2 DESC LIMIT 10").fetchall()
            elif key=="products":
                rows=conn.execute("SELECT COALESCE(NULLIF(TRIM(category),''),'Uncategorized'),COUNT(*) FROM products GROUP BY COALESCE(NULLIF(TRIM(category),''),'Uncategorized') ORDER BY 2 DESC LIMIT 10").fetchall()
            elif key=="payments":
                rows=conn.execute("SELECT mode,SUM(amount) FROM (SELECT COALESCE(NULLIF(payment_mode,''),'Other') mode,amount,payment_date FROM business_payments UNION ALL SELECT COALESCE(NULLIF(payment_mode,''),'Other'),amount,payment_date FROM customer_payments) WHERE payment_date>=datetime('now',?) GROUP BY mode ORDER BY 2 DESC LIMIT 10",(modifier,)).fetchall()
            else:
                rows=[]
        title={"payments":f"Payments by mode · {period}","customers":f"Top customers · {period}","customer_balances":"Customers with outstanding balances","employees":"Employees by role","products":"Products by category"}[key]
        parent=chart.master
        for widget in parent.winfo_children():
            if isinstance(widget,tk.Label):widget.configure(text=title)
        chart.bind("<Configure>",lambda _e,c=chart,d=rows,k=kind:self.draw_summary_chart(c,d,k))
        self.draw_summary_chart(chart,rows,kind)

    def refresh_all_summary_charts(self):
        for key in self.summary_chart_widgets:
            self.refresh_summary_chart(key)
        self.refresh_report_kpis()
        if hasattr(self,"project_kpi_labels"):
            with connect_db() as conn:
                current={"customers":conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0],"employees":conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0],"products":conn.execute("SELECT COUNT(*) FROM products").fetchone()[0],"low_stock":conn.execute("SELECT COUNT(*) FROM products WHERE COALESCE(is_service,0)=0 AND stock<=low_stock").fetchone()[0],"customers_due":conn.execute("""SELECT COUNT(*) FROM (SELECT c.id FROM customers c LEFT JOIN bills b ON b.customer_id=c.id GROUP BY c.id HAVING COALESCE(SUM(b.total),0)-COALESCE(SUM(b.paid),0)-COALESCE((SELECT SUM(p.amount) FROM customer_payments p WHERE p.customer_id=c.id),0)>0)""").fetchone()[0]}
            for key,label in self.project_kpi_labels.items():label.configure(text=f"{current[key]:,}")

    def draw_summary_chart(self,canvas,rows,kind):
        canvas.delete("all")
        w,h=canvas.winfo_width(),canvas.winfo_height()
        if w<120 or h<100:return
        if not rows:
            canvas.create_text(w/2,h/2,text="No data yet",fill=MUTED);return
        if kind in ("line","dot"):
            vals=[float(r[1] or 0) for r in rows]; high=max(vals+[1]); coords=[]
            for i,(label,value) in enumerate(rows):
                x=24+(w-48)*i/max(1,len(rows)-1); y=h-34-(h-65)*float(value or 0)/high
                coords.extend((x,y)); canvas.create_oval(x-4,y-4,x+4,y+4,fill=GREEN if kind=="dot" else BLUE,outline=GREEN if kind=="dot" else BLUE)
                if len(rows)<8 or i%2==0:canvas.create_text(x,h-15,text=str(label)[5:],fill=MUTED,font=("Segoe UI",8))
            if kind=="line" and len(coords)>=4:canvas.create_line(*coords,fill=BLUE,width=2,smooth=True)
        elif kind=="donut":
            palette=(BLUE,GREEN,PURPLE,WARNING,RED,"#A78BFA")
            total=sum(float(r[1] or 0) for r in rows) or 1
            start=0
            for i,(label,value) in enumerate(rows[:6]):
                extent=360*float(value or 0)/total
                canvas.create_arc(14,12,150,148,start=start,extent=extent,fill=palette[i%len(palette)],outline=WHITE,width=2)
                start+=extent
                canvas.create_text(165,24+i*20,text=str(label)[:20],anchor="w",fill=palette[i%len(palette)],font=("Segoe UI",8))
        else:
            top=sorted(rows,key=lambda r:float(r[1] or 0),reverse=True)[:10]; high=max([float(r[1] or 0) for r in top]+[1]); rh=min(24,(h-20)/len(top))
            palette=(BLUE,GREEN,PURPLE,WARNING,RED,"#A78BFA")
            for i,(label,value) in enumerate(top):
                y=10+i*rh; bw=(w-145)*float(value or 0)/high
                canvas.create_text(128,y+rh/2,text=str(label)[:18],anchor="e",fill=DARK,font=("Segoe UI",8))
                canvas.create_rectangle(135,y+3,135+bw,y+rh-3,fill=palette[i%len(palette)],outline="")
                value_text=f"₹{value:,.0f}" if kind=="bar-money" else f"{value:,.0f}"
                canvas.create_text(140+bw,y+rh/2,text=value_text,anchor="w",fill=MUTED,font=("Segoe UI",8))
        return
        self.report_period_var = getattr(self, "report_period_var", tk.StringVar(value="Yearly"))
        controls = tk.Frame(self.content, bg=BG)
        controls.pack(fill="x", pady=(0, 8))
        ttk.Combobox(controls, textvariable=self.report_period_var, values=("Daily", "Weekly", "Monthly", "Yearly"), state="readonly", width=12).pack(side="left", padx=4)
        tk.Button(controls, text="Refresh", command=self.show_reports).pack(side="left", padx=4)
        tk.Button(controls, text="Export CSV", bg=BLUE, fg=WHITE, relief="flat", command=self.export_reports_csv).pack(side="right", padx=4)
        tk.Button(controls, text="Export PDF", bg=GREEN, fg=WHITE, relief="flat", command=self.export_reports_pdf).pack(side="right", padx=4)
        self.report_question_var = tk.StringVar()
        tk.Entry(controls, textvariable=self.report_question_var, width=36).pack(side="left", padx=(8, 3), ipady=4)
        self.ai_report_button = tk.Button(controls, text="Ask AI", command=self.run_ai_report_query)
        self.ai_report_button.pack(side="left", padx=3)
        period_modifier = {"Daily": "-1 day", "Weekly": "-7 days", "Monthly": "-1 month", "Yearly": "-12 months"}.get(self.report_period_var.get(), "-12 months")
        with connect_db() as conn:
            revenue, bill_payments, bill_count = conn.execute("""
                SELECT COALESCE(SUM(total), 0), COALESCE(SUM(paid), 0), COUNT(*)
                FROM bills WHERE bill_date >= datetime('now', ?)
            """, (period_modifier,)).fetchone()
            account_payments = conn.execute("""
                SELECT COALESCE(SUM(amount), 0) FROM customer_payments
                WHERE payment_date >= datetime('now', ?)
            """, (period_modifier,)).fetchone()[0]
            categories = conn.execute("""
                SELECT COALESCE(p.category, 'Other'), SUM(bi.line_total)
                FROM bill_items bi JOIN bills b ON b.id=bi.bill_id
                LEFT JOIN products p ON p.id=bi.product_id
                WHERE b.bill_date >= datetime('now', ?)
                GROUP BY COALESCE(p.category, 'Other') ORDER BY SUM(bi.line_total) DESC
            """, (period_modifier,)).fetchall()
            top_products = conn.execute("""
                SELECT bi.product_name, SUM(bi.quantity), SUM(bi.line_total),
                       SUM((bi.unit_price - COALESCE(p.cost, 0)) * bi.quantity)
                FROM bill_items bi JOIN bills b ON b.id=bi.bill_id
                LEFT JOIN products p ON p.id=bi.product_id
                WHERE b.bill_date >= datetime('now', ?)
                GROUP BY bi.product_name ORDER BY SUM(bi.line_total) DESC LIMIT 10
            """, (period_modifier,)).fetchall()
            customer_count = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
            outstanding = conn.execute("""
                SELECT COALESCE((SELECT SUM(total-paid) FROM bills), 0) -
                       COALESCE((SELECT SUM(amount) FROM customer_payments), 0)
            """).fetchone()[0]
            period_totals = conn.execute("SELECT COALESCE(SUM(total),0),COALESCE(SUM(paid),0) FROM bills WHERE bill_date >= datetime('now', ?)", (period_modifier,)).fetchone()
            monthly_rows = conn.execute("SELECT strftime('%Y-%m', bill_date) AS month, COALESCE(SUM(total),0), COALESCE(SUM(paid),0) FROM bills WHERE bill_date >= datetime('now','-12 months') GROUP BY month ORDER BY month").fetchall()
            overdue_amount = conn.execute("SELECT COALESCE(SUM(total-paid),0) FROM bills WHERE due_date < date('now') AND paid < total AND bill_date >= datetime('now', ?)", (period_modifier,)).fetchone()[0]
            status_rows = conn.execute("SELECT CASE WHEN paid>=total THEN 'Paid' WHEN due_date<date('now') THEN 'Overdue' WHEN paid>0 THEN 'Partial' ELSE 'Unpaid' END, COUNT(*) FROM bills WHERE bill_date >= datetime('now', ?) GROUP BY 1", (period_modifier,)).fetchall()
            aging_rows = conn.execute("SELECT CASE WHEN julianday('now')-julianday(due_date)<=30 THEN '1–30 days' WHEN julianday('now')-julianday(due_date)<=60 THEN '31–60 days' WHEN julianday('now')-julianday(due_date)<=90 THEN '61–90 days' ELSE '90+ days' END, SUM(total-paid) FROM bills WHERE due_date<date('now') AND paid<total GROUP BY 1", ()).fetchall()
            invoice_rows = conn.execute("""
                SELECT c.name, COALESCE(b.invoice_no,'INV-'||b.id), date(b.bill_date), b.due_date,
                       b.total, b.paid, b.total-b.paid,
                       CASE WHEN b.paid>=b.total THEN 'Paid' WHEN b.due_date<date('now') THEN 'Overdue' WHEN b.paid>0 THEN 'Partial' ELSE 'Unpaid' END,
                       CASE WHEN b.due_date<date('now') AND b.paid<b.total THEN CAST(julianday('now')-julianday(b.due_date) AS INTEGER) ELSE 0 END
                FROM bills b JOIN customers c ON c.id=b.customer_id
                WHERE b.bill_date >= datetime('now', ?) ORDER BY b.due_date
            """, (period_modifier,)).fetchall()

        tk.Label(self.content, text=f"Reports · {self.report_period_var.get()}", bg=BG, fg=DARK,
                 font=("Segoe UI", 17, "bold")).pack(anchor="w", pady=(0, 12))
        tk.Button(controls, text="Export PDF", bg=GREEN, fg=WHITE, relief="flat", command=self.export_reports_pdf).pack(side="right", padx=4)
        cards = tk.Frame(self.content, bg=BG)
        cards.pack(fill="x", pady=(0, 14))
        for label, value, color in (
            ("Total billed", f"₹{period_totals[0]:,.2f}", BLUE),
            ("Amount collected", f"₹{period_totals[1] + account_payments:,.2f}", GREEN),
            ("Outstanding balance", f"₹{max(0, outstanding):,.2f}", RED),
            ("Overdue amount", f"₹{overdue_amount:,.2f}", PURPLE),
        ):
            card = tk.Frame(cards, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
            card.pack(side="left", fill="both", expand=True, padx=5)
            tk.Label(card, text=label, bg=WHITE, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=14, pady=(12, 4))
            tk.Label(card, text=value, bg=WHITE, fg=color, font=("Segoe UI", 17, "bold")).pack(anchor="w", padx=14, pady=(0, 12))

        charts = tk.Frame(self.content, bg=BG)
        charts.pack(fill="x", pady=(0, 10))
        for title, rows, draw in (("Monthly billed vs collected", monthly_rows, self.draw_billing_trend), ("Invoice status mix", status_rows, self.draw_status_chart), ("Overdue aging", aging_rows, self.draw_aging_chart)):
            panel = tk.Frame(charts, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
            panel.pack(side="left", fill="both", expand=True, padx=4)
            tk.Label(panel, text=title, bg=WHITE, fg=DARK, font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=10, pady=8)
            canvas = tk.Canvas(panel, bg=WHITE, height=175, highlightthickness=0)
            canvas.pack(fill="both", expand=True, padx=6, pady=4)
            draw(canvas, rows)
            canvas.bind("<Configure>", lambda _event, c=canvas, data=rows, fn=draw: fn(c, data))

        detail = tk.Frame(self.content, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        detail.pack(fill="both", expand=True, pady=(0, 10))
        tk.Label(detail, text="Invoice follow-up", bg=WHITE, fg=DARK, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=12, pady=8)
        cols = ("customer","invoice","date","due","amount","paid","balance","status","days")
        self.report_invoice_table = ttk.Treeview(detail, columns=cols, show="headings", height=7)
        for col, label in zip(cols, ("Customer","Invoice","Invoice date","Due date","Amount","Paid","Balance","Status","Days overdue")):
            self.report_invoice_table.heading(col, text=label, command=lambda c=col: self.sort_report_invoices(c))
            self.report_invoice_table.column(col, width=112, anchor="center")
        self.report_invoice_table.pack(fill="both", expand=True, padx=8, pady=(0,8))
        self.report_invoice_sort_reverse = False
        self.report_invoice_rows = invoice_rows
        for row in invoice_rows:
            self.report_invoice_table.insert("", "end", values=(row[0],row[1],row[2],row[3],f"₹{row[4]:,.2f}",f"₹{row[5]:,.2f}",f"₹{row[6]:,.2f}",row[7],row[8]))

    def draw_billing_trend(self, canvas, rows):
        w, h = canvas.winfo_width(), canvas.winfo_height()
        canvas.delete("all")
        if w < 100 or h < 70: return
        if not rows:
            canvas.create_text(w/2,h/2,text="No billing data",fill=MUTED); return
        maximum=max(max(row[1],row[2]) for row in rows) or 1
        points=[]
        for series,color in ((1,BLUE),(2,GREEN)):
            coords=[]
            for i,row in enumerate(rows):
                x=24+(w-48)*(i/max(1,len(rows)-1))
                y=h-28-(h-58)*row[series]/maximum
                coords.extend((x,y))
                canvas.create_oval(x-3,y-3,x+3,y+3,fill=color,outline=color)
            if len(coords)>=4: canvas.create_line(*coords,fill=color,width=2,smooth=True)
            points.append((series,color))
        for i,row in enumerate(rows):
            if len(rows)<7 or i%2==0:
                x=24+(w-48)*(i/max(1,len(rows)-1))
                canvas.create_text(x,h-12,text=row[0][5:],fill=MUTED,font=("Segoe UI",7))
        canvas.create_text(12,10,text="Billed",anchor="nw",fill=BLUE,font=("Segoe UI",8))
        canvas.create_text(62,10,text="Collected",anchor="nw",fill=GREEN,font=("Segoe UI",8))

    def draw_status_chart(self, canvas, rows):
        colors={"Paid":GREEN,"Partial":WARNING,"Unpaid":BLUE,"Overdue":RED}
        total=sum(count for _,count in rows) or 1
        start=0
        for label,count in rows:
            extent=360*count/total
            canvas.create_arc(20,20,145,145,start=start,extent=extent,fill=colors.get(label,MUTED),outline=WHITE,width=2)
            start+=extent
        for i,(label,count) in enumerate(rows):
            canvas.create_text(165,35+i*28,text=f"{label}: {count}",anchor="w",fill=colors.get(label,DARK))

    def draw_aging_chart(self, canvas, rows):
        if not rows:
            canvas.create_text(100,70,text="No overdue invoices",fill=GREEN); return
        max_amt=max(amount for _,amount in rows) or 1
        for i,(bucket,amount) in enumerate(rows):
            y=18+i*34
            canvas.create_text(75,y+10,text=bucket,anchor="e",fill=DARK)
            width= max(2,(canvas.winfo_width()-150)*amount/max_amt)
            canvas.create_rectangle(85,y,85+width,y+18,fill=RED,outline="")
            canvas.create_text(90+width,y+9,text=f"₹{amount:,.0f}",anchor="w",fill=MUTED)

    def sort_report_invoices(self, column):
        index={"customer":0,"invoice":1,"date":2,"due":3,"amount":4,"paid":5,"balance":6,"status":7,"days":8}[column]
        rows=sorted(self.report_invoice_rows,key=lambda row: (row[index] is None, row[index]),reverse=self.report_invoice_sort_reverse)
        self.report_invoice_sort_reverse=not self.report_invoice_sort_reverse
        for item in self.report_invoice_table.get_children(): self.report_invoice_table.delete(item)
        for row in rows:
            self.report_invoice_table.insert("","end",values=(row[0],row[1],row[2],row[3],f"₹{row[4]:,.2f}",f"₹{row[5]:,.2f}",f"₹{row[6]:,.2f}",row[7],row[8]))

    def run_ai_report_query(self):
        question = self.report_question_var.get().strip()
        if question.startswith("Ask about sales"):
            question = ""
        if not question:
            messagebox.showwarning("Ask AI", "Enter a report request, such as monthly sales by product.")
            return
        self.ai_report_button.configure(state="disabled", text="Thinking…")
        def worker():
            try:
                request = ai_report_request(question)
                self.root.after(0, lambda: self.apply_ai_report_request(request))
            except Exception as exc:
                error = str(exc)
                self.root.after(0, lambda: self.finish_ai_report_error(error))
        threading.Thread(target=worker, daemon=True).start()

    def apply_ai_report_request(self, request):
        period = request.get("period", "Yearly")
        report = request.get("report", "sales")
        if period not in ("Daily", "Weekly", "Monthly", "Yearly"):
            period = "Yearly"
        if report not in ("sales", "products", "customers", "invoice_status", "stock", "tax", "profit"):
            report = "sales"
        self.selected_report_period=period
        self.show_reports()
        answer=self.answer_ai_report(report,period)
        messagebox.showinfo("AI Business Assistant", answer)

    def answer_ai_report(self, report, period):
        modifier={"Daily":"-1 day","Weekly":"-7 days","Monthly":"-1 month","Yearly":"-12 months"}.get(period,"-12 months")
        with connect_db() as conn:
            if report in ("sales","profit"):
                revenue=conn.execute("SELECT COALESCE(SUM(total),0) FROM bills WHERE bill_date>=datetime('now',?)",(modifier,)).fetchone()[0]
                collected=conn.execute("SELECT COALESCE(SUM(amount),0) FROM (SELECT amount,payment_date FROM business_payments UNION ALL SELECT amount,payment_date FROM customer_payments) WHERE payment_date>=datetime('now',?)",(modifier,)).fetchone()[0]
                expenses=conn.execute("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE expense_date>=date('now',?)",(modifier,)).fetchone()[0]
                gross=conn.execute("SELECT COALESCE(SUM((l.rate-COALESCE(p.cost,0))*l.quantity-l.discount),0) FROM invoice_lines l JOIN bills b ON b.id=l.bill_id LEFT JOIN products p ON p.id=l.product_id WHERE b.bill_date>=datetime('now',?)",(modifier,)).fetchone()[0]
                open_balance=conn.execute("SELECT MAX(0,COALESCE((SELECT SUM(total-paid) FROM bills),0)-COALESCE((SELECT SUM(amount) FROM customer_payments),0))").fetchone()[0]
                return f"{period} business summary (from saved BillEase records):\nRevenue billed: ₹{revenue:,.2f}\nPayments received: ₹{collected:,.2f}\nEstimated profit after recorded expenses: ₹{gross-expenses:,.2f}\nRecorded expenses: ₹{expenses:,.2f}\nCurrent outstanding: ₹{open_balance:,.2f}."
            if report=="products":
                rows=conn.execute("SELECT l.description,SUM(l.quantity),SUM(l.line_total) FROM invoice_lines l JOIN bills b ON b.id=l.bill_id WHERE b.bill_date>=datetime('now',?) GROUP BY l.description ORDER BY SUM(l.quantity) DESC LIMIT 5",(modifier,)).fetchall()
                return f"Top products by units sold · {period}:\n"+("\n".join(f"{name}: {qty:g} units · ₹{sales:,.2f}" for name,qty,sales in rows) if rows else "No product sales were recorded in this period.")
            if report=="customers":
                rows=conn.execute("SELECT c.name,SUM(b.total) FROM customers c JOIN bills b ON b.customer_id=c.id WHERE b.bill_date>=datetime('now',?) GROUP BY c.id ORDER BY SUM(b.total) DESC LIMIT 5",(modifier,)).fetchall()
                return f"Top customers by billed amount · {period}:\n"+("\n".join(f"{name}: ₹{amount:,.2f}" for name,amount in rows) if rows else "No customer billing was recorded in this period.")
            if report=="invoice_status":
                rows=conn.execute("SELECT CASE WHEN paid>=total THEN 'Paid' WHEN due_date<date('now') THEN 'Overdue' WHEN paid>0 THEN 'Partially paid' ELSE 'Unpaid' END,COUNT(*) FROM bills WHERE bill_date>=datetime('now',?) GROUP BY 1",(modifier,)).fetchall()
                return f"Invoice status · {period}:\n"+("\n".join(f"{status}: {count}" for status,count in rows) if rows else "No invoices were recorded in this period.")
            if report=="tax":
                amount=conn.execute("SELECT COALESCE(SUM(tax_total),0) FROM bills WHERE bill_date>=datetime('now',?)",(modifier,)).fetchone()[0]
                return f"Tax recorded on invoices · {period}: ₹{amount:,.2f}. This is a summary of saved invoice tax values, not a tax filing calculation."
            rows=conn.execute("SELECT name,stock,low_stock FROM products WHERE stock<=low_stock ORDER BY stock,name LIMIT 10").fetchall()
            return "Low-stock products:\n"+("\n".join(f"{name}: {stock} in stock (alert at {threshold})" for name,stock,threshold in rows) if rows else "No products are currently below their low-stock thresholds.")

    def finish_ai_report_error(self, error):
        self.ai_report_button.configure(state="normal", text="Ask AI")
        messagebox.showerror("AI report", error)

    def export_reports_csv(self):
        if not self.request_security_pin("export business reports"):
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=(("CSV spreadsheet", "*.csv"),))
        if not path:
            return
        with connect_db() as conn, open(path, "w", newline="", encoding="utf-8-sig") as output:
            writer = csv.writer(output)
            writer.writerow(("Invoice", "Date", "Customer", "Status", "Subtotal", "Discount", "Tax", "Total", "Paid", "Balance"))
            for row in conn.execute("SELECT COALESCE(b.invoice_no,'INV-'||b.id), b.bill_date, c.name, CASE WHEN b.paid>=b.total THEN 'paid' WHEN b.due_date<date('now') THEN 'overdue' WHEN b.paid>0 THEN 'partial' ELSE 'unpaid' END, b.subtotal,b.discount,b.tax_total,b.total,b.paid,b.total-b.paid FROM bills b JOIN customers c ON c.id=b.customer_id ORDER BY b.id DESC"):
                writer.writerow(row)
            writer.writerow(())
            writer.writerow(("PRODUCT SALES", "Units", "Sales", "Estimated profit"))
            for row in conn.execute("SELECT i.product_name,SUM(i.quantity),SUM(i.line_total),SUM((i.unit_price-COALESCE(p.cost,0))*i.quantity) FROM bill_items i LEFT JOIN products p ON p.id=i.product_id GROUP BY i.product_name ORDER BY SUM(i.line_total) DESC"):
                writer.writerow(row)
            writer.writerow(())
            writer.writerow(("CUSTOMER SALES", "Phone", "Invoice count", "Sales", "Outstanding"))
            for row in conn.execute("SELECT c.name,c.phone,COUNT(b.id),COALESCE(SUM(b.total),0),COALESCE(SUM(b.total-b.paid),0) FROM customers c LEFT JOIN bills b ON b.customer_id=c.id GROUP BY c.id ORDER BY SUM(b.total) DESC"):
                writer.writerow(row)
            writer.writerow(())
            writer.writerow(("STOCK", "SKU", "Category", "Quantity", "Low stock alert", "Unit value"))
            for row in conn.execute("SELECT name,sku,category,stock,low_stock,price,CASE WHEN stock<=low_stock THEN 'LOW STOCK' ELSE 'OK' END FROM products ORDER BY name"):
                writer.writerow(row)
            writer.writerow(())
            writer.writerow(("TAX SUMMARY", "Tax rate %", "Tax collected"))
            for row in conn.execute("SELECT tax_rate,SUM(tax_amount) FROM invoice_lines GROUP BY tax_rate ORDER BY tax_rate"):
                writer.writerow(row)
            writer.writerow(())
            writer.writerow(("EXPENSES", "Date", "Category", "Description", "Amount"))
            for row in conn.execute("SELECT expense_date,category,description,amount FROM expenses ORDER BY expense_date DESC"):
                writer.writerow(row)
        messagebox.showinfo("Export complete", f"Report exported to:\n{path}")

    def export_accounting_csv(self):
        if not self.request_security_pin("export accounting records"):
            return
        path=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=(("Accounting CSV","*.csv"),),initialfile=f"billease-accounting-{date.today().isoformat()}.csv")
        if not path:return
        with connect_db() as conn,open(path,"w",newline="",encoding="utf-8-sig") as output:
            writer=csv.writer(output)
            writer.writerow(("Date","Record type","Reference","Contact","Description","Subtotal / Amount","Discount","Tax","Invoice total","Paid / Debit","Balance / Credit"))
            for row in conn.execute("SELECT b.bill_date,'Invoice',COALESCE(b.invoice_no,'INV-'||b.id),c.name,'Sales invoice',b.subtotal,b.discount,b.tax_total,b.total,b.paid,b.total-b.paid FROM bills b JOIN customers c ON c.id=b.customer_id ORDER BY b.bill_date,b.id"):
                writer.writerow(row)
            for row in conn.execute("SELECT b.bill_date,'Invoice line',COALESCE(b.invoice_no,'INV-'||b.id),c.name,l.description,l.quantity*l.rate,l.discount,l.tax_amount,l.line_total,0,0 FROM invoice_lines l JOIN bills b ON b.id=l.bill_id JOIN customers c ON c.id=b.customer_id ORDER BY b.bill_date,l.id"):
                writer.writerow(row)
            for row in conn.execute("SELECT p.payment_date,'Invoice payment',COALESCE(b.invoice_no,'INV-'||b.id),c.name,p.payment_mode,p.amount,0,0,p.amount,p.amount,0 FROM business_payments p JOIN bills b ON b.id=p.bill_id JOIN customers c ON c.id=p.customer_id ORDER BY p.payment_date,p.id"):
                writer.writerow(row)
            for row in conn.execute("SELECT p.payment_date,'Customer credit',p.payment_mode,c.name,COALESCE(p.note,''),p.amount,0,0,p.amount,p.amount,0 FROM customer_payments p JOIN customers c ON c.id=p.customer_id ORDER BY p.payment_date,p.id"):
                writer.writerow(row)
            for row in conn.execute("SELECT expense_date,'Expense',category,description,category,amount,0,0,amount,amount,0 FROM expenses ORDER BY expense_date,id"):
                writer.writerow(row)
        messagebox.showinfo("Accounting export",f"Accounting CSV saved to:\n{path}\nImport or map the columns in your accounting software.")

    def export_reports_pdf(self):
        if not self.request_security_pin("export business reports"):
            return
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=(("PDF report", "*.pdf"),))
        if not path:
            return
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
        except ImportError:
            messagebox.showerror("PDF support needed", "Install PDF support with: pip install reportlab")
            return
        with connect_db() as conn:
            sales = conn.execute("SELECT COALESCE(SUM(total),0),COALESCE(SUM(paid),0),COUNT(*) FROM bills").fetchone()
            products = conn.execute("SELECT i.product_name,SUM(i.quantity),SUM(i.line_total),SUM((i.unit_price-COALESCE(p.cost,0))*i.quantity) FROM bill_items i LEFT JOIN products p ON p.id=i.product_id GROUP BY i.product_name ORDER BY SUM(i.line_total) DESC LIMIT 30").fetchall()
            statuses = conn.execute("SELECT CASE WHEN paid>=total THEN 'Paid' WHEN due_date<date('now') THEN 'Overdue' WHEN paid>0 THEN 'Partially paid' ELSE 'Unpaid' END,COUNT(*),COALESCE(SUM(total-paid),0) FROM bills GROUP BY 1").fetchall()
            stock = conn.execute("SELECT name,stock,low_stock,price FROM products ORDER BY stock<=low_stock DESC, name LIMIT 40").fetchall()
            taxes = conn.execute("SELECT tax_rate,SUM(tax_amount) FROM invoice_lines GROUP BY tax_rate ORDER BY tax_rate").fetchall()
            expenses = conn.execute("SELECT expense_date,category,description,amount FROM expenses ORDER BY expense_date DESC LIMIT 40").fetchall()
        pdf = canvas.Canvas(path, pagesize=A4)
        width, height = A4
        y = height - 45
        pdf.setFont("Helvetica-Bold", 16); pdf.drawString(40,y,f"BillEase {self.report_period_var.get()} Report"); y-=28
        pdf.setFont("Helvetica", 10); pdf.drawString(40,y,f"Sales: INR {sales[0]:,.2f}    Received: INR {sales[1]:,.2f}    Invoices: {sales[2]}"); y-=25
        sections = (("Invoice Status", statuses), ("Product Sales / Profit", products), ("Stock / Low Stock", stock), ("Tax Summary", taxes), ("Expenses", expenses))
        for title, rows in sections:
            if y < 100:
                pdf.showPage(); y=height-45
            pdf.setFont("Helvetica-Bold", 12); pdf.drawString(40,y,title); y-=18
            pdf.setFont("Helvetica", 8)
            for row in rows:
                line = " | ".join(str(value) for value in row)
                pdf.drawString(45,y,line[:125]); y-=13
                if y < 45:
                    pdf.showPage(); y=height-45; pdf.setFont("Helvetica",8)
            y-=12
        pdf.save()
        messagebox.showinfo("Export complete", f"PDF report saved to:\n{path}")

    def draw_report_categories(self, canvas, rows):
        canvas.delete("all")
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width < 180 or height < 100:
            return
        if not rows:
            canvas.create_text(width / 2, height / 2, text="No bill sales in the last 12 months", fill=MUTED)
            return
        max_sales = max(float(sales) for _, sales in rows) or 1
        colors = [BLUE, GREEN, PURPLE, WARNING, RED, "#A78BFA"]
        row_height = min(42, (height - 20) / len(rows))
        for index, (category, sales) in enumerate(rows):
            y = 12 + index * row_height
            canvas.create_text(105, y + 12, text=str(category)[:16], anchor="e", fill=DARK, font=("Segoe UI", 9))
            bar = max(2, (width - 175) * float(sales) / max_sales)
            canvas.create_rectangle(115, y + 3, 115 + bar, y + 23, fill=colors[index % len(colors)], outline="")
            canvas.create_text(123 + bar, y + 13, text=f"₹{sales:,.0f}", anchor="w", fill=MUTED, font=("Segoe UI", 9))

    def show_business_setup(self):
        if self.role != "admin":
            messagebox.showerror("Permission denied", "Only an administrator can change business settings or restore data.")
            return
        self.clear_content()
        self.setting_vars = {}
        self.setting_texts = {}
        with connect_db() as conn:
            settings = dict(conn.execute("SELECT key, value FROM app_settings"))

        profile_header=tk.Frame(self.content,bg=WHITE,highlightbackground=BORDER,highlightthickness=1)
        profile_header.pack(fill="x",pady=(0,12))
        title_area=tk.Frame(profile_header,bg=WHITE)
        title_area.pack(side="left",fill="x",expand=True,padx=17,pady=13)
        tk.Label(title_area,text="⚙  Business Profile",bg=WHITE,fg=DARK,font=("Segoe UI",20,"bold")).pack(anchor="w")
        tk.Label(title_area,text="Manage your company identity, invoice appearance, and customer-facing details.",
                 bg=WHITE,fg=MUTED,font=("Segoe UI",9)).pack(anchor="w",pady=(3,0))
        save_head=tk.Frame(profile_header,bg=WHITE)
        save_head.pack(side="right",padx=16)
        tk.Label(save_head,text="Saved locally",bg=LIGHT_BLUE,fg=BLUE,font=("Segoe UI",8,"bold"),padx=9,pady=4).pack(side="top",anchor="e",pady=(0,5))
        tk.Button(save_head,text="Save profile",bg=BLUE,fg=WHITE,relief="flat",padx=16,pady=8,
                  font=("Segoe UI",9,"bold"),cursor="hand2",command=self.save_business_settings).pack(side="top",anchor="e")

        panels = tk.Frame(self.content, bg=BG)
        panels.pack(fill="x")
        profile = tk.Frame(panels, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        profile.pack(side="left", fill="both", expand=True, padx=(0, 6))
        invoice = tk.Frame(panels, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        invoice.pack(side="left", fill="both", expand=True, padx=(6, 0))
        tk.Label(profile, text="◉  Company identity", bg=WHITE, fg=DARK, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16, pady=(13, 2))
        tk.Label(profile, text="Details shown on your invoices and receipts", bg=WHITE, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w", padx=16, pady=(0, 7))
        tk.Label(invoice, text="▧  Invoice branding and terms", bg=WHITE, fg=DARK, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16, pady=(13, 2))
        tk.Label(invoice, text="Set the visual style, payment information, and customer terms", bg=WHITE, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w", padx=16, pady=(0, 7))

        def add_entry(parent, key, label):
            row = tk.Frame(parent, bg=WHITE)
            row.pack(fill="x", padx=15, pady=4)
            tk.Label(row, text=label, bg=WHITE, fg=MUTED, width=19, anchor="w",
                     font=("Segoe UI", 9, "bold")).pack(side="left")
            default_value = "30" if key == "invoice_due_days" else ""
            value = tk.StringVar(value=settings.get(key, default_value))
            self.setting_vars[key] = value
            entry = tk.Entry(row, textvariable=value, relief="solid", bd=1, font=("Segoe UI", 9))
            entry.pack(side="left", fill="x", expand=True, ipady=5)
            return row

        for key, label in (("business_name", "Business name"), ("business_phone", "Phone"),
                           ("business_email", "Email"), ("business_website", "Website"),
                           ("business_tax_id", "GSTIN / tax ID"), ("invoice_prefix", "Invoice prefix"),
                           ("business_upi_id", "UPI ID (optional)")):
            add_entry(profile, key, label)
        add_entry(profile, "business_address", "Business address")
        logo_row = add_entry(profile, "business_logo", "Logo file")
        tk.Button(logo_row, text="Browse", bg=LIGHT_BLUE, fg=DARK, relief="flat", cursor="hand2",
                  command=self.choose_business_logo).pack(side="left", padx=(6, 0))
        signature_row = add_entry(profile, "business_signature", "Signature image")
        tk.Button(signature_row, text="Browse", bg=LIGHT_BLUE, fg=DARK, relief="flat", cursor="hand2",
                  command=self.choose_business_signature).pack(side="left", padx=(6, 0))

        accent_row = tk.Frame(invoice, bg=WHITE)
        accent_row.pack(fill="x", padx=15, pady=4)
        tk.Label(accent_row, text="Invoice color", bg=WHITE, fg=MUTED, width=19, anchor="w",
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        self.setting_vars["template_primary"] = tk.StringVar(value=settings.get("template_primary", BLUE))
        self.business_accent_swatch = tk.Label(accent_row, textvariable=self.setting_vars["template_primary"],
                bg=WHITE, fg=BLUE, font=("Segoe UI", 9, "bold"))
        self.business_accent_swatch.pack(side="left", padx=5)
        tk.Button(accent_row, text="Choose color", bg=LIGHT_BLUE, fg=DARK, relief="flat", cursor="hand2",
                  command=self.choose_business_accent).pack(side="left", padx=5)
        add_entry(invoice, "business_payment_details", "Payment details")
        add_entry(invoice, "invoice_due_days", "Default due days")

        def add_text(parent, key, label, height):
            tk.Label(parent, text=label, bg=WHITE, fg=MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=17, pady=(7, 3))
            text_box = tk.Text(parent, height=height, wrap="word", relief="solid", bd=1,
                               font=("Segoe UI", 9), padx=7, pady=5)
            text_box.pack(fill="x", padx=15, pady=(0, 5))
            text_box.insert("1.0", settings.get(key, ""))
            self.setting_texts[key] = text_box

        add_text(invoice, "template_footer", "Invoice footer note", 2)
        add_text(invoice, "template_terms", "Terms and conditions", 4)

        tk.Label(invoice,text="These saved details are included when you create or download an invoice.",
                 bg=WHITE,fg=GREEN,font=("Segoe UI",8,"bold")).pack(anchor="w",padx=16,pady=(2,12))

        security = tk.Frame(self.content, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        security.pack(fill="x", pady=(12, 7))
        security_head = tk.Frame(security, bg=WHITE)
        security_head.pack(fill="x", padx=15, pady=(11, 4))
        tk.Label(security_head, text="Security and data safety", bg=WHITE, fg=DARK,
                 font=("Segoe UI", 12, "bold")).pack(side="left")
        with connect_db() as conn:
            pin_enabled = conn.execute("SELECT 1 FROM app_settings WHERE key='security_pin_hash'").fetchone() is not None
        self.security_status_label = tk.Label(security_head,
                text="PIN protection on" if pin_enabled else "PIN protection off",
                bg=WHITE, fg=GREEN if pin_enabled else MUTED, font=("Segoe UI", 9, "bold"))
        self.security_status_label.pack(side="right")
        tk.Label(security, text="PIN protection is required for Products and Business Setup, employee edits, audit records, backups, report exports, payment verification, and sensitive delete actions. No login screen is added.",
                 bg=WHITE, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=15, pady=(0, 6))
        security_actions = tk.Frame(security, bg=WHITE)
        security_actions.pack(fill="x", padx=10, pady=(0, 10))
        tk.Button(security_actions, text="Set / change PIN", bg=DARK, fg=WHITE, relief="flat", cursor="hand2",
                  command=self.set_security_pin).pack(side="left", padx=5)
        tk.Button(security_actions, text="Remove PIN", bg=LIGHT_BLUE, fg=DARK, relief="flat", cursor="hand2",
                  command=self.remove_security_pin).pack(side="left", padx=5)
        backup_options = tk.Frame(security, bg=WHITE)
        backup_options.pack(fill="x", padx=15, pady=(0, 10))
        self.auto_backup_var = tk.BooleanVar(value=settings.get("auto_backup_enabled", "1") == "1")
        tk.Checkbutton(backup_options, text="Create one automatic database backup each day while BillEase is running",
                variable=self.auto_backup_var, bg=WHITE, fg=DARK, activebackground=WHITE,
                selectcolor=WHITE, font=("Segoe UI", 9)).pack(side="left")
        self.backup_directory_var = tk.StringVar(value=settings.get("backup_directory", ""))
        tk.Entry(backup_options, textvariable=self.backup_directory_var, relief="solid", bd=1,
                 font=("Segoe UI", 9)).pack(side="left", fill="x", expand=True, padx=(8, 4), ipady=4)
        tk.Button(backup_options, text="Folder…", bg=LIGHT_BLUE, fg=DARK, relief="flat", cursor="hand2",
                  command=self.choose_backup_directory).pack(side="left")
        cloud_options=tk.Frame(security,bg=WHITE)
        cloud_options.pack(fill="x",padx=15,pady=(0,8))
        self.cloud_backup_var=tk.BooleanVar(value=settings.get("cloud_backup_enabled","0")=="1")
        tk.Checkbutton(cloud_options,text="Upload daily backups to Dropbox",variable=self.cloud_backup_var,
                       bg=WHITE,fg=DARK,activebackground=WHITE,selectcolor=WHITE,font=("Segoe UI",9,"bold")).pack(side="left")
        self.dropbox_backup_path_var=tk.StringVar(value=settings.get("dropbox_backup_path","/BillEaseBackups"))
        tk.Label(cloud_options,text="Dropbox folder",bg=WHITE,fg=MUTED,font=("Segoe UI",8,"bold")).pack(side="left",padx=(12,5))
        tk.Entry(cloud_options,textvariable=self.dropbox_backup_path_var,relief="solid",bd=1,font=("Segoe UI",9),width=27).pack(side="left",ipady=4)
        tk.Button(cloud_options,text="Back Up to Dropbox",bg=GREEN,fg=WHITE,relief="flat",cursor="hand2",
                  command=self.backup_to_dropbox_now).pack(side="right",padx=(6,0))
        self.cloud_backup_status=tk.Label(security,text=settings.get("cloud_backup_last_result","Cloud backup has not run yet."),
                 bg=WHITE,fg=MUTED,font=("Segoe UI",8),anchor="w",wraplength=900,justify="left")
        self.cloud_backup_status.pack(anchor="w",padx=15,pady=(0,3))
        tk.Label(security,text="Dropbox token is read from BILLEASE_DROPBOX_TOKEN and is never saved in the local database. Local SQLite backups continue to work without internet.",
                 bg=WHITE,fg=MUTED,font=("Segoe UI",8),wraplength=900,justify="left").pack(anchor="w",padx=15,pady=(0,9))

        actions = tk.Frame(self.content, bg=BG)
        actions.pack(fill="x", pady=7)
        tk.Button(actions, text="Save Business Settings", bg=BLUE, fg=WHITE, relief="flat", padx=14, pady=9, command=self.save_business_settings).pack(side="left", padx=5)
        tk.Button(actions, text="Back Up Database", bg=GREEN, fg=WHITE, relief="flat", padx=14, pady=9, command=self.backup_database).pack(side="left", padx=5)
        tk.Button(actions, text="Restore Backup", bg=RED, fg=WHITE, relief="flat", padx=14, pady=9, command=self.restore_database).pack(side="left", padx=5)
        tk.Button(actions, text="Audit History", bg=DARK, fg=WHITE, relief="flat", padx=14, pady=9, command=self.show_audit_history).pack(side="left", padx=5)
        portal = tk.Frame(self.content,bg=WHITE,highlightbackground=BORDER,highlightthickness=1)
        portal.pack(fill="x",pady=10)
        tk.Label(portal,text="↗  Customer self-service link",bg=WHITE,fg=DARK,font=("Segoe UI",12,"bold")).pack(anchor="w",padx=15,pady=8)
        self.portal_url_var=tk.StringVar(value="Start the customer form to create a link on this Wi-Fi network.")
        tk.Label(portal,textvariable=self.portal_url_var,bg=WHITE,fg=BLUE,anchor="w").pack(fill="x",padx=15)
        actions2=tk.Frame(portal,bg=WHITE);actions2.pack(anchor="w",padx=10,pady=8)
        tk.Button(actions2,text="Start customer form",bg=BLUE,fg=WHITE,relief="flat",command=self.start_customer_portal).pack(side="left",padx=5)
        tk.Button(actions2,text="Create public link",bg=GREEN,fg=WHITE,relief="flat",command=self.start_public_customer_link).pack(side="left",padx=5)
        tk.Button(actions2,text="Copy link",command=self.copy_customer_portal_link).pack(side="left",padx=5)
        with connect_db() as conn:
            product_count=conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
            customer_count=conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
            employee_count=conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
            invoice_count=conn.execute("SELECT COUNT(*) FROM bills").fetchone()[0]
        db_card=tk.Frame(self.content,bg=WHITE,highlightbackground=BORDER,highlightthickness=1)
        db_card.pack(fill="x",pady=(2,8))
        tk.Label(db_card,text="Local SQLite database",bg=WHITE,fg=DARK,font=("Segoe UI",10,"bold")).pack(anchor="w",padx=14,pady=(9,2))
        tk.Label(db_card,text=f"{product_count:,} products  ·  {customer_count:,} customers  ·  {employee_count:,} employees  ·  {invoice_count:,} invoices\nRecords save automatically on this computer. Stored at: {os.path.abspath(DB_NAME)}",
                 bg=WHITE,fg=MUTED,font=("Segoe UI",8),anchor="w",justify="left",wraplength=1050).pack(anchor="w",padx=14,pady=(0,9))

    def show_customer_form_page(self):
        """Dedicated, visible customer form-link page in the sidebar."""
        self.clear_content()
        if not hasattr(self, "portal_url_var"):
            self.portal_url_var = tk.StringVar(value="Customer form is not started yet. Click Start Customer Form.")
        card=tk.Frame(self.content,bg=WHITE,highlightbackground=BORDER,highlightthickness=1)
        card.pack(fill="x",pady=12)
        tk.Label(card,text="↗  Customer Form Link",bg=WHITE,fg=DARK,font=("Segoe UI",18,"bold")).pack(anchor="w",padx=22,pady=(22,6))
        tk.Label(card,text="Start a form, then share the link with customers so they can submit their name, phone, email, address, photo, and payment receipt.",bg=WHITE,fg=MUTED,font=("Segoe UI",10),wraplength=850,justify="left").pack(anchor="w",padx=22,pady=(0,18))
        linkbox=tk.Frame(card,bg=LIGHT_BLUE)
        linkbox.pack(fill="x",padx=22,pady=(0,16))
        tk.Label(linkbox,textvariable=self.portal_url_var,bg=LIGHT_BLUE,fg=BLUE,font=("Segoe UI",10),wraplength=850,justify="left",anchor="w").pack(fill="x",padx=14,pady=12)
        controls=tk.Frame(card,bg=WHITE)
        controls.pack(anchor="w",padx=16,pady=(0,18))
        tk.Button(controls,text="Start Customer Form (Wi-Fi)",bg=BLUE,fg=WHITE,relief="flat",padx=14,pady=9,command=self.start_customer_portal).pack(side="left",padx=5)
        tk.Button(controls,text="Create Public Link",bg=GREEN,fg=WHITE,relief="flat",padx=14,pady=9,command=self.start_public_customer_link).pack(side="left",padx=5)
        tk.Button(controls,text="Copy Link",bg=LIGHT_BLUE,fg=DARK,relief="flat",padx=14,pady=9,command=self.copy_customer_portal_link).pack(side="left",padx=5)
        tk.Label(card,text="Wi-Fi link works only on the same local network. Public link requires cloudflared and stays active only while BillEase AI and the tunnel are running.",bg=WHITE,fg=MUTED,font=("Segoe UI",9),wraplength=850,justify="left").pack(anchor="w",padx=22,pady=(0,20))

    @staticmethod
    def _portal_upload_signature_ok(data, mime_type):
        """Validate common file signatures instead of trusting browser MIME headers."""
        if mime_type == "image/jpeg": return data.startswith(b"\xff\xd8\xff")
        if mime_type == "image/png": return data.startswith(b"\x89PNG\r\n\x1a\n")
        if mime_type == "image/webp": return len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP"
        if mime_type == "application/pdf": return data.startswith(b"%PDF-")
        return False



    def start_customer_portal(self):
        if getattr(self,"portal_server",None):
            current_url=getattr(self,"portal_url_var",None)
            url=current_url.get() if current_url else ""
            if url:
                messagebox.showinfo("Customer Wi-Fi link",f"Customer form is already running:\n{url}\n\nShare this link with phones on the same Wi-Fi.")
            return
        app=self
        self.portal_token=secrets.token_urlsafe(32)
        self.portal_rate_limits={}
        class PortalHandler(BaseHTTPRequestHandler):
            def log_message(self,*_args): pass
            def setup(self):
                super().setup()
                self.connection.settimeout(12)
            def send_page(self,body,status=200):
                data=body.encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type","text/html; charset=utf-8")
                self.send_header("Content-Length",str(len(data)))
                self.send_header("X-Content-Type-Options","nosniff")
                self.send_header("X-Frame-Options","DENY")
                self.send_header("Referrer-Policy","no-referrer")
                self.send_header("Cache-Control","no-store")
                self.send_header("Content-Security-Policy","default-src 'self' 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'")
                self.end_headers()
                try:self.wfile.write(data)
                except (BrokenPipeError,ConnectionResetError):pass
            def authorized(self):
                query=parse_qs(urlsplit(self.path).query)
                return bool(query.get("token") and hmac.compare_digest(query.get("token",[""])[0],app.portal_token))
            def rate_limited(self):
                ip=self.client_address[0]
                now=time.time();bucket=app.portal_rate_limits.get(ip,[])
                bucket=[t for t in bucket if now-t<60]
                if len(bucket)>=20:
                    app.portal_rate_limits[ip]=bucket
                    return True
                bucket.append(now);app.portal_rate_limits[ip]=bucket
                return False
            def do_GET(self):
                if not self.authorized():
                    self.send_page("<h2>Invalid or expired form link. Ask the shop for a new link.</h2>",403);return
                if self.rate_limited():
                    self.send_page("<h2>Too many requests. Try again in a minute.</h2>",429);return
                with connect_db() as conn:
                    staff_names=[row[0] for row in conn.execute("SELECT name FROM employees WHERE COALESCE(phone,'') NOT LIKE 'DEMO-EMP-%' ORDER BY name").fetchall()]
                staff_options="<option value=\"\">-- Select employee --</option>"+"".join(f"<option value=\"{html.escape(staff, quote=True)}\">{html.escape(staff)}</option>" for staff in staff_names)
                page=f'''<!doctype html><html><meta name="viewport" content="width=device-width,initial-scale=1"><title>Customer Information Form</title><style>body{font:16px Arial;background:#f4f7fc;margin:0;padding:20px;color:#18243a}.box{max-width:620px;margin:20px auto;background:white;padding:22px;border-radius:14px;box-shadow:0 5px 20px #ccd3df}input,textarea,select,button{box-sizing:border-box;width:100%;padding:12px;margin:6px 0 12px;border:1px solid #dce2ec;border-radius:7px}button{background:#3978e8;color:white;border:0;font-weight:bold}h2{margin-top:0}.note{color:#657187;font-size:13px}</style><div class="box"><h2>Customer Information</h2><form method="post" enctype="multipart/form-data"><input type="hidden" name="kind" value="customer"><input type="hidden" name="csrf" value="{app.portal_token}"><label>Full name *</label><input required name="name"><label>Phone number *</label><input required name="phone" type="tel"><label>Email</label><input name="email" type="email"><label>Address</label><textarea name="address"></textarea><label>GSTIN / Tax ID</label><input name="gstin"><label>Employee name (staff assisting)</label><select name="assigned_employee">{staff_options}</select><label>Customer photo (optional)</label><input type="file" name="photo" accept="image/jpeg,image/png,image/webp"><button>Submit customer details</button></form><hr><h2>Submit payment receipt</h2><p class="note">AI reads visible details from an image or text-based PDF. The shop must verify the receipt before recording payment.</p><form method="post" enctype="multipart/form-data"><input type="hidden" name="kind" value="payment"><input type="hidden" name="csrf" value="{app.portal_token}"><label>Your name *</label><input required name="name"><label>Phone *</label><input required name="phone" type="tel"><label>UPI / bank receipt image or PDF *</label><input required type="file" name="receipt" accept="image/png,image/jpeg,image/webp,application/pdf"><button>Send for verification</button></form></div></html>'''
                self.send_page(page)
            def do_POST(self):
                if not self.authorized():
                    self.send_page("<h2>Invalid or expired form link. Ask the shop for a new link.</h2>",403);return
                if self.rate_limited():
                    self.send_page("<h2>Too many submissions. Try again in a minute.</h2>",429);return
                try:length=int(self.headers.get("Content-Length",0))
                except (TypeError,ValueError):length=0
                if length<=0 or length>8*1024*1024:
                    self.send_page("<h2>Upload must be smaller than 8 MB.</h2>",400);return
                body=self.rfile.read(length)
                form={};uploaded=b"";mime_type="image/jpeg";photo=b"";photo_mime="";photo_filename="";employee_uploads={}
                if "multipart/form-data" in self.headers.get("Content-Type",""):
                    message=BytesParser(policy=email_policy).parsebytes((f"Content-Type: {self.headers['Content-Type']}\r\nMIME-Version: 1.0\r\n\r\n").encode()+body)
                    for part in message.iter_parts():
                        field=part.get_param("name",header="content-disposition")
                        data=part.get_payload(decode=True) or b""
                        if field=="receipt":
                            uploaded=data;mime_type=part.get_content_type()
                        elif field=="photo":
                            photo=data;photo_mime=part.get_content_type();photo_filename=part.get_filename() or "customer-photo"
                        elif field in ("id_document","resume"):
                            employee_uploads[field]=(data,part.get_content_type(),part.get_filename() or field)
                        elif field:
                            form[field]=data.decode("utf-8",errors="replace").strip()
                else:
                    form={k:v[0].strip() for k,v in parse_qs(body.decode("utf-8"),keep_blank_values=True).items()}
                if not hmac.compare_digest(str(form.get("csrf","")),app.portal_token):
                    self.send_page("<h2>Security check failed. Reload the form and try again.</h2>",403);return
                limits={"name":120,"phone":40,"email":254,"address":1000,"gstin":30,"assigned_employee":120,"role":120,"department":120,"joining_date":30,"salary":30,"emergency_contact":60,"notes":2000}
                for field,maximum in limits.items():
                    if len(form.get(field,""))>maximum:
                        self.send_page(f"<h2>{html.escape(field.title())} is too long.</h2>",400);return
                name,phone=form.get("name",""),form.get("phone","")
                if not name or not phone:
                    self.send_page("<h2>Name and phone are required.</h2>",400);return
                try:
                    with connect_db() as conn:
                        if form.get("kind")=="customer":
                            submitted_gstin = form.get("gstin", "")
                            if len(re.sub(r"\s+", "", submitted_gstin)) == 15 and not valid_gstin_format(submitted_gstin):
                                raise ValueError("GSTIN must match the standard 15-character format.")
                            conn.execute("INSERT INTO customers(name,phone,email,address,gstin,assigned_employee) VALUES (?,?,?,?,?,?) ON CONFLICT(phone) DO UPDATE SET name=excluded.name,email=excluded.email,address=excluded.address,gstin=excluded.gstin,assigned_employee=excluded.assigned_employee",(name,phone,form.get("email",""),form.get("address",""),form.get("gstin",""),form.get("assigned_employee","")))
                            customer_id=conn.execute("SELECT id FROM customers WHERE phone=?",(phone,)).fetchone()[0]
                            if photo:
                                if photo_mime not in ("image/jpeg","image/png","image/webp") or len(photo)>5*1024*1024 or not app._portal_upload_signature_ok(photo,photo_mime): raise ValueError("Customer photo must be a valid JPG, PNG, or WEBP and under 5 MB.")
                                upload_dir=os.path.join(os.path.dirname(DB_NAME),"customer_uploads");os.makedirs(upload_dir,exist_ok=True)
                                ext={"image/jpeg":".jpg","image/png":".png","image/webp":".webp"}.get(photo_mime,".img")
                                safe_name=f"customer_{customer_id}_{int(time.time())}{ext}";photo_path=os.path.join(upload_dir,safe_name)
                                with open(photo_path,"wb") as photo_file:photo_file.write(photo)
                                conn.execute("INSERT INTO portal_uploads(customer_id,kind,file_path,mime_type) VALUES (?,?,?,?)",(customer_id,"customer_photo",photo_path,photo_mime))
                            response="Your customer details and photo were sent to the shop. Thank you." if photo else "Your customer details were sent to the shop. Thank you."
                        elif form.get("kind")=="payment":
                            if not uploaded:raise ValueError("Upload a payment screenshot.")
                            if mime_type not in ("image/jpeg", "image/png", "image/webp", "application/pdf") or not app._portal_upload_signature_ok(uploaded,mime_type):
                                raise ValueError("Upload a valid PNG, JPG, WEBP, or PDF receipt.")
                            extracted=extract_payment_receipt_upload(uploaded,mime_type)
                            amount=float(extracted.get("amount") or 0)
                            if amount<=0:raise ValueError("AI could not read the payment amount. Submit a clearer screenshot.")
                            conn.execute("INSERT OR IGNORE INTO customers(name,phone) VALUES (?,?)", (name, phone))
                            reference=str(extracted.get("reference", "")).strip()
                            payer=str(extracted.get("payer_name", "")).strip()
                            paid_at=str(extracted.get("paid_at", "")).strip()
                            note=f"AI extracted; verify screenshot details. Payee: {extracted.get('payee_name','')}"
                            conn.execute("INSERT INTO payment_requests(customer_name,phone,amount,payment_mode,reference,payer_name,paid_at,ai_note,receipt_blob,receipt_mime) VALUES (?,?,?,?,?,?,?,?,?,?)",(name,phone,amount,"UPI",reference,payer,paid_at,note,sqlite3.Binary(uploaded),mime_type))
                            response=f"Payment notification received for INR {amount:.2f}. Transaction reference: {reference or 'not read'}. The shop must verify it."
                        else:
                            raise ValueError("Invalid form.")
                    self.send_page(f"<html><meta name='viewport' content='width=device-width'><body style='font:18px Arial;padding:30px;background:#f4f7fc'><h2>{html.escape(response)}</h2><a href='/'>Back to form</a></body></html>")
                    app.root.after(0,app.refresh_portal_views)
                except Exception as exc:
                    self.send_page(f"<h2>Could not submit: {html.escape(str(exc))}</h2><a href='/'>Back</a>",400)
        try:
            self.portal_server=ThreadingHTTPServer(("0.0.0.0",8765),PortalHandler)
            threading.Thread(target=self.portal_server.serve_forever,daemon=True).start()
            sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            try:
                sock.connect(("8.8.8.8",80));ip=sock.getsockname()[0]
            except OSError:
                ip="127.0.0.1"
            finally:sock.close()
            url=f"http://{ip}:8765/?token={self.portal_token}"
            self.portal_url_var.set(url)
            messagebox.showinfo("Customer form is ready",f"Share this link with customers on the same Wi-Fi:\n{url}")
        except OSError as exc:
            messagebox.showerror("Could not start form",str(exc))

    def copy_customer_portal_link(self):
        url=self.portal_url_var.get()
        if url.startswith("http://"):
            self.root.clipboard_clear();self.root.clipboard_append(url)
            messagebox.showinfo("Copied","Customer form link copied.")

    def refresh_portal_views(self):
        page = self.page_title.cget("text") if hasattr(self, "page_title") else ""
        if page == "Employees":
            self.refresh_employee_directory()
        elif page == "Customers":
            self.refresh_customer_table()
        elif page == "Payments":
            self.refresh_payment_requests()
            self.refresh_payment_history()

    def start_public_customer_link(self):
        self.start_customer_portal()
        executable=shutil.which("cloudflared")
        if not executable:
            messagebox.showerror("Public link unavailable","Install Cloudflare Tunnel (cloudflared) on this computer, then click Create public link again. The Wi-Fi link only works on the shop network.")
            return
        if getattr(self,"public_tunnel_process",None) and self.public_tunnel_process.poll() is None:
            current=self.portal_url_var.get()
            messagebox.showinfo("Public link",current);return
        self.public_tunnel_process=subprocess.Popen([executable,"tunnel","--url","http://127.0.0.1:8765"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
        def read_tunnel_output():
            for line in self.public_tunnel_process.stdout:
                match=re.search(r"https://[a-z0-9-]+\.trycloudflare\.com",line)
                if match:
                    url=match.group(0)+"/?token="+self.portal_token
                    self.root.after(0,lambda u=url:self.portal_url_var.set(u))
                    self.root.after(0,lambda u=url:messagebox.showinfo("Public customer link",f"Share this link outside your Wi-Fi:\n{u}\n\nKeep this app and tunnel running while customers use it."))
                    return
        threading.Thread(target=read_tunnel_output,daemon=True).start()

    def choose_business_logo(self):
        path = filedialog.askopenfilename(
            title="Choose business logo",
            filetypes=(("Image files", "*.png *.jpg *.jpeg *.gif"), ("All files", "*.*")),
        )
        if path and "business_logo" in self.setting_vars:
            self.setting_vars["business_logo"].set(path)

    def choose_business_signature(self):
        path=filedialog.askopenfilename(title="Choose signature image",filetypes=(("Signature image","*.png *.jpg *.jpeg"),("All files","*.*")))
        if path and "business_signature" in self.setting_vars:
            self.setting_vars["business_signature"].set(path)

    def choose_backup_directory(self):
        folder = filedialog.askdirectory(title="Choose automatic backup folder")
        if folder and hasattr(self, "backup_directory_var"):
            self.backup_directory_var.set(folder)

    def choose_business_accent(self):
        current = self.setting_vars.get("template_primary", tk.StringVar(value=BLUE)).get()
        _rgb, color = colorchooser.askcolor(color=current, title="Invoice accent color")
        if color:
            self.setting_vars["template_primary"].set(color.upper())
            if hasattr(self, "business_accent_swatch"):
                self.business_accent_swatch.configure(fg=BLUE)

    @staticmethod
    def _security_pin_hash(pin, salt_hex):
        return hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), bytes.fromhex(salt_hex), 240000).hex()

    def request_security_pin(self, action):
        with connect_db() as conn:
            saved = dict(conn.execute("SELECT key,value FROM app_settings WHERE key IN ('security_pin_salt','security_pin_hash')"))
        if not saved.get("security_pin_hash"):
            return True
        entered = self.show_pin_dialog("Security check",f"Enter your PIN to {action}.","Unlock")
        if entered is None:
            return False
        digest = self._security_pin_hash(entered, saved["security_pin_salt"])
        if hmac.compare_digest(digest, saved["security_pin_hash"]):
            return True
        messagebox.showerror("Incorrect PIN", "The security PIN was not accepted.")
        return False

    def show_pin_dialog(self,title,prompt,confirm_label="Continue"):
        dialog=tk.Toplevel(self.root)
        dialog.title(title);dialog.configure(bg=BG);dialog.transient(self.root);dialog.grab_set();dialog.resizable(False,False)
        card=tk.Frame(dialog,bg=WHITE,highlightbackground=BORDER,highlightthickness=1)
        card.pack(fill="both",expand=True,padx=18,pady=18)
        accent=tk.Frame(card,bg=BLUE,height=5);accent.pack(fill="x")
        tk.Label(card,text="🔒  BillEase Security",bg=WHITE,fg=DARK,font=("Segoe UI",16,"bold")).pack(anchor="w",padx=22,pady=(18,4))
        tk.Label(card,text=prompt,bg=WHITE,fg=MUTED,font=("Segoe UI",10),wraplength=340,justify="left").pack(anchor="w",padx=22,pady=(0,14))
        pin_var=tk.StringVar()
        entry=tk.Entry(card,textvariable=pin_var,show="*",font=("Segoe UI",13),relief="solid",bd=1,width=30,justify="center")
        entry.pack(fill="x",padx=22,pady=(0,16),ipady=8)
        result={"value":None}
        actions=tk.Frame(card,bg=WHITE);actions.pack(fill="x",padx=22,pady=(0,18))
        def finish(value):
            result["value"]=value
            dialog.destroy()
        tk.Button(actions,text="Cancel",bg=WHITE,fg=MUTED,relief="flat",cursor="hand2",padx=14,pady=8,command=lambda:finish(None)).pack(side="right",padx=(7,0))
        tk.Button(actions,text=confirm_label,bg=BLUE,fg=WHITE,relief="flat",cursor="hand2",font=("Segoe UI",10,"bold"),padx=16,pady=8,command=lambda:finish(pin_var.get())).pack(side="right")
        entry.bind("<Return>",lambda _event:finish(pin_var.get()))
        dialog.protocol("WM_DELETE_WINDOW",lambda:finish(None))
        dialog.update_idletasks()
        x=self.root.winfo_rootx()+max(0,(self.root.winfo_width()-dialog.winfo_reqwidth())//2)
        y=self.root.winfo_rooty()+max(0,(self.root.winfo_height()-dialog.winfo_reqheight())//2)
        dialog.geometry(f"{dialog.winfo_reqwidth()}x{dialog.winfo_reqheight()}+{x}+{y}")
        entry.focus_set();dialog.wait_window()
        return result["value"]

    def set_security_pin(self):
        with connect_db() as conn:
            saved = dict(conn.execute("SELECT key,value FROM app_settings WHERE key IN ('security_pin_salt','security_pin_hash')"))
        if saved.get("security_pin_hash") and not self.request_security_pin("change security settings"):
            return
        pin = self.show_pin_dialog("Create security PIN","Choose a PIN or passphrase with at least 6 characters.","Continue")
        if pin is None:
            return
        if len(pin) < 6:
            messagebox.showwarning("PIN too short", "Use at least 6 characters for the security PIN.")
            return
        confirmation = self.show_pin_dialog("Confirm security PIN","Enter the same PIN once more.","Save PIN")
        if confirmation != pin:
            messagebox.showwarning("PIN mismatch", "The two entries did not match. The PIN was not changed.")
            return
        salt = secrets.token_hex(16)
        digest = self._security_pin_hash(pin, salt)
        with connect_db() as conn:
            conn.executemany("INSERT INTO app_settings(key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                             (("security_pin_salt", salt), ("security_pin_hash", digest)))
        if hasattr(self, "security_status_label"):
            self.security_status_label.configure(text="PIN protection on", fg=GREEN)
        messagebox.showinfo("PIN enabled", "PIN checks now protect business settings, audit history, restore, and delete actions.")

    def remove_security_pin(self):
        with connect_db() as conn:
            enabled = conn.execute("SELECT 1 FROM app_settings WHERE key='security_pin_hash'").fetchone() is not None
        if not enabled:
            messagebox.showinfo("PIN protection", "No security PIN is currently set.")
            return
        if not self.request_security_pin("remove security PIN protection"):
            return
        with connect_db() as conn:
            conn.execute("DELETE FROM app_settings WHERE key IN ('security_pin_salt','security_pin_hash')")
        if hasattr(self, "security_status_label"):
            self.security_status_label.configure(text="PIN protection off", fg=MUTED)
        messagebox.showinfo("PIN removed", "Security PIN protection has been removed.")

    def save_business_settings(self):
        if not self.request_page_pin("Business Setup","save business settings"):
            return
        values = [(key, var.get().strip()) for key, var in self.setting_vars.items()]
        values.extend((key, widget.get("1.0", "end-1c").strip()) for key, widget in self.setting_texts.items())
        values.extend((
            ("auto_backup_enabled", "1" if getattr(self, "auto_backup_var", tk.BooleanVar(value=True)).get() else "0"),
            ("backup_directory", getattr(self, "backup_directory_var", tk.StringVar()).get().strip()),
            ("cloud_backup_enabled", "1" if getattr(self,"cloud_backup_var",tk.BooleanVar(value=False)).get() else "0"),
            ("dropbox_backup_path", getattr(self,"dropbox_backup_path_var",tk.StringVar(value="/BillEaseBackups")).get().strip() or "/BillEaseBackups"),
        ))
        profile_name = dict(values).get("business_name", "")
        if not profile_name:
            messagebox.showwarning("Business name required", "Enter the business name before saving.")
            return
        tax_id = dict(values).get("business_tax_id", "").strip()
        if len(re.sub(r"\s+", "", tax_id)) == 15 and not valid_gstin_format(tax_id):
            messagebox.showwarning("GSTIN format", "The business GSTIN does not match the standard 15-character format. Check it or use another tax ID.")
            return
        invoice_prefix = dict(values).get("invoice_prefix", "INV") or "INV"
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,12}", invoice_prefix):
            messagebox.showwarning("Invalid invoice prefix", "Use 1–12 letters, numbers, hyphens, or underscores.")
            return
        values = [(key, invoice_prefix if key == "invoice_prefix" else value) for key, value in values]
        accent = dict(values).get("template_primary", BLUE)
        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", accent):
            messagebox.showwarning("Invalid invoice color", "Choose a valid six-digit color such as #2563EB.")
            return
        due_days = dict(values).get("invoice_due_days", "")
        if due_days and (not due_days.isdigit() or int(due_days) > 3650):
            messagebox.showwarning("Invalid due days", "Default due days must be a whole number from 0 to 3650.")
            return
        logo_path = dict(values).get("business_logo", "")
        if logo_path and not os.path.isfile(logo_path):
            messagebox.showwarning("Logo not found", "Choose an existing logo image file or clear the logo path.")
            return
        signature_path = dict(values).get("business_signature", "")
        if signature_path and not os.path.isfile(signature_path):
            messagebox.showwarning("Signature image not found", "Choose an existing signature image file or clear the signature path.")
            return
        with connect_db() as conn:
            conn.executemany("INSERT INTO app_settings(key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", values)
        messagebox.showinfo("Saved", "Business profile and invoice settings saved.")

    def run_automatic_backup(self):
        try:
            with connect_db() as conn:
                settings = dict(conn.execute("SELECT key,value FROM app_settings WHERE key IN ('auto_backup_enabled','backup_directory','auto_backup_last_date','cloud_backup_enabled','dropbox_backup_path')"))
            today = date.today().isoformat()
            if settings.get("auto_backup_enabled", "1") == "1" and settings.get("auto_backup_last_date") != today:
                folder = settings.get("backup_directory", "").strip()
                if not folder:
                    folder = os.path.join(os.path.dirname(os.path.abspath(DB_NAME)), "billease_backups")
                os.makedirs(folder, exist_ok=True)
                backup_path = os.path.join(folder, f"billease-auto-{today}.db")
                with sqlite3.connect(DB_NAME, timeout=30) as source, sqlite3.connect(backup_path, timeout=30) as target:
                    source.backup(target)
                with connect_db() as conn:
                    conn.execute("INSERT INTO app_settings(key,value) VALUES ('auto_backup_last_date',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (today,))
                if settings.get("cloud_backup_enabled","0")=="1":
                    threading.Thread(target=self.upload_auto_backup,kwargs={"backup_path":backup_path,"remote_folder":settings.get("dropbox_backup_path","/BillEaseBackups")},daemon=True).start()
        except (OSError, sqlite3.Error) as exc:
            try:
                messagebox.showwarning("Automatic backup", f"Today’s backup could not be created: {exc}")
            except tk.TclError:
                pass
        next_run = datetime.now().replace(hour=2, minute=0, second=0, microsecond=0) + timedelta(days=1)
        try:
            self.root.after(max(60_000, int((next_run-datetime.now()).total_seconds()*1000)), self.run_automatic_backup)
        except tk.TclError:
            pass

    def upload_auto_backup(self,backup_path,remote_folder):
        try:
            remote=upload_backup_to_dropbox(backup_path,remote_folder)
            with connect_db() as conn:conn.execute("INSERT INTO app_settings(key,value) VALUES ('cloud_backup_last_result',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(f"Uploaded {datetime.now().isoformat(timespec='minutes')} · {remote}",))
            self.root.after(0,lambda:self.set_cloud_backup_status(f"Cloud backup complete: {remote}",GREEN))
        except Exception as exc:
            error=str(exc)
            try:
                with connect_db() as conn:conn.execute("INSERT INTO app_settings(key,value) VALUES ('cloud_backup_last_result',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(f"Failed {datetime.now().isoformat(timespec='minutes')} · {error[:240]}",))
                self.root.after(0,lambda:self.set_cloud_backup_status(f"Cloud backup failed: {error[:180]}",RED))
            except Exception:pass

    def set_cloud_backup_status(self,text,color):
        if hasattr(self,"cloud_backup_status") and self.cloud_backup_status.winfo_exists():
            self.cloud_backup_status.configure(text=text,fg=color)

    def backup_to_dropbox_now(self):
        if not self.request_security_pin("create a Dropbox backup"):
            return
        with connect_db() as conn:
            settings=dict(conn.execute("SELECT key,value FROM app_settings WHERE key IN ('dropbox_backup_path',)"))
        remote_folder=getattr(self,"dropbox_backup_path_var",tk.StringVar(value=settings.get("dropbox_backup_path","/BillEaseBackups"))).get().strip() or "/BillEaseBackups"
        with connect_db() as conn:
            conn.executemany("INSERT INTO app_settings(key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(("dropbox_backup_path",remote_folder),("cloud_backup_enabled","1" if getattr(self,"cloud_backup_var",tk.BooleanVar(value=False)).get() else "0")))
        backup_path=os.path.join(tempfile.gettempdir(),f"billease-cloud-{datetime.now().strftime('%Y%m%d-%H%M%S')}.db")
        if hasattr(self,"cloud_backup_status"):self.cloud_backup_status.configure(text="Creating and uploading backup…",fg=BLUE)
        def worker():
            try:
                with sqlite3.connect(DB_NAME,timeout=30) as source,sqlite3.connect(backup_path,timeout=30) as target:source.backup(target)
                remote=upload_backup_to_dropbox(backup_path,remote_folder)
                self.root.after(0,lambda:self.finish_manual_cloud_backup(remote))
            except Exception as exc:
                error=str(exc)
                self.root.after(0,lambda:messagebox.showerror("Dropbox backup",error))
                if hasattr(self,"cloud_backup_status"):
                    try:self.root.after(0,lambda:self.cloud_backup_status.configure(text=f"Cloud backup failed: {error[:180]}",fg=RED))
                    except tk.TclError:pass
            finally:
                try:os.remove(backup_path)
                except OSError:pass
        threading.Thread(target=worker,daemon=True).start()

    def finish_manual_cloud_backup(self,remote_path):
        if hasattr(self,"cloud_backup_status"):
            self.cloud_backup_status.configure(text=f"Cloud backup complete: {remote_path}",fg=GREEN)
        messagebox.showinfo("Dropbox backup complete",f"SQLite backup uploaded to Dropbox:\n{remote_path}")

    def backup_database(self):
        if not self.request_security_pin("create a database backup"):
            return
        path = filedialog.asksaveasfilename(defaultextension=".db", filetypes=(("SQLite database", "*.db"),), initialfile=f"billease-backup-{date.today().isoformat()}.db")
        if not path:
            return
        with sqlite3.connect(DB_NAME, timeout=30) as source, sqlite3.connect(path, timeout=30) as target:
            source.backup(target)
        messagebox.showinfo("Backup complete", f"Database backup saved to:\n{path}")

    def show_audit_history(self):
        if self.role != "admin":
            messagebox.showerror("Permission denied", "Only an administrator can view the audit history.")
            return
        if not self.request_security_pin("view audit history"):
            return
        window = tk.Toplevel(self.root)
        window.title("Invoice Audit History")
        window.geometry("780x420")
        table = ttk.Treeview(window, columns=("date", "user", "action", "invoice", "detail"), show="headings")
        for col, title, width in (("date","DATE",160),("user","USER",120),("action","ACTION",100),("invoice","INVOICE ID",90),("detail","DETAIL",280)):
            table.heading(col, text=title); table.column(col, width=width)
        table.pack(fill="both", expand=True, padx=10, pady=10)
        with connect_db() as conn:
            rows = conn.execute("SELECT created_at,username,action,COALESCE(invoice_id,''),COALESCE(detail,'') FROM audit_log ORDER BY id DESC").fetchall()
        for row in rows:
            table.insert("", "end", values=row)

    def restore_database(self):
        if self.role != "admin":
            messagebox.showerror("Permission denied", "Only an administrator can restore backups.")
            return
        if not self.request_security_pin("restore a database backup"):
            return
        path = filedialog.askopenfilename(filetypes=(("SQLite database", "*.db"), ("All files", "*.*")))
        if not path:
            return
        if not messagebox.askyesno("Restore backup", "Restoring replaces the current local database. Continue?"):
            return
        try:
            with sqlite3.connect(path, timeout=30) as source, sqlite3.connect(DB_NAME, timeout=30) as target:
                source.backup(target)
            initialize_database()
            messagebox.showinfo("Restore complete", "Backup restored. Restart the app to reload all screens.")
        except sqlite3.Error as exc:
            messagebox.showerror("Restore failed", str(exc))

    def export_invoice_pdf(self):
        selected = self.bill_table.selection() if hasattr(self, "bill_table") else ()
        if not selected:
            messagebox.showwarning("Select invoice", "Select an invoice from the list first.")
            return
        bill_id = int(self.bill_table.item(selected[0], "values")[0])
        self.save_invoice_pdf_for_id(bill_id)

    def generate_invoice_pdf(self):
        search_value = self.invoice_lookup_var.get().strip()
        if not search_value:
            messagebox.showwarning("Invoice details needed", "Enter an invoice ID, invoice number, or customer phone number.")
            return
        with connect_db() as conn:
            if search_value.isdigit():
                row = conn.execute("SELECT id FROM bills WHERE id=? OR invoice_no=? ORDER BY CASE WHEN id=? THEN 0 ELSE 1 END LIMIT 1", (int(search_value), search_value, int(search_value))).fetchone()
            else:
                row = conn.execute("SELECT id FROM bills WHERE invoice_no=?", (search_value,)).fetchone()
            if not row:
                phone_digits="".join(character for character in search_value if character.isdigit())
                matches=[]
                if phone_digits:
                    matches=conn.execute("SELECT b.id,COALESCE(b.invoice_no,'INV-'||b.id),c.phone FROM bills b JOIN customers c ON c.id=b.customer_id ORDER BY b.bill_date DESC,b.id DESC").fetchall()
                    matches=[candidate for candidate in matches if "".join(character for character in str(candidate[2] or "") if character.isdigit())==phone_digits]
                if matches:
                    row=(matches[0][0],)
                    if len(matches)>1:
                        messagebox.showinfo("Customer invoices",f"Found {len(matches)} invoices for this phone number. Generating the latest invoice: {matches[0][1]}.")
        if not row:
            messagebox.showerror("Invoice not found", f"No invoice matches '{search_value}'.")
            return
        self.save_invoice_pdf_for_id(row[0])

    def save_invoice_pdf_for_id(self, bill_id, output_path=None, announce=True):
        with connect_db() as conn:
            invoice_no = conn.execute("SELECT invoice_no FROM bills WHERE id=?", (bill_id,)).fetchone()
        if not invoice_no:
            messagebox.showerror("Invoice not found", "That invoice no longer exists.")
            return
        suggested_name = (invoice_no[0] or f"invoice-{bill_id}").replace("/", "-").replace("\\", "-")
        path = output_path or filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=(("PDF document", "*.pdf"),), initialfile=f"{suggested_name}.pdf", title="Save invoice as PDF")
        if not path:
            return
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
        except ImportError:
            messagebox.showerror("PDF support needed", "Install PDF support with: pip install reportlab")
            return
        with connect_db() as conn:
            template_name = self.invoice_template_var.get() if hasattr(self, "invoice_template_var") else None
            template_font = self.invoice_font_var.get() if hasattr(self, "invoice_font_var") else None
            template_accent = self.invoice_accent_var.get() if hasattr(self, "invoice_accent_var") else None
            try:
                template_font_size = int(self.invoice_font_size_var.get()) if hasattr(self, "invoice_font_size_var") else None
            except ValueError:
                template_font_size = None
            updates=[]
            values=[]
            for column,value in (("template_name",template_name),("template_font",template_font),("template_font_size",template_font_size),("template_accent",template_accent)):
                if value is not None:
                    updates.append(f"{column}=?");values.append(value)
            if updates:
                conn.execute(f"UPDATE bills SET {','.join(updates)} WHERE id=?",(*values,bill_id))
                conn.executemany("INSERT INTO app_settings(key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (("invoice_template",template_name),("template_font",template_font),("template_font_size",str(template_font_size)),("template_primary",template_accent)))
            bill = conn.execute("SELECT b.invoice_no,b.bill_date,b.due_date,b.subtotal,b.discount,b.tax_total,b.total,b.paid,c.name,c.phone,c.email,c.address,c.gstin,b.template_name,b.template_font,b.template_accent,b.template_font_size FROM bills b JOIN customers c ON c.id=b.customer_id WHERE b.id=?", (bill_id,)).fetchone()
            lines = conn.execute("SELECT l.description,COALESCE(p.sku,''),COALESCE(p.category,''),l.quantity,l.unit,l.rate,l.discount,l.tax_rate,l.tax_amount,l.line_total FROM invoice_lines l LEFT JOIN products p ON p.id=l.product_id WHERE l.bill_id=? ORDER BY l.id", (bill_id,)).fetchall()
            settings = dict(conn.execute("SELECT key,value FROM app_settings"))
            try:
                payment_row = conn.execute("SELECT payment_mode FROM business_payments WHERE bill_id=? ORDER BY id DESC LIMIT 1", (bill_id,)).fetchone()
            except sqlite3.Error:
                payment_row = None
        pdf = canvas.Canvas(path, pagesize=A4)
        page_width, page_height = A4
        template_name = bill[13] or "Classic"
        font_key = bill[14] or "Helvetica"
        font_regular, font_bold = {"Helvetica": ("Helvetica", "Helvetica-Bold"), "Times": ("Times-Roman", "Times-Bold"), "Courier": ("Courier", "Courier-Bold")}.get(font_key, ("Helvetica", "Helvetica-Bold"))
        try:
            font_size = max(8, min(12, int(bill[16] or 10)))
        except (TypeError, ValueError):
            font_size = 10
        accent = bill[15] or settings.get("template_primary", BLUE)
        try:
            from reportlab.lib.colors import HexColor, white, black
            from reportlab.lib.utils import simpleSplit
            accent_color = HexColor(accent)
        except Exception:
            from reportlab.lib.colors import HexColor, white, black
            from reportlab.lib.utils import simpleSplit
            accent_color = HexColor(BLUE)
        if template_name == "Modern":
            accent_color = HexColor(BLUE)
        pdf.setStrokeColor(accent_color)
        logo = settings.get("business_logo", "")
        if template_name == "Modern":
            # Blue and ink invoice inspired by the supplied reference.
            pdf.setFillColor(white); pdf.rect(0,0,page_width,page_height,fill=1,stroke=0)
            pdf.setFillColor(accent_color); pdf.rect(0,page_height-105,page_width,105,fill=1,stroke=0)
            pdf.setFillColor(white); pdf.rect(34,page_height-87,page_width-68,65,fill=1,stroke=0)
            if logo and os.path.isfile(logo):
                try: pdf.drawImage(logo,45,page_height-77,width=54,height=44,preserveAspectRatio=True,mask="auto")
                except Exception: pass
            pdf.setFillColor(black); pdf.setFont(font_bold,font_size+3); pdf.drawString(108,page_height-49,settings.get("business_name","BillEase")[:32])
            pdf.setFont(font_regular,max(7,font_size-2)); pdf.drawString(108,page_height-67,settings.get("business_address","")[:58])
            contact = "  ·  ".join(value for value in (settings.get("business_phone", ""), settings.get("business_email", ""), settings.get("business_website", "")) if value)
            if contact:
                pdf.setFont(font_regular,7); pdf.drawString(108,page_height-78,contact[:72])
            pdf.setFillColor(accent_color); pdf.rect(page_width-205,page_height-86,160,62,fill=1,stroke=0)
            pdf.setFillColor(white); pdf.setFont(font_bold,font_size+8); pdf.drawCentredString(page_width-125,page_height-53,"INVOICE")
            stripe_y=page_height-150
            pdf.setFillColor(accent_color);pdf.rect(40,stripe_y,page_width-80,34,fill=1,stroke=0)
            pdf.setFillColor(white);pdf.setFont(font_bold,font_size-1);pdf.drawString(52,stripe_y+12,f"INVOICE NO.  {bill[0] or 'INV-' + str(bill_id)}")
            pdf.setFillColor(black);pdf.rect(page_width-195,stripe_y,155,34,fill=1,stroke=0)
            pdf.setFillColor(white);pdf.setFont(font_bold,font_size-1);pdf.drawRightString(page_width-50,stripe_y+12,f"DATE  {bill[1]}")
            # Two information panels keep customer and payment details easy to scan.
            pdf.setFillColor(accent_color); pdf.setFont(font_bold,font_size); pdf.drawString(45,page_height-166,"BILL TO")
            pdf.drawString(315,page_height-166,"ACCOUNT DETAILS")
            pdf.setFillColor(black); pdf.setFont(font_bold,font_size); pdf.drawString(45,page_height-184,str(bill[8] or "Walk-in customer")[:38])
            pdf.setFont(font_regular,max(7,font_size-1))
            pdf.drawString(45,page_height-199,f"Phone: {bill[9] or '—'}")
            pdf.drawString(45,page_height-213,f"{(bill[11] or '')[:50]}")
            pdf.drawString(45,page_height-227,f"Email: {bill[10] or '—'}")
            pdf.drawString(45,page_height-241,f"Tax ID: {bill[12] or '—'}")
            paid_amount=float(bill[7] or 0); grand_total=float(bill[6] or 0)
            pay_status="PAID" if paid_amount >= grand_total else ("PARTIALLY PAID" if paid_amount > 0 else "UNPAID")
            pdf.drawString(315,page_height-184,f"Due date: {bill[2] or '—'}")
            pdf.drawString(315,page_height-199,f"Payment: {(payment_row[0] if payment_row else '—') or '—'}")
            pdf.drawString(315,page_height-213,f"Paid: INR {paid_amount:,.2f}")
            pdf.drawString(315,page_height-227,f"Status: {pay_status}")
            pdf.drawString(315,page_height-241,f"Business tax ID: {settings.get('business_tax_id', '—') or '—'}")
            payment_details = settings.get("business_payment_details", "")
            if payment_details:
                pdf.drawString(315,page_height-255,f"Payment details: {payment_details[:38]}")
            y=page_height-272 if payment_details else page_height-257
        else:
            if template_name == "Corporate":
                pdf.setFillColor(accent_color); pdf.rect(0,0,16,page_height,fill=1,stroke=0)
            elif template_name == "Elegant":
                pdf.setLineWidth(1.5); pdf.line(45,page_height-42,page_width-45,page_height-42)
                pdf.setLineWidth(.5); pdf.line(45,page_height-46,page_width-45,page_height-46)
            elif template_name == "Minimal":
                pdf.setLineWidth(2); pdf.line(45,page_height-50,page_width-45,page_height-50)
            else:
                pdf.setFillColor(accent_color); pdf.rect(45,page_height-54,page_width-90,4,fill=1,stroke=0)
            if logo and os.path.isfile(logo):
                try: pdf.drawImage(logo,page_width-145,page_height-88,width=90,height=42,preserveAspectRatio=True,mask="auto")
                except Exception: pass
            pdf.setFillColor(black); pdf.setFont(font_bold,font_size+7); pdf.drawString(45,page_height-78,settings.get("business_name","BillEase"))
            pdf.setFont(font_regular,max(8,font_size-1)); pdf.drawString(45,page_height-96,settings.get("business_address",""))
            if template_name == "Elegant":
                pdf.setFillColor(accent_color); pdf.setFont(font_bold,font_size+3); pdf.drawRightString(page_width-45,page_height-78,f"INVOICE  {bill[0] or 'INV-' + str(bill_id)}")
                pdf.setFillColor(black)
            else:
                pdf.setFont(font_bold,font_size+3); pdf.drawString(45,page_height-128,f"Invoice {bill[0] or 'INV-' + str(bill_id)}")
            y=page_height-151
        if template_name != "Modern":
            pdf.setFillColor(black)
            pdf.setFont(font_regular,max(8,font_size-1))
            contact_line = "  ·  ".join(value for value in (settings.get("business_phone", ""), settings.get("business_email", ""), settings.get("business_website", "")) if value)
            for text in (f"Business tax ID: {settings.get('business_tax_id', '')}", f"Business contact: {contact_line}", f"Payment details: {settings.get('business_payment_details', '')}", f"Date: {bill[1]}    Due: {bill[2] or ''}", f"Customer: {bill[8]}    Phone: {bill[9] or ''}", f"Email: {bill[10] or ''}    GSTIN: {bill[12] or ''}", f"Address: {bill[11] or ''}"):
                pdf.drawString(45, y, text[:115]); y -= font_size+6
            y -= 8
        if template_name == "Modern":
            # Blue reference layout: boxed line-item grid, payment details, totals and terms.
            left,right=40,page_width-40
            table_top=page_height-290
            row_count=max(6,len(lines))
            row_height=min(34,220/row_count)
            header_height=25
            table_bottom=table_top-header_height-row_count*row_height
            xs=(left,left+28,left+193,left+255,left+312,left+378,left+445,right)
            pdf.setFillColor(HexColor(LIGHT_BLUE));pdf.rect(left,table_top-header_height,right-left,header_height,fill=1,stroke=0)
            pdf.setStrokeColor(HexColor(DARK));pdf.setLineWidth(.75)
            pdf.rect(left,table_bottom,right-left,table_top-table_bottom,fill=0,stroke=1)
            for x in xs[1:-1]:pdf.line(x,table_bottom,x,table_top)
            pdf.line(left,table_top-header_height,right,table_top-header_height)
            for row_index in range(1,row_count):
                line_y=table_top-header_height-row_index*row_height
                pdf.line(left,line_y,right,line_y)
            pdf.setFillColor(accent_color);pdf.setFont(font_bold,8)
            for x,label in zip(((xs[0]+xs[1])/2,(xs[1]+xs[2])/2,(xs[2]+xs[3])/2,(xs[3]+xs[4])/2,(xs[4]+xs[5])/2,(xs[5]+xs[6])/2,(xs[6]+xs[7])/2),("No.","Product","SKU / code","Qty / unit","Unit price","Tax %","Line total")):
                pdf.drawCentredString(x,table_top-16,label)
            pdf.setFillColor(black);pdf.setFont(font_regular,max(7,font_size-2))
            for index,(desc,sku,category,qty,unit,rate,discount,tax_rate,tax_amt,total) in enumerate(lines):
                row_top=table_top-header_height-index*row_height
                baseline=row_top-row_height/2-2
                if index%2==1:
                    pdf.setFillColor(HexColor(BG));pdf.rect(left,row_top-row_height,right-left,row_height,fill=1,stroke=0)
                    pdf.setFillColor(black)
                pdf.drawCentredString((xs[0]+xs[1])/2,baseline,str(index+1))
                pdf.drawString(xs[1]+5,baseline+3 if category else baseline,str(desc)[:27])
                if category:
                    pdf.setFont(font_regular,6.5);pdf.setFillColor(HexColor(MUTED));pdf.drawString(xs[1]+5,baseline-6,str(category)[:27]);pdf.setFillColor(black);pdf.setFont(font_regular,max(7,font_size-2))
                pdf.drawString(xs[2]+4,baseline,str(sku)[:11])
                pdf.drawCentredString((xs[3]+xs[4])/2,baseline,f"{qty:g} {unit}"[:10])
                pdf.drawRightString(xs[5]-5,baseline,f"{rate:,.2f}")
                pdf.drawCentredString((xs[5]+xs[6])/2,baseline,f"{tax_rate:g}%")
                pdf.drawRightString(xs[7]-6,baseline,f"{total:,.2f}")
            # Draw grid lines again on top of the alternating row fills.
            pdf.setStrokeColor(HexColor(DARK));pdf.rect(left,table_bottom,right-left,table_top-table_bottom,fill=0,stroke=1)
            for x in xs[1:-1]:pdf.line(x,table_bottom,x,table_top)
            pdf.line(left,table_top-header_height,right,table_top-header_height)
            for row_index in range(1,row_count):pdf.line(left,table_top-header_height-row_index*row_height,right,table_top-header_height-row_index*row_height)

            info_y=table_bottom-24
            pdf.setFillColor(accent_color);pdf.setFont(font_bold,10);pdf.drawString(left,info_y,"PAYMENT METHOD")
            pdf.setFillColor(black);pdf.setFont(font_regular,8)
            payment_lines=simpleSplit(settings.get("business_payment_details","") or "Payment details not provided",font_regular,8,300)
            for line_index,line in enumerate(payment_lines[:4]):pdf.drawString(left,info_y-16-line_index*11,line)
            payment_mode=payment_row[0] if payment_row else "—"
            pdf.drawString(left,info_y-64,f"Recorded payment mode: {payment_mode}")

            total_box_x=left+370;total_box_top=info_y+7;total_row_h=20
            total_rows=(("Subtotal",bill[3]),("Discount",bill[4]),("Tax",bill[5]),("Total",bill[6]))
            pdf.setStrokeColor(HexColor(DARK));pdf.rect(total_box_x,total_box_top-total_row_h*len(total_rows),right-total_box_x,total_row_h*len(total_rows),fill=0,stroke=1)
            split_x=total_box_x+72;pdf.line(split_x,total_box_top-total_row_h*len(total_rows),split_x,total_box_top)
            for index,(label,value) in enumerate(total_rows):
                row_top=total_box_top-index*total_row_h
                if index:pdf.line(total_box_x,row_top,right,row_top)
                if label=="Total":
                    pdf.setFillColor(HexColor(LIGHT_BLUE));pdf.rect(total_box_x,row_top-total_row_h,right-total_box_x,total_row_h,fill=1,stroke=0)
                    pdf.setFillColor(black)
                pdf.setFont(font_bold if label=="Total" else font_regular,8)
                pdf.drawCentredString((total_box_x+split_x)/2,row_top-13,label)
                pdf.drawRightString(right-7,row_top-13,f"INR {value:,.2f}")
            terms_y=155
            pdf.setFillColor(accent_color);pdf.setFont(font_bold,10);pdf.drawString(left,terms_y,"TERMS AND CONDITIONS")
            pdf.setFillColor(black);pdf.setFont(font_regular,7)
            terms_text="\n".join(value for value in (settings.get("template_footer",""),settings.get("template_terms","")) if value)
            term_lines=simpleSplit(terms_text,font_regular,7,330) if terms_text else ["Thank you for your business."]
            for index,line in enumerate(term_lines[:6]):pdf.drawString(left,terms_y-14-index*10,line)
        else:
            # Other styles retain their own header, while sharing a full grid table.
            left,right=40,page_width-40
            col_x=(left,left+25,left+165,left+220,left+268,left+333,left+383,left+445,right)
            header_h=24;row_h=22;table_top=y+10;line_index=0;first_table_page=True
            while first_table_page or line_index<len(lines):
                first_table_page=False
                available=max(1,int((table_top-250-header_h)/row_h))
                count=min(available,max(0,len(lines)-line_index))
                table_bottom=table_top-header_h-count*row_h
                pdf.setFillColor(accent_color);pdf.rect(left,table_top-header_h,right-left,header_h,fill=1,stroke=0)
                pdf.setFillColor(white);pdf.setFont(font_bold,max(7,font_size-2))
                for x,label in zip(tuple((col_x[i]+col_x[i+1])/2 for i in range(8)),("No.","Product","SKU / code","Qty / unit","Unit price","Tax %","Tax amt","Total")):
                    pdf.drawCentredString(x,table_top-16,label)
                pdf.setFillColor(black);pdf.setFont(font_regular,max(7,font_size-2))
                for offset in range(count):
                    index=line_index+offset
                    desc,sku,category,qty,unit,rate,discount,tax_rate,tax_amt,total=lines[index]
                    row_top=table_top-header_h-offset*row_h;baseline=row_top-row_h/2-2
                    if offset%2==1:
                        pdf.setFillColor(HexColor(BG));pdf.rect(left,row_top-row_h,right-left,row_h,fill=1,stroke=0);pdf.setFillColor(black)
                    pdf.drawCentredString((col_x[0]+col_x[1])/2,baseline,str(index+1))
                    pdf.drawString(col_x[1]+4,baseline+3 if category else baseline,str(desc)[:22])
                    if category:
                        pdf.setFont(font_regular,6.5);pdf.setFillColor(HexColor(MUTED));pdf.drawString(col_x[1]+4,baseline-6,str(category)[:22]);pdf.setFillColor(black);pdf.setFont(font_regular,max(7,font_size-2))
                    pdf.drawString(col_x[2]+3,baseline,str(sku)[:9])
                    pdf.drawCentredString((col_x[3]+col_x[4])/2,baseline,f"{qty:g} {unit}"[:9])
                    pdf.drawRightString(col_x[5]-4,baseline,f"{rate:,.2f}")
                    pdf.drawCentredString((col_x[5]+col_x[6])/2,baseline,f"{tax_rate:g}%")
                    pdf.drawRightString(col_x[7]-4,baseline,f"{tax_amt:,.2f}")
                    pdf.drawRightString(right-5,baseline,f"{total:,.2f}")
                pdf.setStrokeColor(HexColor(DARK));pdf.setLineWidth(.65)
                pdf.rect(left,table_bottom,right-left,table_top-table_bottom,fill=0,stroke=1)
                for x in col_x[1:-1]:pdf.line(x,table_bottom,x,table_top)
                pdf.line(left,table_top-header_h,right,table_top-header_h)
                for offset in range(1,count):pdf.line(left,table_top-header_h-offset*row_h,right,table_top-header_h-offset*row_h)
                line_index+=count
                if line_index<len(lines):
                    pdf.showPage();table_top=page_height-55
                else:
                    y=table_bottom-20
            for label, value in (("Subtotal",bill[3]),("Discount",bill[4]),("Tax",bill[5]),("Grand total",bill[6]),("Paid",bill[7]),("Balance due",bill[6]-bill[7])):
                pdf.setFont(font_bold if label=="Grand total" else font_regular,font_size); pdf.drawRightString(455,y,label); pdf.drawRightString(545,y,f"INR {value:,.2f}"); y-=font_size+6
            pdf.setFont(font_regular,max(7,font_size-2))
            for note in (settings.get("template_footer", ""), settings.get("template_terms", "")):
                if note:
                    y -= 16
                    note_lines = simpleSplit(note, font_regular, max(7, font_size-2), page_width-90)
                    for note_line in note_lines:
                        y -= 10
                        if y < 70:
                            pdf.showPage(); y=page_height-55
                            pdf.setFont(font_regular,max(7,font_size-2))
                        pdf.drawString(45, y, note_line)
        signature_path=settings.get("business_signature","")
        pdf.setStrokeColor(HexColor(BORDER)); pdf.line(page_width-185,55,page_width-45,55)
        if signature_path and os.path.isfile(signature_path):
            try:pdf.drawImage(signature_path,page_width-175,59,width=120,height=34,preserveAspectRatio=True,anchor="c",mask="auto")
            except Exception:pass
        pdf.setFillColor(HexColor(MUTED)); pdf.setFont(font_regular,8)
        pdf.drawCentredString(page_width-115,43,"AUTHORIZED SIGNATURE")
        if template_name == "Modern":
            pdf.setFillColor(accent_color); pdf.rect(0,0,page_width,10,fill=1,stroke=0)
        pdf.save()
        if announce:
            try:
                os.startfile(path, "print")
            except (AttributeError, OSError):
                pass
            messagebox.showinfo("Invoice ready", f"PDF saved to:\n{path}")
        return path

    def send_selected_invoice_email(self):
        selected=self.bill_table.selection() if hasattr(self,"bill_table") else ()
        if not selected:
            messagebox.showwarning("Select invoice","Select an invoice first.");return
        bill_id=int(self.bill_table.item(selected[0],"values")[0])
        with connect_db() as conn:
            row=conn.execute("SELECT b.invoice_no,c.name,c.email FROM bills b JOIN customers c ON c.id=b.customer_id WHERE b.id=?",(bill_id,)).fetchone()
        if not row or not row[2]:
            messagebox.showwarning("Customer email missing","Add an email address to this customer before sending the invoice.");return
        host=os.environ.get("BILLEASE_SMTP_HOST","").strip()
        username=os.environ.get("BILLEASE_SMTP_USER","").strip()
        password=os.environ.get("BILLEASE_SMTP_PASSWORD","")
        sender=os.environ.get("BILLEASE_SMTP_FROM",username).strip()
        if not host or not sender:
            messagebox.showerror("Email not configured","Set BILLEASE_SMTP_HOST, BILLEASE_SMTP_USER, BILLEASE_SMTP_PASSWORD, and BILLEASE_SMTP_FROM as Windows environment variables, then restart BillEase.");return
        if not messagebox.askyesno("Send invoice",f"Send {row[0]} to {row[2]} using the configured email account?"):return
        temp_path=os.path.join(tempfile.gettempdir(),f"billease_email_{bill_id}_{int(datetime.now().timestamp())}.pdf")
        try:
            generated=self.save_invoice_pdf_for_id(bill_id,output_path=temp_path,announce=False)
            if not generated:return
            msg=EmailMessage();msg["Subject"]=f"Invoice {row[0]} from BillEase";msg["From"]=sender;msg["To"]=row[2]
            msg.set_content(f"Hello {row[1]},\n\nPlease find invoice {row[0]} attached.\n\nThank you.")
            with open(generated,"rb") as attachment:msg.add_attachment(attachment.read(),maintype="application",subtype="pdf",filename=f"{row[0]}.pdf")
            port=int(os.environ.get("BILLEASE_SMTP_PORT","587"))
            smtp_client=smtplib.SMTP_SSL if port==465 else smtplib.SMTP
            with smtp_client(host,port,timeout=30) as smtp:
                if port!=465:smtp.starttls()
                if username:smtp.login(username,password)
                smtp.send_message(msg)
            status,detail="Sent","SMTP accepted message"
        except Exception as exc:
            status,detail="Failed",str(exc)[:500]
        finally:
            try:os.remove(temp_path)
            except OSError:pass
        with connect_db() as conn:
            conn.execute("INSERT INTO invoice_delivery_log(bill_id,recipient,channel,status,detail) VALUES (?,?,?,?,?)",(bill_id,row[2],"Email",status,detail))
        if status=="Sent":messagebox.showinfo("Invoice sent",f"{row[0]} was accepted by the email server for {row[2]}.")
        else:messagebox.showerror("Email failed",detail)

    def send_selected_payment_reminder(self):
        selected=self.bill_table.selection() if hasattr(self,"bill_table") else ()
        if not selected:
            messagebox.showwarning("Select invoice","Select an invoice first.");return
        bill_id=int(self.bill_table.item(selected[0],"values")[0])
        with connect_db() as conn:row=conn.execute("SELECT b.invoice_no,b.total-b.paid,b.due_date,c.name,c.email FROM bills b JOIN customers c ON c.id=b.customer_id WHERE b.id=?",(bill_id,)).fetchone()
        if not row or not row[4]:
            messagebox.showwarning("Customer email missing","Add an email address to this customer before sending a reminder.");return
        if row[1]<=0:
            messagebox.showinfo("Invoice paid","There is no outstanding amount to remind the customer about.");return
        host=os.environ.get("BILLEASE_SMTP_HOST","").strip();username=os.environ.get("BILLEASE_SMTP_USER","").strip();password=os.environ.get("BILLEASE_SMTP_PASSWORD","");sender=os.environ.get("BILLEASE_SMTP_FROM",username).strip()
        if not host or not sender:
            messagebox.showerror("Email not configured","Set BILLEASE_SMTP_HOST, BILLEASE_SMTP_USER, BILLEASE_SMTP_PASSWORD, and BILLEASE_SMTP_FROM as Windows environment variables, then restart BillEase.");return
        if not messagebox.askyesno("Send payment reminder",f"Send a reminder for ₹{row[1]:,.2f} to {row[4]}?"):return
        try:
            msg=EmailMessage();msg["Subject"]=f"Payment reminder: invoice {row[0]}";msg["From"]=sender;msg["To"]=row[4]
            msg.set_content(f"Hello {row[3]},\n\nThis is a friendly reminder that invoice {row[0]} has an outstanding balance of ₹{row[1]:,.2f}. Due date: {row[2] or 'not specified'}.\n\nPlease contact us if you have already paid. Thank you.")
            port=int(os.environ.get("BILLEASE_SMTP_PORT","587"));smtp_client=smtplib.SMTP_SSL if port==465 else smtplib.SMTP
            with smtp_client(host,port,timeout=30) as smtp:
                if port!=465:smtp.starttls()
                if username:smtp.login(username,password)
                smtp.send_message(msg)
            status,detail="Sent","SMTP accepted message"
        except Exception as exc:status,detail="Failed",str(exc)[:500]
        with connect_db() as conn:conn.execute("INSERT INTO invoice_delivery_log(bill_id,recipient,channel,status,detail) VALUES (?,?,?,?,?)",(bill_id,row[4],"Payment reminder",status,detail))
        if status=="Sent":messagebox.showinfo("Reminder sent",f"Reminder accepted by the email server for {row[4]}.")
        else:messagebox.showerror("Email failed",detail)

    def show_invoice_delivery_history(self):
        selected=self.bill_table.selection() if hasattr(self,"bill_table") else ()
        if not selected:
            messagebox.showwarning("Select invoice","Select an invoice first.");return
        bill_id=int(self.bill_table.item(selected[0],"values")[0])
        window=tk.Toplevel(self.root);window.title("Invoice delivery and payment links");window.geometry("850x400");window.configure(bg=BG)
        table=ttk.Treeview(window,columns=("date","channel","recipient","status","detail"),show="headings")
        for col,label,width in (("date","DATE",145),("channel","CHANNEL",130),("recipient","RECIPIENT",190),("status","STATUS",90),("detail","DETAIL / LINK",280)):
            table.heading(col,text=label);table.column(col,width=width,anchor="center")
        table.pack(fill="both",expand=True,padx=12,pady=12)
        with connect_db() as conn:rows=conn.execute("SELECT created_at,channel,recipient,status,detail FROM invoice_delivery_log WHERE bill_id=? ORDER BY id DESC",(bill_id,)).fetchall()
        for row in rows:table.insert("","end",values=row)

    def create_invoice_payment_link(self):
        selected=self.bill_table.selection() if hasattr(self,"bill_table") else ()
        if not selected:
            messagebox.showwarning("Select invoice","Select an invoice first.");return
        bill_id=int(self.bill_table.item(selected[0],"values")[0])
        key_id=os.environ.get("RAZORPAY_KEY_ID","").strip();secret=os.environ.get("RAZORPAY_KEY_SECRET","").strip()
        if not key_id or not secret:
            with connect_db() as conn:
                upi=conn.execute("SELECT value FROM app_settings WHERE key='business_upi_id'").fetchone()
                bill=conn.execute("SELECT b.invoice_no,b.total-b.paid,c.name FROM bills b JOIN customers c ON c.id=b.customer_id WHERE b.id=?",(bill_id,)).fetchone()
            if upi and upi[0] and bill and bill[1]>0:
                self.create_upi_qr(upi[0],bill[0],bill[1],bill[2]);return
            messagebox.showerror("Payment provider not configured","Set Razorpay API credentials in Windows environment variables, or add your UPI ID under Business Setup to create a static UPI QR.");return
        with connect_db() as conn:
            row=conn.execute("SELECT b.invoice_no,b.total-b.paid,c.name,c.phone,c.email FROM bills b JOIN customers c ON c.id=b.customer_id WHERE b.id=?",(bill_id,)).fetchone()
        if not row or row[1]<=0:
            messagebox.showinfo("No balance due","This invoice has no outstanding balance.");return
        payload={"amount":int(round(float(row[1])*100)),"currency":"INR","reference_id":f"{str(row[0])[:25]}-{int(datetime.now().timestamp())}"[:40],"description":f"Payment for invoice {row[0]}","customer":{"name":row[2]},"upi_link":True,"reminder_enable":True,"notify":{"sms":False,"email":False},"notes":{"invoice_id":str(bill_id)}}
        if row[3]:payload["customer"]["contact"]=row[3]
        if row[4]:payload["customer"]["email"]=row[4]
        def worker():
            try:
                token=base64.b64encode(f"{key_id}:{secret}".encode()).decode()
                req=urllib.request.Request("https://api.razorpay.com/v1/payment_links",data=json.dumps(payload).encode(),headers={"Authorization":f"Basic {token}","Content-Type":"application/json"},method="POST")
                with urllib.request.urlopen(req,timeout=30) as response:data=json.loads(response.read().decode())
                self.root.after(0,lambda:self.finish_payment_link(bill_id,float(row[1]),data))
            except Exception as exc:
                error=str(exc)
                self.root.after(0,lambda:messagebox.showerror("Payment link",error))
        threading.Thread(target=worker,daemon=True).start()

    def create_upi_qr(self,upi_id,invoice_no,amount,customer_name):
        uri="upi://pay?"+urlencode({"pa":upi_id,"pn":customer_name,"am":f"{float(amount):.2f}","cu":"INR","tn":f"Invoice {invoice_no}"})
        path=filedialog.asksaveasfilename(defaultextension=".png",filetypes=(("PNG QR code","*.png"),),initialfile=f"{invoice_no}-upi.png")
        if not path:return
        try:
            import qrcode
            qrcode.make(uri).save(path)
            self.root.clipboard_clear();self.root.clipboard_append(uri);self.root.update()
            try:os.startfile(path)
            except (AttributeError,OSError):pass
            messagebox.showinfo("UPI QR created",f"QR code saved to:\n{path}\n\nThe UPI payment URI was copied too. UPI transfers must be verified from the bank receipt before recording.")
        except ImportError:
            messagebox.showerror("QR package needed","Install QR support with: pip install qrcode[pil]")
        except Exception as exc:messagebox.showerror("UPI QR",str(exc))

    def finish_payment_link(self,bill_id,amount,data):
        link_id=str(data.get("id",""));url=str(data.get("short_url",""));status=str(data.get("status","created"))
        if not link_id or not url:
            messagebox.showerror("Payment link","Provider response did not include a usable payment link.");return
        with connect_db() as conn:
            conn.execute("INSERT OR REPLACE INTO provider_payment_links(bill_id,provider,provider_id,short_url,amount,status) VALUES (?, 'Razorpay', ?, ?, ?, ?)",(bill_id,link_id,url,amount,status))
            invoice=conn.execute("SELECT invoice_no FROM bills WHERE id=?",(bill_id,)).fetchone()
            conn.execute("INSERT INTO invoice_delivery_log(bill_id,recipient,channel,status,detail) VALUES (?,?,?,?,?)",(bill_id,"","Payment link",status,url))
        self.refresh_bill_table()
        try:
            self.root.clipboard_clear();self.root.clipboard_append(url);self.root.update()
        except tk.TclError:pass
        messagebox.showinfo("Payment link created",f"Payment link for {invoice[0] if invoice else 'invoice'}:\n{url}\n\nUse Copy in the dialog to share it. Payment confirmation must be synced and verified.")

    def sync_selected_payment_link(self):
        selected=self.bill_table.selection() if hasattr(self,"bill_table") else ()
        if not selected:
            messagebox.showwarning("Select invoice","Select an invoice first.");return
        bill_id=int(self.bill_table.item(selected[0],"values")[0])
        key_id=os.environ.get("RAZORPAY_KEY_ID","").strip();secret=os.environ.get("RAZORPAY_KEY_SECRET","").strip()
        if not key_id or not secret:
            messagebox.showerror("Payment provider not configured","Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET first.");return
        with connect_db() as conn:link=conn.execute("SELECT provider_id FROM provider_payment_links WHERE bill_id=? ORDER BY id DESC LIMIT 1",(bill_id,)).fetchone()
        if not link:
            messagebox.showinfo("No payment link","Create a payment link for the selected invoice first.");return
        token=base64.b64encode(f"{key_id}:{secret}".encode()).decode()
        req=urllib.request.Request(f"https://api.razorpay.com/v1/payment_links/{link[0]}",headers={"Authorization":f"Basic {token}"})
        try:
            with urllib.request.urlopen(req,timeout=30) as response:data=json.loads(response.read().decode())
        except Exception as exc:
            messagebox.showerror("Sync payment status",str(exc));return
        status=str(data.get("status","unknown"));paid=float(data.get("amount_paid",0) or 0)/100
        with connect_db() as conn:
            conn.execute("UPDATE provider_payment_links SET status=? WHERE provider_id=?",(status,link[0]))
            if status in ("paid","partially_paid") and paid>0:
                bill=conn.execute("SELECT b.customer_id,b.invoice_no,c.name,c.phone FROM bills b JOIN customers c ON c.id=b.customer_id WHERE b.id=?",(bill_id,)).fetchone()
                existing=conn.execute("SELECT id FROM payment_requests WHERE reference=?",(link[0],)).fetchone()
                if bill and not existing:
                    conn.execute("INSERT INTO payment_requests(customer_name,phone,amount,payment_mode,reference,payer_name,paid_at,ai_note,status) VALUES (?,?,?,'Razorpay',?,?,datetime('now'),?,'Pending')",(bill[2],bill[3] or "",paid,link[0],"Provider status: "+status,f"Provider-reported amount paid: ₹{paid:,.2f}; invoice {bill[1]}. Verify before recording."))
        self.refresh_payment_requests()
        messagebox.showinfo("Provider status updated",f"Payment link status: {status}\nAmount reported paid: ₹{paid:,.2f}\nAny payment is listed as Pending for manual verification before it changes invoice balances.")

    # ======================================
    # CUSTOMERS, BILLS AND CREDIT
    # ======================================
    def customer_balance(self, customer_id):
        with connect_db() as conn:
            billed = conn.execute(
                "SELECT COALESCE(SUM(total), 0) FROM bills WHERE customer_id=?",
                (customer_id,)
            ).fetchone()[0]
            paid_on_bills = conn.execute(
                "SELECT COALESCE(SUM(paid), 0) FROM bills WHERE customer_id=?",
                (customer_id,)
            ).fetchone()[0]
            extra_payments = conn.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM customer_payments WHERE customer_id=?",
                (customer_id,)
            ).fetchone()[0]
        return max(0, billed - paid_on_bills - extra_payments)

    def show_employee_directory(self):
        self.clear_content()
        heading=tk.Frame(self.content,bg=BG)
        heading.pack(fill="x",pady=(0,12))
        tk.Label(heading,text="♙  Employee Directory",bg=BG,fg=DARK,font=("Segoe UI",20,"bold")).pack(side="left")
        toolbar=tk.Frame(self.content,bg=WHITE,highlightbackground=BORDER,highlightthickness=1)
        toolbar.pack(fill="x",pady=(0,10))
        self.employee_search_var=tk.StringVar()
        search=tk.Entry(toolbar,textvariable=self.employee_search_var,font=("Segoe UI",10),relief="flat",bd=0)
        search.pack(side="left",fill="x",expand=True,ipady=11,padx=12)
        search.insert(0,"Search employees by name, role, or phone")
        search.bind("<FocusIn>",lambda _e: search.delete(0,"end") if search.get()=="Search employees by name, role, or phone" else None)
        self.employee_search_var.trace_add("write",lambda *_:self.refresh_employee_directory())
        tk.Button(toolbar,text="+ Add employee",bg=BLUE,fg=WHITE,relief="flat",cursor="hand2",font=("Segoe UI",10,"bold"),padx=15,pady=8,command=lambda:self.edit_employee_record()).pack(side="right",padx=5,pady=5)
        tk.Button(toolbar,text="Edit",bg=LIGHT_BLUE,fg=BLUE,relief="flat",cursor="hand2",font=("Segoe UI",10,"bold"),padx=15,pady=8,command=lambda:self.edit_employee_record(True)).pack(side="right",padx=5,pady=5)
        tk.Button(toolbar,text="Delete",bg="#FEE2E2",fg=RED,relief="flat",cursor="hand2",font=("Segoe UI",10,"bold"),padx=15,pady=8,command=self.delete_employee_record).pack(side="right",padx=5,pady=5)
        columns=("id","name","role","phone","email","outstanding")
        self.employee_table=ttk.Treeview(self.content,columns=columns,show="headings",style="Employee.Treeview",height=16)
        self.add_table_scroll_controls(heading,self.employee_table)
        for col,label,width in (("id","ID",60),("name","EMPLOYEE NAME",205),("role","ROLE",160),("phone","PHONE",160),("email","EMAIL",230),("outstanding","ASSIGNED OUTSTANDING",170)):
            self.employee_table.heading(col,text=label)
            self.employee_table.column(col,width=width,anchor="w" if col!="id" else "center")
        self.employee_table.tag_configure("even",background=BG)
        self.employee_table.tag_configure("odd",background=WHITE)
        self.employee_table.pack(fill="both",expand=True)
        self.employee_table.bind("<Double-1>",lambda _e:self.edit_employee_record(True))
        self.refresh_employee_directory()

    def refresh_employee_directory(self):
        if not hasattr(self,"employee_table") or not self.employee_table.winfo_exists():return
        self.employee_table.delete(*self.employee_table.get_children())
        term=getattr(self,"employee_search_var",tk.StringVar()).get().strip().casefold()
        if term=="search employees by name, role, or phone":term=""
        with connect_db() as conn:
            rows=conn.execute("""SELECT e.id,e.name,e.role,COALESCE(e.phone,''),COALESCE(e.email,''),
                COALESCE((SELECT SUM(CASE WHEN b.total>b.paid THEN b.total-b.paid ELSE 0 END) FROM bills b WHERE b.employee_id=e.id),0)
                FROM employees e ORDER BY e.name COLLATE NOCASE""").fetchall()
        for row in rows:
            if term and term not in " ".join(map(str,row)).casefold():continue
            display_values=(*row[:5],f"₹{row[5]:,.2f}")
            self.employee_table.insert("","end",values=display_values,tags=("even" if len(self.employee_table.get_children())%2==0 else "odd",))

    def edit_employee_record(self, editing=False):
        if not self.authorize_sensitive_page("Employee edit"):
            return
        selected=self.employee_table.selection() if hasattr(self,"employee_table") else ()
        if editing and not selected:
            messagebox.showwarning("Select employee","Select an employee row to edit.")
            return
        employee_id=int(self.employee_table.item(selected[0],"values")[0]) if selected else None
        initial=("","Staff","","")
        if employee_id:
            with connect_db() as conn:initial=conn.execute("SELECT name,role,COALESCE(phone,''),COALESCE(email,'') FROM employees WHERE id=?",(employee_id,)).fetchone() or initial
        dialog=tk.Toplevel(self.root);dialog.title("Edit employee" if editing else "Add employee");dialog.configure(bg=BG);dialog.transient(self.root);dialog.grab_set();dialog.resizable(False,False)
        card=tk.Frame(dialog,bg=WHITE,highlightbackground=BORDER,highlightthickness=1);card.pack(fill="both",expand=True,padx=18,pady=18)
        banner=tk.Frame(card,bg=LIGHT_BLUE);banner.grid(row=0,column=0,columnspan=2,sticky="ew",padx=12,pady=(12,14))
        tk.Label(banner,text="Employee profile",bg=LIGHT_BLUE,fg=BLUE,font=("Segoe UI",16,"bold")).pack(anchor="w",padx=12,pady=(10,2))
        tk.Label(banner,text="Save contact details and role for your team directory.",bg=LIGHT_BLUE,fg=MUTED,font=("Segoe UI",9)).pack(anchor="w",padx=12,pady=(0,10))
        variables=[]
        for i,(label,value) in enumerate(zip(("Name","Role","Phone","Email"),initial),1):
            tk.Label(card,text=label,bg=WHITE,fg=MUTED,font=("Segoe UI",10,"bold")).grid(row=i,column=0,sticky="w",padx=(20,12),pady=7)
            var=tk.StringVar(value=value or "")
            if label=="Role":
                field=ttk.Combobox(card,textvariable=var,values=("Manager","Sales Staff","Cashier","Inventory Staff","Billing Staff","Other"),font=("Segoe UI",10),width=34)
            else:
                field=tk.Entry(card,textvariable=var,font=("Segoe UI",10),relief="solid",bd=1,width=36)
            field.grid(row=i,column=1,sticky="ew",padx=(0,20),pady=7,ipady=6);variables.append(var)
        def save():
            name,role,phone,email=(v.get().strip() for v in variables)
            if not name:
                messagebox.showwarning("Employee details","Enter an employee name.",parent=dialog);return
            with connect_db() as conn:
                if employee_id:conn.execute("UPDATE employees SET name=?,role=?,phone=?,email=? WHERE id=?",(name,role or "Staff",phone,email,employee_id))
                else:conn.execute("INSERT INTO employees(name,role,phone,email) VALUES (?,?,?,?)",(name,role or "Staff",phone,email))
            dialog.destroy();self.refresh_employee_directory()
            messagebox.showinfo("Saved","Employee details saved.")
        actions=tk.Frame(card,bg=WHITE);actions.grid(row=5,column=0,columnspan=2,sticky="e",padx=20,pady=(12,18))
        tk.Button(actions,text="Cancel",bg=WHITE,fg=MUTED,relief="flat",cursor="hand2",padx=14,pady=8,command=dialog.destroy).pack(side="right",padx=(7,0))
        tk.Button(actions,text="Save changes" if editing else "Add employee",bg=BLUE,fg=WHITE,relief="flat",cursor="hand2",font=("Segoe UI",10,"bold"),padx=16,pady=8,command=save).pack(side="right")
        dialog.update_idletasks()
        x=self.root.winfo_rootx()+max(0,(self.root.winfo_width()-dialog.winfo_reqwidth())//2)
        y=self.root.winfo_rooty()+max(0,(self.root.winfo_height()-dialog.winfo_reqheight())//2)
        dialog.geometry(f"{dialog.winfo_reqwidth()}x{dialog.winfo_reqheight()}+{x}+{y}")

    def delete_employee_record(self):
        if not self.authorize_sensitive_page("Employee edit"):
            return
        selected=self.employee_table.selection()
        if not selected:
            messagebox.showwarning("Select employee","Select an employee row to delete.");return
        employee_id=int(self.employee_table.item(selected[0],"values")[0])
        if not messagebox.askyesno("Delete employee","Delete this employee from the directory?"):return
        with connect_db() as conn:conn.execute("DELETE FROM employees WHERE id=?",(employee_id,))
        self.refresh_employee_directory()

    def show_customers(self):
        self.clear_content()
        if not hasattr(self, "portal_url_var"):
            self.portal_url_var = tk.StringVar(value="Start Customer Form to create a Wi-Fi link.")
        heading = tk.Frame(self.content, bg=BG)
        heading.pack(fill="x", pady=(0, 10))
        tk.Label(heading,text="♧  Customer Directory",bg=BG,fg=DARK,font=("Segoe UI",18,"bold")).pack(side="left")
        tk.Button(heading,text="+ Add customer",bg=GREEN,fg=WHITE,relief="flat",cursor="hand2",
                  font=("Segoe UI",10,"bold"),padx=14,pady=8,command=lambda:self.edit_customer(creating=True)).pack(side="right",padx=(5,0))
        tk.Button(heading,text="Import customers CSV",bg=BLUE,fg=WHITE,relief="flat",cursor="hand2",
                  command=lambda:self.import_records_csv("customers")).pack(side="right")
        row_actions=tk.Frame(self.content,bg=BG)
        row_actions.pack(fill="x",pady=(0,8))
        tk.Button(row_actions,text="✎  Edit selected",bg=LIGHT_BLUE,fg=BLUE,relief="flat",cursor="hand2",
                  font=("Segoe UI",10,"bold"),padx=14,pady=8,command=self.edit_customer).pack(side="left",padx=(0,7))
        tk.Button(row_actions,text="Delete selected",bg="#FEE2E2",fg=RED,relief="flat",cursor="hand2",
                  font=("Segoe UI",10,"bold"),padx=14,pady=8,command=self.delete_customer).pack(side="left")
        tk.Button(row_actions,text="Copy Customer Link",bg=LIGHT_BLUE,fg=BLUE,relief="flat",cursor="hand2",
                  font=("Segoe UI",9,"bold"),padx=12,pady=8,command=self.copy_customer_portal_link).pack(side="right",padx=(5,0))
        tk.Button(row_actions,text="Start Wi-Fi Customer Link",bg=BLUE,fg=WHITE,relief="flat",cursor="hand2",
                  font=("Segoe UI",9,"bold"),padx=12,pady=8,command=self.start_customer_portal).pack(side="right",padx=(5,0))
        self.customer_search_var=tk.StringVar()
        search_card = tk.Frame(self.content, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        search_card.pack(fill="x", pady=(0, 10))
        tk.Label(search_card, text="⌕", bg=WHITE, fg=BLUE, font=("Segoe UI", 17, "bold")).pack(side="left", padx=(10, 3))
        search=tk.Entry(search_card,textvariable=self.customer_search_var,font=("Segoe UI",10),relief="flat",bd=0)
        search.pack(side="left",fill="x",expand=True,ipady=10,padx=5)
        search.bind("<Return>", self.handle_customer_scan)
        tk.Button(search_card, text="▦ Scan", bg=LIGHT_BLUE, fg=DARK, relief="flat", cursor="hand2",
                  font=("Segoe UI", 9, "bold"), padx=10, pady=6,
                  command=search.focus_set).pack(side="left", padx=3, pady=4)
        tk.Button(search_card, text="Search", bg=BLUE, fg=WHITE, relief="flat", cursor="hand2",
                  font=("Segoe UI", 9, "bold"), padx=11, pady=6,
                  command=self.refresh_customer_table).pack(side="left", padx=3, pady=4)
        tk.Button(search_card, text="Clear", bg=WHITE, fg=MUTED, relief="flat", cursor="hand2",
                  command=lambda:self.customer_search_var.set("")).pack(side="left", padx=(3, 10))
        self.customer_search_var.trace_add("write",lambda *_:self.refresh_customer_table())
        columns=("id","name","phone","email","gstin","address","purchases","paid","balance")
        self.customer_table=ttk.Treeview(self.content,columns=columns,show="headings")
        self.add_table_scroll_controls(heading, self.customer_table)
        for col,label,width in (("id","ID",45),("name","CUSTOMER",155),("phone","PHONE",115),("email","EMAIL",165),("gstin","GSTIN / TAX ID",130),("address","ADDRESS",200),("purchases","BILLED",110),("paid","PAID",100),("balance","BALANCE",110)):
            self.customer_table.heading(col,text=label,command=lambda c=col:self.sort_customer_table(c))
            self.customer_table.column(col,width=width,anchor="center")
        self.customer_table.tag_configure("even",background=BG)
        self.customer_table.tag_configure("odd",background=WHITE)
        self.customer_table.pack(fill="both",expand=True)
        self.customer_table.bind("<Double-1>", self.edit_customer)
        self.refresh_customer_table()

    def handle_customer_scan(self, _event=None):
        """A keyboard scanner can find a customer by ID or phone."""
        raw_scan = self.customer_search_var.get().strip()
        scanned = "".join(ch for ch in raw_scan if ch.isdigit())
        if scanned:
            self.customer_search_var.set(scanned)
        self.refresh_customer_table()
        for item in self.customer_table.get_children():
            values = self.customer_table.item(item, "values")
            if values and (str(values[0]) == (scanned or raw_scan) or
                           (scanned and "".join(ch for ch in str(values[2]) if ch.isdigit()) == scanned)):
                self.customer_table.selection_set(item)
                self.customer_table.focus(item)
                self.customer_table.see(item)
                break
        return "break"
    def add_customer(self):
        name = self.customer_name_var.get().strip()
        phone = self.customer_phone_var.get().strip()
        address = self.customer_address_var.get().strip()
        email = self.customer_email_var.get().strip()
        gstin = self.customer_gstin_var.get().strip()
        if not name:
            messagebox.showwarning("Customer details", "Enter the customer name.")
            return
        if len(re.sub(r"\s+", "", gstin)) == 15 and not valid_gstin_format(gstin):
            messagebox.showwarning("GSTIN format", "This does not match the standard 15-character GSTIN format. Check the GSTIN or enter another tax ID.")
            return
        try:
            with connect_db() as conn:
                if phone:
                    conn.execute("""
                        INSERT INTO customers(name, phone, address, email, gstin) VALUES (?, ?, ?, ?, ?)
                        ON CONFLICT(phone) DO UPDATE SET
                            name=excluded.name, address=excluded.address, email=excluded.email, gstin=excluded.gstin
                    """, (name, phone, address, email, gstin))
                else:
                    conn.execute("INSERT INTO customers(name, phone, address, email, gstin) VALUES (?, NULL, ?, ?, ?)", (name, address, email, gstin))
            self.customer_name_var.set("")
            self.customer_phone_var.set("")
            self.customer_address_var.set("")
            self.customer_email_var.set("")
            self.customer_gstin_var.set("")
            self.refresh_customer_table()
            self.refresh_customer_choices()
            messagebox.showinfo("Saved", "Customer saved for future bills.")
        except sqlite3.IntegrityError as exc:
            messagebox.showerror("Could not save", str(exc))

    def sort_customer_table(self,column):
        if not hasattr(self,"customer_table"):return
        col_index=self.customer_table["columns"].index(column)
        rows=[(self.customer_table.set(item,column),item) for item in self.customer_table.get_children("")]
        reverse=getattr(self,"customer_sort_reverse",False)
        rows.sort(key=lambda pair:pair[0].casefold(),reverse=reverse)
        self.customer_sort_reverse=not reverse
        for position,(_,item) in enumerate(rows):self.customer_table.move(item,"",position)

    def select_customer(self, _event=None):
        selected = self.customer_table.selection()
        if not selected:
            return
        cid = int(self.customer_table.item(selected[0], "values")[0])
        with connect_db() as conn:
            row = conn.execute("SELECT name, phone, address, email, gstin FROM customers WHERE id=?", (cid,)).fetchone()
        if row:
            for var, value in zip((self.customer_name_var, self.customer_phone_var, self.customer_address_var, self.customer_email_var, self.customer_gstin_var), row):
                var.set(value or "")

    def delete_customer(self):
        if self.role != "admin":
            messagebox.showerror("Permission denied", "Only an administrator can delete customers.")
            return
        selected = self.customer_table.selection()
        if not selected:
            messagebox.showwarning("Select customer", "Select a customer first.")
            return
        cid = int(self.customer_table.item(selected[0], "values")[0])
        if not messagebox.askyesno("Delete customer", "Delete this customer? Customers with invoices cannot be deleted."):
            return
        with connect_db() as conn:
            used = conn.execute("SELECT 1 FROM bills WHERE customer_id=? LIMIT 1", (cid,)).fetchone()
            if used:
                messagebox.showerror("Customer has billing history", "This customer has invoices, so the record is kept for billing history.")
                return
            conn.execute("DELETE FROM customers WHERE id=?", (cid,))
        self.refresh_customer_table()

    def edit_customer(self, _event=None, creating=False):
        """Open a saveable editor for a customer record."""
        selected=self.customer_table.selection() if hasattr(self,"customer_table") else ()
        if not creating and not selected:
            messagebox.showwarning("Select customer","Select a customer row to edit.")
            return
        customer_id=None if creating else int(self.customer_table.item(selected[0],"values")[0])
        row=("","","","","")
        if customer_id:
            with connect_db() as conn:
                row=conn.execute("SELECT name,COALESCE(phone,''),COALESCE(email,''),COALESCE(gstin,''),COALESCE(address,'') FROM customers WHERE id=?",(customer_id,)).fetchone()
            if not row:
                messagebox.showerror("Customer not found","This customer record may have been removed. Refresh the list and try again.")
                self.refresh_customer_table()
                return
        dialog=tk.Toplevel(self.root)
        dialog.title("Add customer" if creating else "Edit customer")
        dialog.configure(bg=BG)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False,False)
        card=tk.Frame(dialog,bg=WHITE,highlightbackground=BORDER,highlightthickness=1)
        card.pack(fill="both",expand=True,padx=18,pady=18)
        tk.Label(card,text="Customer details",bg=WHITE,fg=DARK,font=("Segoe UI",16,"bold")).grid(row=0,column=0,columnspan=2,sticky="w",padx=20,pady=(18,14))
        fields=("Name","Phone","Email","GSTIN / Tax ID","Address")
        variables=[]
        for index,(label,value) in enumerate(zip(fields,row),start=1):
            tk.Label(card,text=label,bg=WHITE,fg=MUTED,font=("Segoe UI",10,"bold")).grid(row=index,column=0,sticky="w",padx=(20,12),pady=6)
            var=tk.StringVar(value=value or "")
            entry=tk.Entry(card,textvariable=var,font=("Segoe UI",10),relief="solid",bd=1,width=38)
            entry.grid(row=index,column=1,sticky="ew",padx=(0,20),pady=6,ipady=6)
            variables.append(var)
        card.columnconfigure(1,weight=1)
        actions=tk.Frame(card,bg=WHITE)
        actions.grid(row=len(fields)+1,column=0,columnspan=2,sticky="e",padx=20,pady=(14,20))
        def save_customer():
            name,phone,email,gstin,address=(var.get().strip() for var in variables)
            if not name:
                messagebox.showwarning("Customer details","Enter the customer name.",parent=dialog)
                return
            if len(re.sub(r"\s+","",gstin))==15 and not valid_gstin_format(gstin):
                messagebox.showwarning("GSTIN format","Check the 15-character GSTIN or enter another tax ID.",parent=dialog)
                return
            try:
                with connect_db() as conn:
                    if customer_id:
                        conn.execute("UPDATE customers SET name=?,phone=?,email=?,gstin=?,address=? WHERE id=?",(name,phone or None,email,gstin,address,customer_id))
                    else:
                        conn.execute("INSERT INTO customers(name,phone,email,gstin,address) VALUES (?,?,?,?,?)",(name,phone or None,email,gstin,address))
                dialog.destroy()
                self.refresh_customer_table()
                self.refresh_customer_choices()
                messagebox.showinfo("Saved","Customer details saved.")
            except sqlite3.IntegrityError:
                messagebox.showerror("Phone number already exists","Use a different phone number for this customer.",parent=dialog)
        tk.Button(actions,text="Cancel",bg=WHITE,fg=MUTED,relief="flat",cursor="hand2",padx=14,pady=8,command=dialog.destroy).pack(side="right",padx=(7,0))
        tk.Button(actions,text="Add customer" if creating else "Save changes",bg=BLUE,fg=WHITE,relief="flat",cursor="hand2",font=("Segoe UI",10,"bold"),padx=16,pady=8,command=save_customer).pack(side="right")
        dialog.update_idletasks()
        dialog.geometry(f"{dialog.winfo_reqwidth()}x{dialog.winfo_reqheight()}+{self.root.winfo_rootx()+100}+{self.root.winfo_rooty()+80}")

    def lookup_customer_form_phone(self, *_):
        if getattr(self, "loading_customer_form", False):
            return
        phone = self.customer_phone_var.get().strip()
        if not phone:
            return
        with connect_db() as conn:
            row = conn.execute(
                "SELECT name, address FROM customers WHERE phone=?", (phone,)
            ).fetchone()
        if row:
            self.loading_customer_form = True
            self.customer_name_var.set(row[0])
            self.customer_address_var.set(row[1] or "")
            self.loading_customer_form = False

    def extract_customer_with_ai(self):
        source_text = self.customer_ai_text.get("1.0", "end").strip()
        if not source_text:
            messagebox.showwarning("AI form fill", "Paste customer details first.")
            return
        def worker():
            try:
                details = ai_extract_customer_details(source_text)
                self.root.after(0, lambda: self.apply_ai_customer_details(details))
            except Exception as exc:
                error = str(exc)
                self.root.after(0, lambda: self.finish_ai_customer_error(error))

        # Keep the UI responsive while the AI request runs.
        self.ai_fill_button.configure(state="disabled", text="Reading…")
        threading.Thread(target=worker, daemon=True).start()

    def apply_ai_customer_details(self, details):
        self.customer_name_var.set(details["name"])
        self.customer_phone_var.set(details["phone"])
        self.customer_email_var.set(details["email"])
        self.customer_address_var.set(details["address"])
        self.customer_gstin_var.set(details["gstin"])
        self.ai_fill_button.configure(state="normal", text="Fill with AI")
        messagebox.showinfo("Review details", "AI filled the form. Check the name and phone before saving.")

    def finish_ai_customer_error(self, error):
        self.ai_fill_button.configure(state="normal", text="Fill with AI")
        messagebox.showerror("AI form fill", error)

    def refresh_customer_choices(self):
        if not hasattr(self, "payment_customer_combo"):
            return
        with connect_db() as conn:
            rows = conn.execute("SELECT id, name, COALESCE(phone, '') FROM customers ORDER BY name").fetchall()
        self.customer_choices = {f"{name} — {phone}" if phone else name: cid for cid, name, phone in rows}
        self.payment_customer_combo["values"] = list(self.customer_choices)

    def load_employee_choices(self):
        with connect_db() as conn:
            rows=conn.execute("SELECT id,name,role FROM employees ORDER BY name COLLATE NOCASE").fetchall()
        return {f"{name} · {role}":employee_id for employee_id,name,role in rows}

    def assign_employee_to_invoice(self):
        selected=self.bill_table.selection() if hasattr(self,"bill_table") else ()
        if not selected:
            messagebox.showwarning("Select invoice","Select an invoice from history first.");return
        invoice_id=int(self.bill_table.item(selected[0],"values")[0])
        employee_id=getattr(self,"invoice_employee_choices",{}).get(self.invoice_employee_var.get())
        with connect_db() as conn:conn.execute("UPDATE bills SET employee_id=? WHERE id=?",(employee_id,invoice_id))
        messagebox.showinfo("Invoice updated","Employee assignment saved to this invoice.")

    def show_payment_customer_details(self, _event=None):
        customer_id = getattr(self, "customer_choices", {}).get(self.payment_customer_var.get())
        if not customer_id:
            self.payment_customer_details.configure(text="Select a customer to view billing details.")
            return
        with connect_db() as conn:
            row = conn.execute("SELECT name,COALESCE(phone,''),COALESCE(email,''),COALESCE(address,''),COALESCE(gstin,'') FROM customers WHERE id=?", (customer_id,)).fetchone()
        balance = self.customer_balance(customer_id)
        self.payment_customer_details.configure(text=f"{row[0]}  |  Phone: {row[1]}  |  Email: {row[2]}  |  Address: {row[3]}  |  GSTIN: {row[4]}  |  Outstanding: ₹{balance:,.2f}")

    def refresh_customer_table(self):
        if not hasattr(self, "customer_table") or not self.customer_table.winfo_exists():
            return
        for item in self.customer_table.get_children():
            self.customer_table.delete(item)
        with connect_db() as conn:
            rows = conn.execute("""
            SELECT c.id, c.name, COALESCE(c.phone, ''), COALESCE(c.email, ''), COALESCE(c.gstin, ''), COALESCE(c.address, ''),
                       COALESCE(SUM(b.total), 0), COALESCE(SUM(b.paid), 0)
                FROM customers c LEFT JOIN bills b ON b.customer_id=c.id
                GROUP BY c.id ORDER BY c.name
            """).fetchall()
        search = getattr(self, "customer_search_var", tk.StringVar()).get().lower()
        for cid, name, phone, email, gstin, address, purchases, bill_paid in rows:
            if search and search not in " ".join((str(cid), name, phone, email, gstin, address)).lower():
                continue
            outstanding = self.customer_balance(cid)
            self.customer_table.insert("", "end", values=(cid, name, phone, email, gstin, address, f"₹{purchases:,.2f}", f"₹{bill_paid:,.2f}", f"₹{outstanding:,.2f}"),tags=("even" if len(self.customer_table.get_children())%2==0 else "odd",))

    def record_customer_payment(self):
        key = self.payment_customer_var.get()
        try:
            amount = float(self.payment_amount_var.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid amount", "Enter a payment greater than zero.")
            return
        customer_id = getattr(self, "customer_choices", {}).get(key)
        if not customer_id:
            messagebox.showwarning("Select customer", "Choose a saved customer.")
            return
        if amount > self.customer_balance(customer_id):
            messagebox.showerror("Payment too high", "Payment cannot exceed the outstanding balance.")
            return
        with connect_db() as conn:
            mode = getattr(self, "payment_mode_var", tk.StringVar(value="Cash")).get()
            employee_id=getattr(self,"payment_employee_choices",{}).get(getattr(self,"payment_employee_var",tk.StringVar()).get())
            remaining = amount
            invoices = conn.execute("SELECT id,total,paid FROM bills WHERE customer_id=? AND paid<total ORDER BY due_date,id", (customer_id,)).fetchall()
            for invoice_id, total, paid in invoices:
                if remaining <= 0:
                    break
                applied = min(remaining, total-paid)
                updated_paid = paid + applied
                status = "paid" if updated_paid >= total else "partial"
                conn.execute("UPDATE bills SET paid=?,status=? WHERE id=?", (updated_paid,status,invoice_id))
                conn.execute("INSERT INTO business_payments(bill_id,customer_id,amount,payment_mode,employee_id) VALUES (?,?,?,?,?)", (invoice_id,customer_id,applied,mode,employee_id))
                remaining -= applied
        self.payment_amount_var.set("")
        self.refresh_customer_table()
        if hasattr(self, "payment_history_table"):
            self.refresh_payment_history()
        messagebox.showinfo("Payment recorded", "Customer payment has been added to their account.")

    def show_payments(self):
        self.clear_content()
        tk.Label(self.content, text="◉  Payments", bg=BG, fg=DARK, font=("Segoe UI", 20, "bold")).pack(anchor="w")
        tk.Label(self.content, text="Record collections, check customer balances, and review online receipts.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(2, 12))
        payment_search = tk.Frame(self.content, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        payment_search.pack(fill="x", pady=(0, 10))
        tk.Label(payment_search, text="⌕", bg=WHITE, fg=BLUE, font=("Segoe UI", 17, "bold")).pack(side="left", padx=(10, 3))
        self.payment_search_var = tk.StringVar()
        payment_search_entry = tk.Entry(payment_search, textvariable=self.payment_search_var,
                font=("Segoe UI", 10), relief="flat", bd=0)
        payment_search_entry.pack(side="left", fill="x", expand=True, ipady=9, padx=5)
        payment_search_entry.bind("<Return>", self.handle_payment_scan)
        tk.Button(payment_search, text="▦ Scan", bg=LIGHT_BLUE, fg=DARK, relief="flat", cursor="hand2",
                  font=("Segoe UI", 9, "bold"), padx=10, pady=6,
                  command=payment_search_entry.focus_set).pack(side="left", padx=3, pady=4)
        tk.Button(payment_search, text="Search", bg=BLUE, fg=WHITE, relief="flat", cursor="hand2",
                  font=("Segoe UI", 9, "bold"), padx=11, pady=6,
                  command=self.refresh_payment_tables).pack(side="left", padx=3, pady=4)
        tk.Button(payment_search, text="Clear", bg=WHITE, fg=MUTED, relief="flat", cursor="hand2",
                  command=lambda: self.payment_search_var.set("")).pack(side="left", padx=(3, 10))
        self.payment_search_var.trace_add("write", lambda *_: self.refresh_payment_tables())

        top = tk.Frame(self.content, bg=BG)
        top.pack(fill="x", pady=(0, 12))
        card = tk.Frame(top, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        card.pack(side="left", fill="both", expand=True, padx=(0, 6))
        details_card = tk.Frame(top, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        details_card.pack(side="left", fill="both", expand=True, padx=(6, 0))
        tk.Label(card, text="Record a customer payment", bg=WHITE, fg=DARK,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16, pady=(13, 8))
        form = tk.Frame(card, bg=WHITE)
        form.pack(fill="x", padx=15, pady=(0, 14))
        self.payment_customer_var = tk.StringVar()
        self.payment_customer_combo = ttk.Combobox(form, textvariable=self.payment_customer_var, state="readonly", width=25)
        self.payment_customer_combo.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=4)
        self.payment_customer_combo.bind("<<ComboboxSelected>>", self.show_payment_customer_details)
        tk.Label(form, text="Customer", bg=WHITE, fg=MUTED, font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(form, text="Amount", bg=WHITE, fg=MUTED, font=("Segoe UI", 9, "bold")).grid(row=0, column=1, sticky="w")
        self.payment_amount_var = tk.StringVar()
        tk.Entry(form, textvariable=self.payment_amount_var, width=13, relief="solid", bd=1).grid(row=1, column=1, sticky="ew", padx=4, pady=4, ipady=5)
        tk.Label(form, text="Payment mode", bg=WHITE, fg=MUTED, font=("Segoe UI", 9, "bold")).grid(row=2, column=0, sticky="w", pady=(5, 0))
        self.payment_mode_var = tk.StringVar(value="Cash")
        ttk.Combobox(form, textvariable=self.payment_mode_var, values=("Cash", "Card", "UPI", "Bank transfer"), state="readonly", width=20).grid(row=3, column=0, sticky="ew", padx=(0, 8), pady=4)
        tk.Label(form,text="Handled by",bg=WHITE,fg=MUTED,font=("Segoe UI",9,"bold")).grid(row=4,column=0,sticky="w",pady=(5,0))
        self.payment_employee_var=tk.StringVar(value="")
        self.payment_employee_combo=ttk.Combobox(form,textvariable=self.payment_employee_var,state="readonly",width=25)
        self.payment_employee_combo.grid(row=5,column=0,sticky="ew",padx=(0,8),pady=4)
        self.payment_employee_choices=self.load_employee_choices()
        self.payment_employee_combo["values"]=[""]+list(self.payment_employee_choices)
        tk.Button(form, text="＋  Record Payment", bg=GREEN, fg=WHITE, relief="flat", cursor="hand2",
                  font=("Segoe UI", 9, "bold"), padx=12, pady=7,
                  command=self.record_customer_payment).grid(row=5, column=1, sticky="ew", padx=4, pady=4)
        form.columnconfigure(0, weight=3); form.columnconfigure(1, weight=2)
        self.refresh_customer_choices()

        tk.Label(details_card, text="Customer balance", bg=WHITE, fg=DARK,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16, pady=(13, 8))
        tk.Frame(details_card, bg=GREEN, height=3).pack(fill="x", padx=16, pady=(0, 9))
        self.payment_customer_details = tk.Label(details_card, text="Select a customer to see their balance and open bills.",
                bg=WHITE, fg=MUTED, anchor="nw", justify="left", wraplength=470,
                font=("Segoe UI", 10), padx=4, pady=4)
        self.payment_customer_details.pack(fill="both", expand=True, padx=14, pady=(0, 12))

        lists = tk.Frame(self.content, bg=BG)
        lists.pack(fill="both", expand=True)
        history_card = tk.Frame(lists, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        history_card.pack(side="left", fill="both", expand=True, padx=(0, 6))
        requests_card = tk.Frame(lists, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        requests_card.pack(side="left", fill="both", expand=True, padx=(6, 0))

        def section_heading(parent, title, table_getter):
            heading = tk.Frame(parent, bg=WHITE)
            heading.pack(fill="x", padx=12, pady=(10, 6))
            tk.Label(heading, text=title, bg=WHITE, fg=DARK, font=("Segoe UI", 12, "bold")).pack(side="left")
            controls = tk.Frame(heading, bg=WHITE)
            controls.pack(side="right")
            table_getter_ref = table_getter
            for glyph, direction in (("↑", -4), ("↓", 4)):
                tk.Button(controls, text=glyph, width=3, bg=LIGHT_BLUE, fg=DARK, relief="flat", cursor="hand2",
                          font=("Segoe UI", 10, "bold"), command=lambda step=direction, get=table_getter_ref: get().yview_scroll(step, "units")).pack(side="left", padx=2)

        section_heading(history_card, "Payment history", lambda: self.payment_history_table)
        columns = ("date", "customer", "phone", "source", "amount", "note", "employee")
        self.payment_history_table = ttk.Treeview(history_card, columns=columns, show="headings", height=8)
        for col, title, width in (
            ("date", "DATE", 110), ("customer", "CUSTOMER", 135),
            ("phone", "PHONE", 100), ("source", "TYPE", 105),
            ("amount", "AMOUNT", 100), ("note", "DETAIL", 120), ("employee", "HANDLED BY", 125),
        ):
            self.payment_history_table.heading(col, text=title)
            self.payment_history_table.column(col, width=width, anchor="center")
        self.payment_history_table.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.refresh_payment_history()

        section_heading(requests_card, "Online payment receipts", lambda: self.payment_requests_table)
        tk.Label(requests_card, text="AI extracted details · verify a receipt before recording it", bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 8)).pack(anchor="w", padx=13, pady=(0, 5))
        request_columns = ("date", "customer", "phone", "payer", "amount", "paid_at", "reference", "status", "ai_note")
        request_table_area = tk.Frame(requests_card, bg=WHITE)
        request_table_area.pack(fill="both", expand=True, padx=10)
        self.payment_requests_table = ttk.Treeview(request_table_area, columns=request_columns, show="headings", height=8)
        for col, label in (("date","SUBMITTED"),("customer","CUSTOMER"),("phone","PHONE"),("payer","PAYER"),("amount","AMOUNT"),("paid_at","PAID DATE"),("reference","REFERENCE"),("status","STATUS"),("ai_note","AI NOTE")):
            self.payment_requests_table.heading(col, text=label)
            self.payment_requests_table.column(col, width=95 if col not in ("payer", "reference", "ai_note") else 110, anchor="center", stretch=False)
        request_xscroll = ttk.Scrollbar(request_table_area, orient="horizontal", command=self.payment_requests_table.xview)
        self.payment_requests_table.configure(xscrollcommand=request_xscroll.set)
        self.payment_requests_table.pack(fill="both", expand=True)
        request_xscroll.pack(fill="x")
        receipt_actions = tk.Frame(requests_card, bg=WHITE)
        receipt_actions.pack(fill="x", padx=10, pady=9)
        tk.Button(receipt_actions,text="Import receipt image / PDF",bg=LIGHT_BLUE,fg=DARK,relief="flat",cursor="hand2",
                  command=self.import_payment_receipt).pack(side="left",padx=(0,5))
        tk.Button(receipt_actions, text="View receipt", bg=LIGHT_BLUE, fg=DARK, relief="flat", cursor="hand2",
                  command=self.open_payment_request_receipt).pack(side="left")
        tk.Button(receipt_actions, text="Verify & record", bg=GREEN, fg=WHITE, relief="flat", cursor="hand2",
                  command=self.verify_payment_request).pack(side="right")
        self.refresh_payment_requests()

    def import_payment_receipt(self):
        path=filedialog.askopenfilename(title="Choose payment receipt",filetypes=(("Receipt image or PDF","*.png *.jpg *.jpeg *.webp *.pdf"),))
        if not path:return
        try:
            with open(path,"rb") as source:file_bytes=source.read(8*1024*1024+1)
            if len(file_bytes)>8*1024*1024:raise ValueError("Choose a file smaller than 8 MB.")
            ext=os.path.splitext(path)[1].lower()
            mime={".png":"image/png",".jpg":"image/jpeg",".jpeg":"image/jpeg",".webp":"image/webp",".pdf":"application/pdf"}.get(ext)
            if not mime:raise ValueError("Choose PNG, JPG, WEBP, or PDF.")
        except Exception as exc:
            messagebox.showerror("Receipt file",str(exc));return
        messagebox.showinfo("Reading receipt","AI will extract visible payment details. Nothing is posted to accounts until you review and verify it.")
        def worker():
            try:
                details=extract_payment_receipt_upload(file_bytes,mime)
                self.root.after(0,lambda:self.save_imported_payment_receipt(details,file_bytes,mime))
            except Exception as exc:
                error=str(exc);self.root.after(0,lambda:messagebox.showerror("Receipt scan",error))
        threading.Thread(target=worker,daemon=True).start()

    def save_imported_payment_receipt(self,details,file_bytes,mime):
        from tkinter import simpledialog
        try:amount=float(details.get("amount") or 0)
        except (TypeError,ValueError):amount=0
        if amount<=0:
            messagebox.showwarning("Amount not found","No valid amount was read. Check the receipt manually; it was not recorded.");return
        payer=str(details.get("payer_name") or "").strip()
        phone=""
        if payer:
            with connect_db() as conn:
                found=conn.execute("SELECT phone FROM customers WHERE name=? COLLATE NOCASE ORDER BY id DESC LIMIT 1",(payer,)).fetchone()
            phone=(found[0] if found else "") or ""
        name=payer or simpledialog.askstring("Receipt customer","Enter the customer name to identify this payment:",parent=self.root)
        if name is None:return
        if not phone:phone=simpledialog.askstring("Customer phone","Enter the customer phone number (or type Unknown):",parent=self.root) or "Unknown"
        reference=str(details.get("reference") or "").strip()
        paid_at=str(details.get("paid_at") or "").strip()
        note=f"AI extracted; verify receipt before recording. Payee: {details.get('payee_name') or 'not read'}"
        with connect_db() as conn:
            conn.execute("INSERT INTO payment_requests(customer_name,phone,amount,payment_mode,reference,payer_name,paid_at,ai_note,receipt_blob,receipt_mime) VALUES (?,?,?,?,?,?,?,?,?,?)",(name.strip(),phone.strip(),amount,"UPI",reference,payer,paid_at,note,sqlite3.Binary(file_bytes),mime))
        self.refresh_payment_requests()
        messagebox.showinfo("Receipt queued",f"Extracted ₹{amount:,.2f}. It is saved as Pending and must be checked before it changes any balance.")

    def refresh_payment_tables(self):
        self.refresh_payment_history()
        self.refresh_payment_requests()

    def handle_payment_scan(self, _event=None):
        # Payment references, employee phone numbers, and customer names can be scanned or typed.
        self.refresh_payment_tables()
        return "break"

    def open_payment_request_receipt(self):
        selected = self.payment_requests_table.selection() if hasattr(self, "payment_requests_table") else ()
        if not selected:
            messagebox.showwarning("Select receipt", "Select a payment request first.")
            return
        request_id = int(selected[0])
        with connect_db() as conn:
            row = conn.execute("SELECT receipt_blob,receipt_mime FROM payment_requests WHERE id=?", (request_id,)).fetchone()
        if not row or not row[0]:
            messagebox.showerror("Receipt unavailable", "This payment request has no saved receipt image.")
            return
        extension = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "application/pdf": ".pdf"}.get(row[1], ".img")
        path = os.path.join(tempfile.gettempdir(), f"billease_receipt_{request_id}{extension}")
        try:
            with open(path, "wb") as receipt_file:
                receipt_file.write(row[0])
            os.startfile(path)
        except (AttributeError, OSError) as exc:
            messagebox.showerror("Could not open receipt", str(exc))

    def verify_payment_request(self):
        if not self.request_security_pin("verify a payment receipt"):
            return
        selected = self.payment_requests_table.selection() if hasattr(self, "payment_requests_table") else ()
        if not selected:
            messagebox.showwarning("Select receipt", "Select a receipt from the list first.")
            return
        request_id = int(selected[0])
        with connect_db() as conn:
            request = conn.execute("SELECT customer_name,phone,amount,reference,status FROM payment_requests WHERE id=?", (request_id,)).fetchone()
            if not request:
                messagebox.showerror("Receipt not found", "Refresh the Payments page and select the receipt again.")
                return
            name, phone, amount, reference, status = request
            if status != "Pending":
                messagebox.showinfo("Already reviewed", f"This receipt is already marked {status.lower()}.")
                return
            if not messagebox.askyesno("Verify payment", f"Confirm that the receipt is genuine and ₹{amount:,.2f} was received from {name}?"):
                return
            customer = conn.execute("SELECT id FROM customers WHERE phone=?", (phone,)).fetchone()
            if customer:
                customer_id = customer[0]
            else:
                cursor = conn.execute("INSERT INTO customers(name,phone) VALUES (?,?)", (name, phone))
                customer_id = cursor.lastrowid

            remaining = float(amount)
            invoices = conn.execute("SELECT id,total,paid FROM bills WHERE customer_id=? AND paid<total ORDER BY due_date,id", (customer_id,)).fetchall()
            for invoice_id, total, paid in invoices:
                if remaining <= 0:
                    break
                applied = min(remaining, total - paid)
                new_paid = paid + applied
                invoice_status = "paid" if new_paid >= total else "partial"
                conn.execute("UPDATE bills SET paid=?,status=? WHERE id=?", (new_paid, invoice_status, invoice_id))
                conn.execute("INSERT INTO business_payments(bill_id,customer_id,amount,payment_mode, payment_date) VALUES (?,?,?,?,COALESCE((SELECT paid_at FROM payment_requests WHERE id=? AND paid_at<>''),CURRENT_TIMESTAMP))", (invoice_id, customer_id, applied, "UPI", request_id))
                remaining -= applied
            if remaining > 0:
                note = f"UPI receipt {reference}".strip()
                conn.execute("INSERT INTO customer_payments(customer_id,amount,payment_mode,note,payment_date) VALUES (?,?,?,?,COALESCE((SELECT paid_at FROM payment_requests WHERE id=? AND paid_at<>''),CURRENT_TIMESTAMP))", (customer_id, remaining, "UPI", note, request_id))
            conn.execute("UPDATE payment_requests SET status='Verified' WHERE id=? AND status='Pending'", (request_id,))
        self.refresh_payment_requests()
        self.refresh_customer_choices()
        self.refresh_payment_history()
        messagebox.showinfo("Payment recorded", f"Verified ₹{amount:,.2f} from {name} and added it to Payments.")

    def refresh_payment_requests(self):
        if not hasattr(self,"payment_requests_table") or not self.payment_requests_table.winfo_exists():
            return
        for item in self.payment_requests_table.get_children():self.payment_requests_table.delete(item)
        with connect_db() as conn:
            rows=conn.execute("SELECT id,submitted_at,customer_name,phone,payer_name,amount,paid_at,reference,status,ai_note FROM payment_requests ORDER BY id DESC LIMIT 100").fetchall()
        search = getattr(self, "payment_search_var", tk.StringVar()).get().strip().casefold()
        for row in rows:
            if search and search not in " ".join(str(value or "") for value in row).casefold():
                continue
            self.payment_requests_table.insert("","end",iid=str(row[0]),values=(row[1],row[2],row[3],row[4],f"₹{row[5]:,.2f}",row[6],row[7],row[8],row[9]))

    def refresh_payment_history(self):
        if not hasattr(self, "payment_history_table") or not self.payment_history_table.winfo_exists():
            return
        for item in self.payment_history_table.get_children():
            self.payment_history_table.delete(item)
        with connect_db() as conn:
            rows = conn.execute("""
                SELECT payment_date, name, phone, source, amount, note, employee FROM (
                    SELECT p.payment_date, c.name, COALESCE(c.phone, '') AS phone,
                           'Invoice payment' AS source, p.amount,
                           COALESCE(b.invoice_no,'INV-'||b.id) AS note, COALESCE(e.name,'—') AS employee
                    FROM business_payments p JOIN bills b ON b.id=p.bill_id JOIN customers c ON c.id=p.customer_id
                    LEFT JOIN employees e ON e.id=p.employee_id
                    UNION ALL
                    SELECT p.payment_date, c.name, COALESCE(c.phone, ''),
                           'Account payment', p.amount, p.note, '—'
                    FROM customer_payments p JOIN customers c ON c.id=p.customer_id
                ) ORDER BY payment_date DESC
            """).fetchall()
        search = getattr(self, "payment_search_var", tk.StringVar()).get().strip().casefold()
        for date, customer, phone, source, amount, note, employee in rows:
            if search and search not in " ".join(str(value or "") for value in (date, customer, phone, source, amount, note, employee)).casefold():
                continue
            self.payment_history_table.insert(
                "", "end",
                values=(date, customer, phone, source, f"₹{amount:,.2f}", note, employee)
            )

    def show_bills(self):
        self.clear_content()
        card=tk.Frame(self.content,bg=WHITE,highlightbackground=BORDER,highlightthickness=1)
        card.pack(fill="x",pady=(0,10))
        tk.Label(card,text="▧  Find an invoice and choose its design",bg=WHITE,fg=DARK,font=("Segoe UI",14,"bold")).pack(anchor="w",padx=15,pady=(10,5))
        tk.Label(card,text="Invoices are saved automatically to your local SQLite database and appear in Invoice History.",bg=WHITE,fg=MUTED,font=("Segoe UI",9)).pack(anchor="w",padx=15,pady=(0,8))
        with connect_db() as conn:
            invoice_settings = dict(conn.execute("SELECT key,value FROM app_settings WHERE key IN ('invoice_template','template_font','template_font_size','template_primary')"))
        self.invoice_template_var = tk.StringVar(value=invoice_settings.get("invoice_template", "Classic"))
        self.invoice_font_var = tk.StringVar(value=invoice_settings.get("template_font", "Helvetica"))
        self.invoice_font_size_var = tk.StringVar(value=invoice_settings.get("template_font_size", "10"))
        self.invoice_accent_var = tk.StringVar(value=invoice_settings.get("template_primary", BLUE))
        tk.Label(card,text="Choose a design",bg=WHITE,fg=DARK,font=("Segoe UI",10,"bold")).pack(anchor="w",padx=14,pady=(4,2))
        template_row=tk.Frame(card,bg=WHITE)
        template_row.pack(fill="x",padx=10,pady=(0,6))
        self.invoice_template_cards={}
        for template_name in ("Classic", "Modern", "Minimal", "Corporate", "Elegant"):
            template_card=tk.Frame(template_row,bg=WHITE,highlightthickness=2)
            template_card.pack(side="left",fill="x",expand=True,padx=4)
            preview=tk.Canvas(template_card,width=130,height=48,bg=BG,highlightthickness=0)
            preview.pack(padx=5,pady=(5,0))
            self.invoice_template_cards[template_name]=(template_card,preview)
            preview.bind("<Button-1>",lambda _event,name=template_name:self.select_invoice_template(name))
            tk.Button(template_card,text=template_name,relief="flat",bg=WHITE,fg=DARK,font=("Segoe UI",9,"bold"),command=lambda name=template_name:self.select_invoice_template(name)).pack(fill="x",padx=3,pady=(0,4))
        controls=tk.Frame(card,bg=WHITE)
        controls.pack(fill="x",padx=14,pady=(0,8))
        tk.Label(controls,text="Font",bg=WHITE,fg=MUTED).pack(side="left")
        ttk.Combobox(controls,textvariable=self.invoice_font_var,values=("Helvetica","Times","Courier"),state="readonly",width=13).pack(side="left",padx=(5,14))
        tk.Label(controls,text="Size",bg=WHITE,fg=MUTED).pack(side="left")
        ttk.Combobox(controls,textvariable=self.invoice_font_size_var,values=("8","9","10","11","12"),state="readonly",width=5).pack(side="left",padx=5)
        tk.Button(controls,text="Choose accent color",command=self.choose_invoice_accent).pack(side="left",padx=(12,5))
        self.invoice_accent_swatch=tk.Label(controls,textvariable=self.invoice_accent_var,bg=WHITE,fg=BLUE,font=("Segoe UI",9,"bold"))
        self.invoice_accent_swatch.pack(side="left",padx=5)
        self.refresh_invoice_template_preview()
        lookup=tk.Frame(card,bg=LIGHT_BLUE)
        lookup.pack(fill="x",padx=14,pady=(2,9))
        tk.Label(lookup,text="Invoice ID, invoice number, or customer phone",bg=LIGHT_BLUE,fg=MUTED).pack(side="left",padx=(8,5),pady=8)
        self.invoice_lookup_var=tk.StringVar()
        self.bill_search_var=self.invoice_lookup_var
        invoice_lookup_entry=tk.Entry(lookup,textvariable=self.invoice_lookup_var,width=34,font=("Segoe UI",10),relief="solid",bd=1)
        invoice_lookup_entry.pack(side="left",padx=4,ipady=5)
        invoice_lookup_entry.bind("<Return>",lambda _event:self.generate_invoice_pdf())
        self.invoice_lookup_var.trace_add("write",lambda *_:self.refresh_bill_table())
        tk.Button(lookup,text="▦ Scan",bg=LIGHT_BLUE,fg=DARK,relief="flat",cursor="hand2",
                  command=invoice_lookup_entry.focus_set).pack(side="left",padx=3,pady=4)
        tk.Button(lookup,text="Search",bg=BLUE,fg=WHITE,relief="flat",cursor="hand2",
                  command=self.refresh_bill_table).pack(side="left",padx=3,pady=4)
        tk.Button(lookup,text="Clear",relief="flat",command=lambda:self.invoice_lookup_var.set("")).pack(side="left",padx=5)
        tk.Button(lookup,text="Generate PDF",bg=GREEN,fg=WHITE,relief="flat",command=self.generate_invoice_pdf).pack(side="right",padx=8,pady=5)
        history_heading = tk.Frame(self.content, bg=BG)
        history_heading.pack(fill="x", pady=(4, 5))
        tk.Label(history_heading, text="▤  Invoice History", bg=BG, fg=DARK, font=("Segoe UI", 13, "bold")).pack(side="left")
        cols = ("id", "number", "date", "due_date", "customer", "phone", "status", "total", "paid", "balance")
        self.bill_table = ttk.Treeview(self.content, columns=cols, show="headings")
        self.add_table_scroll_controls(history_heading, self.bill_table)
        for col, label, width in (("id","ID",55),("number","INVOICE NUMBER",145),("date","INVOICE DATE",125),("due_date","DUE DATE",105),("customer","CUSTOMER",150),("phone","PHONE",120),("status","STATUS",95),("total","TOTAL",95),("paid","PAID",95),("balance","BALANCE",95)):
            self.bill_table.heading(col, text=label)
            self.bill_table.column(col, width=width, anchor="center")
        self.bill_table.tag_configure("even",background=BG)
        self.bill_table.tag_configure("odd",background=WHITE)
        self.bill_table.pack(fill="both", expand=True)
        self.bill_table.bind("<Double-1>",self.show_invoice_history_details)
        tk.Label(self.content,text="Double-click an invoice row to view its item and payment details.",bg=BG,fg=MUTED,font=("Segoe UI",9)).pack(anchor="w",pady=(4,0))
        tk.Button(self.content, text="Save selected invoice as PDF / Print", bg=BLUE, fg=WHITE, relief="flat", command=self.export_invoice_pdf).pack(anchor="e", pady=7)
        staff_assignment=tk.Frame(self.content,bg=WHITE,highlightbackground=BORDER,highlightthickness=1)
        staff_assignment.pack(fill="x",pady=(0,6))
        tk.Label(staff_assignment,text="Handled by",bg=WHITE,fg=MUTED,font=("Segoe UI",9,"bold")).pack(side="left",padx=(10,5),pady=6)
        self.invoice_employee_var=tk.StringVar()
        self.invoice_employee_choices=self.load_employee_choices()
        self.invoice_employee_combo=ttk.Combobox(staff_assignment,textvariable=self.invoice_employee_var,values=[""]+list(self.invoice_employee_choices),state="readonly",width=32)
        self.invoice_employee_combo.pack(side="left",padx=4,pady=6)
        tk.Button(staff_assignment,text="Assign to selected invoice",bg=LIGHT_BLUE,fg=BLUE,relief="flat",cursor="hand2",command=self.assign_employee_to_invoice).pack(side="left",padx=8,pady=5)
        invoice_actions = tk.Frame(self.content, bg=BG)
        invoice_actions.pack(fill="x", pady=(0, 6))
        tk.Button(invoice_actions,text="Email invoice",bg=LIGHT_BLUE,fg=DARK,relief="flat",command=self.send_selected_invoice_email).pack(side="left",padx=4)
        tk.Button(invoice_actions,text="Email payment reminder",bg=LIGHT_BLUE,fg=DARK,relief="flat",command=self.send_selected_payment_reminder).pack(side="left",padx=4)
        tk.Button(invoice_actions,text="Delivery history",bg=LIGHT_BLUE,fg=DARK,relief="flat",command=self.show_invoice_delivery_history).pack(side="left",padx=4)
        tk.Button(invoice_actions,text="Create online payment link",bg=GREEN,fg=WHITE,relief="flat",command=self.create_invoice_payment_link).pack(side="left",padx=4)
        tk.Button(invoice_actions,text="Sync payment status",bg=LIGHT_BLUE,fg=DARK,relief="flat",command=self.sync_selected_payment_link).pack(side="left",padx=4)
        tk.Button(invoice_actions, text="Edit invoice due date", command=self.edit_invoice).pack(side="left", padx=4)
        if self.role == "admin":
            tk.Button(invoice_actions, text="Delete invoice", bg=RED, fg=WHITE, relief="flat", command=self.delete_invoice).pack(side="left", padx=4)
        self.refresh_bill_table()

    def fill_invoice_lookup_from_history(self,_event=None):
        selected=self.bill_table.selection() if hasattr(self,"bill_table") else ()
        if selected and hasattr(self,"invoice_lookup_var"):
            values=self.bill_table.item(selected[0],"values")
            self.invoice_lookup_var.set(values[1] or values[0])

    def show_invoice_history_details(self,_event=None):
        selected=self.bill_table.selection() if hasattr(self,"bill_table") else ()
        if not selected:
            return
        bill_id=int(self.bill_table.item(selected[0],"values")[0])
        with connect_db() as conn:
            bill=conn.execute("SELECT COALESCE(b.invoice_no,'INV-'||b.id),b.bill_date,b.due_date,c.name,c.phone,b.subtotal,b.discount,b.tax_total,b.total,b.paid,COALESCE(e.name,'Unassigned') FROM bills b JOIN customers c ON c.id=b.customer_id LEFT JOIN employees e ON e.id=b.employee_id WHERE b.id=?",(bill_id,)).fetchone()
            items=conn.execute("SELECT l.description,COALESCE(p.sku,''),COALESCE(p.category,''),l.quantity,l.unit,l.rate,l.discount,l.tax_rate,l.tax_amount,l.line_total FROM invoice_lines l LEFT JOIN products p ON p.id=l.product_id WHERE l.bill_id=? ORDER BY l.id",(bill_id,)).fetchall()
        if not bill:
            messagebox.showerror("Invoice not found","This invoice could not be found.")
            return
        window=tk.Toplevel(self.root)
        window.title(f"Invoice details · {bill[0]}")
        window.geometry("1180x520")
        window.configure(bg=BG)
        tk.Label(window,text=f"Invoice {bill[0]}",bg=BG,fg=DARK,font=("Segoe UI",17,"bold")).pack(anchor="w",padx=18,pady=(16,8))
        tk.Label(window,text=f"Customer: {bill[3]}  ·  Phone: {bill[4] or '—'}  ·  Date: {bill[1]}  ·  Due: {bill[2] or '—'}  ·  Handled by: {bill[10]}",bg=BG,fg=MUTED,font=("Segoe UI",10)).pack(anchor="w",padx=18,pady=(0,10))
        item_table=ttk.Treeview(window,columns=("item","sku","category","quantity","rate","discount","tax_rate","tax","total"),show="headings",height=11)
        for col,title,width in (("item","PRODUCT / SERVICE",175),("sku","SKU / CODE",90),("category","CATEGORY",105),("quantity","QUANTITY",90),("rate","UNIT PRICE",90),("discount","DISCOUNT",90),("tax_rate","TAX %",65),("tax","TAX AMOUNT",95),("total","LINE TOTAL",105)):
            item_table.heading(col,text=title);item_table.column(col,width=width,anchor="center")
        item_table.pack(fill="both",expand=True,padx=18,pady=5)
        for item in items:
            item_table.insert("","end",values=(item[0],item[1],item[2],f"{item[3]:g} {item[4]}",f"₹{item[5]:,.2f}",f"₹{item[6]:,.2f}",f"{item[7]:g}%",f"₹{item[8]:,.2f}",f"₹{item[9]:,.2f}"))
        status="Paid" if bill[9]>=bill[8] else ("Overdue" if bill[2] and bill[2]<date.today().isoformat() else ("Partially paid" if bill[9]>0 else "Unpaid"))
        tk.Label(window,text=f"Subtotal ₹{bill[5]:,.2f}   ·   Discount ₹{bill[6]:,.2f}   ·   Tax ₹{bill[7]:,.2f}   ·   Total ₹{bill[8]:,.2f}   ·   Paid ₹{bill[9]:,.2f}   ·   Balance ₹{bill[8]-bill[9]:,.2f}   ·   {status}",bg=BG,fg=DARK,font=("Segoe UI",10,"bold"),wraplength=800,justify="left").pack(anchor="w",padx=18,pady=12)

    def select_invoice_template(self, template_name):
        self.invoice_template_var.set(template_name)
        self.refresh_invoice_template_preview()

    def choose_invoice_accent(self):
        _rgb, color=colorchooser.askcolor(color=self.invoice_accent_var.get(),title="Invoice accent color")
        if color:
            self.invoice_accent_var.set(color.upper())
            self.refresh_invoice_template_preview()

    def refresh_invoice_template_preview(self):
        if not hasattr(self,"invoice_template_cards"):
            return
        accent=self.invoice_accent_var.get() or BLUE
        try:
            self.invoice_accent_swatch.configure(fg=accent)
        except (AttributeError, tk.TclError):
            pass
        for name,(card,canvas) in self.invoice_template_cards.items():
            selected=name==self.invoice_template_var.get()
            try:
                card.configure(highlightbackground=BLUE if selected else BORDER)
                canvas.delete("all")
                if name=="Modern":
                    canvas.create_rectangle(0,0,130,18,fill=accent,outline="")
                    canvas.create_text(8,9,text="BUSINESS",fill=WHITE,anchor="w",font=("Segoe UI",7,"bold"))
                    canvas.create_line(8,28,122,28,fill=BORDER)
                elif name=="Minimal":
                    canvas.create_text(8,10,text="BUSINESS",fill=DARK,anchor="w",font=("Segoe UI",8,"bold"))
                    canvas.create_line(8,17,122,17,fill=accent,width=2)
                    canvas.create_line(8,25,80,25,fill="#D8DFEA")
                elif name=="Corporate":
                    canvas.create_rectangle(0,0,13,48,fill=accent,outline="")
                    canvas.create_text(22,9,text="INVOICE",fill=DARK,anchor="w",font=("Segoe UI",8,"bold"))
                    canvas.create_line(22,18,121,18,fill=accent,width=2)
                elif name=="Elegant":
                    canvas.create_text(65,9,text="Business",fill=DARK,anchor="center",font=("Times New Roman",9,"bold"))
                    canvas.create_line(14,17,116,17,fill=accent)
                    canvas.create_line(25,20,105,20,fill=accent)
                else:
                    canvas.create_text(8,9,text="BUSINESS",fill=DARK,anchor="w",font=("Segoe UI",8,"bold"))
                    canvas.create_line(8,17,122,17,fill=accent,width=2)
                canvas.create_rectangle(8,26,122,46,fill=WHITE,outline=BORDER,width=1)
                canvas.create_rectangle(8,26,122,32,fill=LIGHT_BLUE,outline="")
                for xx in (19,72,91,105):canvas.create_line(xx,26,xx,46,fill=BORDER)
                for yy in (32,39):canvas.create_line(8,yy,122,yy,fill=BORDER)
                for xx,label in ((13,"#"),(44,"PRODUCT"),(81,"SKU"),(98,"QTY"),(113,"TOTAL")):
                    canvas.create_text(xx,29,text=label,fill=DARK,anchor="center",font=("Segoe UI",4,"bold"))
                canvas.create_text(22,35.5,text="Item name",fill=MUTED,anchor="w",font=("Segoe UI",5))
                canvas.create_text(77,35.5,text="A001",fill=MUTED,anchor="w",font=("Segoe UI",5))
                canvas.create_text(98,35.5,text="2",fill=MUTED,anchor="center",font=("Segoe UI",5))
                canvas.create_text(114,35.5,text="₹",fill=MUTED,anchor="center",font=("Segoe UI",5))
                canvas.create_text(22,42.5,text="Product",fill=MUTED,anchor="w",font=("Segoe UI",5))
            except tk.TclError:
                pass

    def edit_invoice(self):
        if self.role != "admin":
            messagebox.showerror("Permission denied", "Only an administrator can edit invoices.")
            return
        if not self.request_security_pin("edit an invoice"):
            return
        selected = self.bill_table.selection()
        if not selected:
            messagebox.showwarning("Select invoice", "Select an invoice first.")
            return
        from tkinter import simpledialog
        invoice_id = int(self.bill_table.item(selected[0], "values")[0])
        with connect_db() as conn:
            old_due, invoice_no = conn.execute("SELECT due_date,invoice_no FROM bills WHERE id=?", (invoice_id,)).fetchone()
        new_due = simpledialog.askstring("Edit invoice", "Due date (YYYY-MM-DD):", initialvalue=old_due or "", parent=self.root)
        if new_due is None:
            return
        try:
            new_due = date.fromisoformat(new_due).isoformat()
        except ValueError:
            messagebox.showerror("Invalid date", "Use YYYY-MM-DD format.")
            return
        with connect_db() as conn:
            conn.execute("UPDATE bills SET due_date=? WHERE id=?", (new_due, invoice_id))
            conn.execute("INSERT INTO audit_log(username,action,invoice_id,detail) VALUES (?,?,?,?)", (self.username,"edited",invoice_id,f"{invoice_no} due date changed to {new_due}"))
        self.refresh_bill_table()

    def delete_invoice(self):
        if self.role != "admin":
            messagebox.showerror("Permission denied", "Only an administrator can delete invoices.")
            return
        if not self.request_security_pin("delete an invoice"):
            return
        selected = self.bill_table.selection()
        if not selected:
            messagebox.showwarning("Select invoice", "Select an invoice first.")
            return
        values = self.bill_table.item(selected[0], "values")
        invoice_id, invoice_no = int(values[0]), values[1]
        if not messagebox.askyesno("Delete invoice", f"Delete {invoice_no}? The deletion will be recorded in audit history."):
            return
        with connect_db() as conn:
            lines = conn.execute("SELECT product_id,quantity FROM invoice_lines WHERE bill_id=?", (invoice_id,)).fetchall()
            for product_id, quantity in lines:
                if product_id:
                    conn.execute("UPDATE products SET stock=stock+? WHERE id=? AND is_service=0", (quantity, product_id))
            conn.execute("INSERT INTO audit_log(username,action,invoice_id,detail) VALUES (?,?,?,?)", (self.username,"deleted",invoice_id,f"Deleted {invoice_no}"))
            conn.execute("DELETE FROM business_payments WHERE bill_id=?", (invoice_id,))
            conn.execute("DELETE FROM invoice_lines WHERE bill_id=?", (invoice_id,))
            conn.execute("DELETE FROM bill_items WHERE bill_id=?", (invoice_id,))
            conn.execute("DELETE FROM bills WHERE id=?", (invoice_id,))
        self.refresh_bill_table()

    def load_bill_choices(self):
        with connect_db() as conn:
            customers = conn.execute("SELECT id, name, COALESCE(phone, ''), COALESCE(email,''), COALESCE(address,''), COALESCE(gstin,'') FROM customers ORDER BY name").fetchall()
            products = conn.execute("SELECT id, name, sku, price, stock, unit, tax_rate, is_service FROM products ORDER BY name").fetchall()
        self.bill_customer_by_phone = {phone: (cid, name, email, address, gstin) for cid, name, phone, email, address, gstin in customers if phone}
        self.bill_product_choices = {}
        for pid, name, sku, price, stock, unit, tax, service in products:
            label = f"{name} | {sku or ''} | ₹{price:.2f}/{unit} | tax {tax:g}%" + (" | service" if service else f" | stock {stock}")
            self.bill_product_choices[label] = (pid, name, price, stock, unit, tax, service)
        self.bill_product_combo["values"] = list(self.bill_product_choices)

    def lookup_bill_customer_phone(self, *_):
        if getattr(self, "loading_bill_customer", False):
            return
        phone = self.bill_customer_phone_var.get().strip()
        if not phone:
            return
        customer = getattr(self, "bill_customer_by_phone", {}).get(phone)
        if customer:
            self.loading_bill_customer = True
            self.bill_customer_name_var.set(customer[1])
            self.bill_customer_email_var.set(customer[2])
            self.bill_customer_address_var.set(customer[3])
            self.bill_customer_gstin_var.set(customer[4])
            self.loading_bill_customer = False

    def add_invoice_line(self):
        product = getattr(self, "bill_product_choices", {}).get(self.bill_product_var.get())
        if not product:
            messagebox.showwarning("Choose item", "Choose a product or service.")
            return
        pid, name, rate, stock, unit, tax_rate, service = product
        try:
            qty = float(self.bill_qty_var.get())
            discount = float(self.bill_item_discount_var.get() or 0)
            if qty <= 0 or discount < 0 or discount > qty * rate:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid line", "Quantity must be positive and discount cannot exceed the line amount.")
            return
        if not service and qty > stock:
            messagebox.showerror("Insufficient stock", f"Only {stock} {unit} are available.")
            return
        taxable = qty * rate - discount
        tax = taxable * tax_rate / 100
        total = taxable + tax
        self.invoice_lines.append((pid, name, qty, rate, discount, tax_rate, tax, total, unit, service))
        self.invoice_line_table.insert("", "end", values=(name, f"{qty:g} {unit}", f"₹{rate:,.2f}", f"₹{discount:,.2f}", f"₹{tax:,.2f}", f"₹{total:,.2f}"))
        self.bill_qty_var.set("1")
        self.bill_item_discount_var.set("0")

    def create_bill(self):
        if not getattr(self, "invoice_lines", []):
            messagebox.showwarning("Invoice items", "Add at least one invoice line.")
            return
        phone = self.bill_customer_phone_var.get().strip()
        customer_name = self.bill_customer_name_var.get().strip()
        customer_email = self.bill_customer_email_var.get().strip()
        customer_address = self.bill_customer_address_var.get().strip()
        customer_gstin = self.bill_customer_gstin_var.get().strip()
        customer = getattr(self, "bill_customer_by_phone", {}).get(phone)
        customer_id = customer[0] if customer else None
        if not customer_id and (not phone or not customer_name):
            messagebox.showwarning("Missing details", "Enter a customer phone and name.")
            return
        if len(re.sub(r"\s+", "", customer_gstin)) == 15 and not valid_gstin_format(customer_gstin):
            messagebox.showwarning("GSTIN format", "This does not match the standard 15-character GSTIN format. Check the GSTIN or enter another tax ID.")
            return
        try:
            paid = float(self.bill_paid_var.get() or 0)
            bill_discount = float(self.bill_discount_var.get() or 0)
            if paid < 0 or bill_discount < 0:
                raise ValueError
            due_text = self.bill_due_date_var.get().strip()
            if due_text:
                due_date = date.fromisoformat(due_text).isoformat()
            else:
                with connect_db() as conn:
                    due_days_setting = conn.execute("SELECT value FROM app_settings WHERE key='invoice_due_days'").fetchone()
                due_days = int(due_days_setting[0]) if due_days_setting and due_days_setting[0].isdigit() else 30
                due_date = (date.today() + timedelta(days=due_days)).isoformat()
        except ValueError:
            messagebox.showerror("Invalid details", "Enter valid non-negative amounts and a YYYY-MM-DD due date.")
            return
        subtotal = sum(line[1] * line[2] for line in self.invoice_lines)
        line_discounts = sum(line[3] for line in self.invoice_lines)
        tax_total = sum(line[4] for line in self.invoice_lines)
        total = max(0, subtotal - line_discounts + tax_total - bill_discount)
        if paid > total or bill_discount > subtotal - line_discounts + tax_total:
            messagebox.showerror("Invalid amount", "Payment or bill discount exceeds the invoice total.")
            return
        with connect_db() as conn:
            cursor = conn.cursor()
            if not customer_id:
                cursor.execute("INSERT INTO customers(name, phone, email, address, gstin) VALUES (?, ?, ?, ?, ?)", (customer_name, phone, customer_email, customer_address, customer_gstin))
                customer_id = cursor.lastrowid
            else:
                cursor.execute("UPDATE customers SET name=?,email=?,address=?,gstin=? WHERE id=?", (customer_name, customer_email, customer_address, customer_gstin, customer_id))
            prefix = conn.execute("SELECT value FROM app_settings WHERE key='invoice_prefix'").fetchone()[0]
            year = date.today().year
            last = conn.execute("SELECT COUNT(*) FROM bills WHERE invoice_no LIKE ?", (f"{prefix}-{year}-%",)).fetchone()[0]
            invoice_no = f"{prefix}-{year}-{last + 1:04d}"
            status = "paid" if paid >= total else ("partial" if paid > 0 else "unpaid")
            template_name=self.invoice_template_var.get()
            template_font=self.invoice_font_var.get()
            template_font_size=int(self.invoice_font_size_var.get())
            template_accent=self.invoice_accent_var.get()
            assigned_employee=getattr(self,"invoice_employee_choices",{}).get(getattr(self,"invoice_employee_var",tk.StringVar()).get())
            cursor.execute("INSERT INTO bills(customer_id, bill_date, due_date, invoice_no, subtotal, discount, tax_total, total, paid, status, template_name, template_font, template_font_size, template_accent, employee_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (customer_id, datetime.now().isoformat(timespec="seconds"), due_date, invoice_no, subtotal, bill_discount + line_discounts, tax_total, total, paid, status, template_name, template_font, template_font_size, template_accent,assigned_employee))
            conn.executemany("INSERT INTO app_settings(key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (("invoice_template",template_name),("template_font",template_font),("template_font_size",str(template_font_size)),("template_primary",template_accent)))
            bill_id = cursor.lastrowid
            conn.execute("INSERT INTO audit_log(username,action,invoice_id,detail) VALUES (?,?,?,?)", (self.username, "created", bill_id, f"Invoice {invoice_no} created"))
            for pid, name, qty, rate, discount, tax_rate, tax, line_total, unit, service in self.invoice_lines:
                cursor.execute("INSERT INTO invoice_lines(bill_id, product_id, description, quantity, unit, rate, discount, tax_rate, tax_amount, line_total) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (bill_id, pid, name, qty, unit, rate, discount, tax_rate, tax, line_total))
                cursor.execute("INSERT INTO bill_items(bill_id, product_id, product_name, quantity, unit_price, line_total) VALUES (?, ?, ?, ?, ?, ?)", (bill_id, pid, name, qty, rate, line_total))
                if not service:
                    cursor.execute("UPDATE products SET stock=stock-? WHERE id=?", (qty, pid))
            if paid > 0:
                cursor.execute("INSERT INTO business_payments(bill_id, customer_id, amount, payment_mode,employee_id) VALUES (?, ?, ?, ?,?)", (bill_id, customer_id, paid, self.bill_paymode_var.get(),assigned_employee))
        self.refresh_bill_table()
        if self.page_title.cget("text") == "Customers":
            self.refresh_customer_table()
        messagebox.showinfo("Invoice saved", f"{invoice_no} saved. Due: ₹{total-paid:,.2f}")
        self.invoice_lines = []
        for item in self.invoice_line_table.get_children():
            self.invoice_line_table.delete(item)
        self.bill_paid_var.set("0")
        self.bill_customer_phone_var.set("")
        self.bill_customer_name_var.set("")
        self.bill_customer_email_var.set("")
        self.bill_customer_address_var.set("")
        self.bill_customer_gstin_var.set("")
        self.load_bill_choices()

    def refresh_bill_table(self):
        if not hasattr(self, "bill_table") or not self.bill_table.winfo_exists():
            return
        for item in self.bill_table.get_children():
            self.bill_table.delete(item)
        with connect_db() as conn:
            rows = conn.execute("""
                SELECT b.id, COALESCE(b.invoice_no, 'INV-' || b.id), b.bill_date, b.due_date, c.name, COALESCE(c.phone,''),
                       CASE WHEN b.paid >= b.total THEN 'paid'
                            WHEN b.due_date < date('now') AND b.paid < b.total THEN 'overdue'
                            WHEN b.paid > 0 THEN 'partial' ELSE 'unpaid' END,
                       b.total, b.paid, b.total-b.paid
                FROM bills b JOIN customers c ON c.id=b.customer_id
                ORDER BY b.id DESC
            """).fetchall()
        search=getattr(self,"bill_search_var",tk.StringVar()).get().strip().casefold()
        for bill_id, number, bill_date, due_date, customer, phone, status, total, paid, due in rows:
            searchable=f"{bill_id} {number} {customer} {phone}".casefold()
            if search and search not in searchable:
                continue
            tag="even" if len(self.bill_table.get_children())%2==0 else "odd"
            self.bill_table.insert("", "end", values=(bill_id, number, bill_date, due_date or "—", customer, phone, status.title(), f"₹{total:,.2f}", f"₹{paid:,.2f}", f"₹{due:,.2f}"),tags=(tag,))
    # ======================================
    # REFRESH DASHBOARD
    # ======================================
    def refresh_dashboard_if_needed(self):

        if self.page_title.cget("text") == "Dashboard":
            self.show_dashboard()


# ==========================================
# START APPLICATION
# ==========================================

if __name__ == "__main__":

    initialize_database()

    root = tk.Tk()
    app = BillEaseApp(root, role="admin", username="owner")
    root.mainloop()
