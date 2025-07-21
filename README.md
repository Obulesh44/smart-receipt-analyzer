
# 🧾 Smart Receipt Analyzer – Full Stack Bill Parser with OCR & Insights

A full-stack intelligent bill parser that extracts and analyzes receipt data using OCR and rule-based logic. It features real-time UI correction, export options, and insightful analytics. Built using **FastAPI** (backend), **Streamlit** (frontend), and **PostgreSQL** (database).

---

## 🚀 Demo

- **Frontend (Streamlit):** http://localhost:8501  
- **Backend API (FastAPI Swagger):** http://localhost:8000/docs

---

## 📦 Features

- 📤 Upload receipts (PDF, JPG, PNG)
- 🧠 Automatic OCR extraction using Tesseract
- 🧾 Fields extracted: Vendor, Amount, Date, Category, Currency
- 🖊️ UI-based manual correction
- 📊 Visual insights by vendor, amount, date, category
- 💾 Export parsed data to CSV / JSON
- 🌐 Multi-language OCR and currency detection
- 🔐 Token-based API authentication

---

## 🧱 Architecture Overview

```
             [User Interface]
                   |
             [Streamlit Frontend]
                   |
             [FastAPI Backend]
       ┌────────────┼────────────┐
 [Tesseract OCR]   [PostgreSQL DB]
```

---

## 🛠️ Tech Stack

| Layer       | Technology                   |
|-------------|------------------------------|
| Frontend    | Streamlit                    |
| Backend     | FastAPI, Pydantic            |
| OCR Engine  | Tesseract OCR                |
| Database    | PostgreSQL, SQLAlchemy       |
| Others      | PIL, pdf2image, dotenv       |

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/smart-receipt-analyzer.git
cd smart-receipt-analyzer
```

### 2. Backend Setup (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env

# Start backend server
uvicorn main:app --reload
```

### 3. Frontend Setup (Streamlit)

```bash
cd ../frontend
pip install -r requirements.txt

# Launch the frontend
streamlit run app.py
```

---

## 🧪 API Reference

Base URL: `http://localhost:8000`

| Method | Endpoint              | Description                  |
|--------|------------------------|------------------------------|
| POST   | `/upload-receipt/`     | Upload and parse receipt     |
| POST   | `/save-corrected/`     | Save user-edited receipt     |
| GET    | `/receipts/search/`    | Filter/search receipts       |
| GET    | `/receipts/summary/`   | Spend analytics & statistics |

Docs available at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📁 Folder Structure

```
smart-receipt-analyzer/
│
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── parser.py
│   ├── utils.py
│   └── ...
│
├── frontend/
│   ├── app.py
│   ├── components/
│   ├── utils.py
│   └── ...
│
├── requirements.txt
├── README.md
└── .env.example
```

---

## 📌 Design Choices

- **FastAPI** enables scalable and well-documented APIs.
- **Streamlit** provides an intuitive and lightweight data dashboard.
- **Tesseract OCR** offers offline support and multi-language compatibility.
- **Rule-based logic** allows fine-grained extraction tailored to receipt formats.
- **PostgreSQL** stores and enables powerful querying for receipt data.

---

## ⚠️ Limitations

- OCR accuracy varies based on image quality and formatting.
- Limited detection for poorly structured or handwritten receipts.
- No authentication UI yet; token-based access only.

---

## 🔮 Planned Features

- [ ] Docker containerization
- [ ] User login & receipt history
- [ ] ML-based category predictions
- [ ] Batch receipt upload
- [ ] Internationalization (UI translations)

---

## 🤝 Contributing

Pull requests and suggestions are welcome. Fork the repository and submit a PR.

---

## 📄 License

This project is licensed under the MIT License.

---

## 👤 Author

**Obulesh Boya**  
📧 obuleshvalmiki417@gmail.com  
🔗 [LinkedIn](https://www.linkedin.com/in/obulesh44/)
