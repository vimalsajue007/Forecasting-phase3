# ForecastIQ — AI Demand Forecasting Platform

A full-stack AI-powered demand forecasting application with a FastAPI backend and React frontend.

---



##  Backend Setup

### 1. Create & activate virtual environment

```bash
cd backend
python3 -m venv venv
venv\Scripts\activate             # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure MySQL

Create a database:

```sql
CREATE DATABASE demand_forecasting CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```


### 4. Start the server

```bash
uvicorn main:app --reload 
```


---

##  Frontend Setup

### 1. Install dependencies

```bash
cd frontend
npm install
```

### 3. Start dev server

```bash
npm run dev
```


##  Features

| Module | Description |
|---|---|
| **Authentication** | JWT-based register / login / protected routes |
| **Dataset Upload** | CSV/XLSX upload with validation, deduplication, null handling |
| **AI Forecasting** | Linear Regression + Prophet models with train/test split metrics |
| **Dashboard** | Sales trends, accuracy, top products, recent forecasts |
| **Reports** | Excel (openpyxl) and PDF (reportlab) export |
| **Frontend** | Responsive React + Tailwind CSS, light green theme |

---

##  Tech Stack

**Backend:** FastAPI · MySQL · SQLAlchemy · JWT · Pandas · Scikit-learn · Prophet · OpenPyXL · ReportLab

**Frontend:** React 18 · Tailwind CSS · Axios · Recharts · React Router · React Dropzone

---

##  API Endpoints

```
POST   /api/auth/register          Register new user
POST   /api/auth/login             Login → JWT token
GET    /api/auth/me                Current user info

GET    /api/datasets/              List datasets
POST   /api/datasets/upload        Upload CSV/XLSX
GET    /api/datasets/{id}          Get dataset
GET    /api/datasets/{id}/preview  Preview first 10 rows
DELETE /api/datasets/{id}          Delete dataset

POST   /api/forecasts/             Create & run forecast
GET    /api/forecasts/             List forecasts
GET    /api/forecasts/{id}         Get forecast with results
DELETE /api/forecasts/{id}         Delete forecast

GET    /api/dashboard/stats        Dashboard analytics

GET    /api/reports/{id}/excel     Download Excel report
GET    /api/reports/{id}/pdf       Download PDF report
```

---

##  Sample CSV Format

Your dataset should have at minimum:

| date | sales | product |
|------|-------|---------|
| 2024-01-01 | 1200 | ProductA |
| 2024-01-02 | 980  | ProductB |

The date and target (sales) columns are selected when creating a forecast.

---

##  Security

- Passwords hashed with bcrypt
- JWT tokens expire after 30 minutes (configurable)
- All dataset/forecast endpoints require authentication
- CORS restricted to localhost in development

---

##  License

MIT
