# 🚗 Car Spending Tracker

A full-stack web application for tracking vehicle expenses, maintenance, and fleet analytics. Built with **React** (Vite + Tailwind CSS) and **Python FastAPI**.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.14-blue.svg)
![React](https://img.shields.io/badge/react-18-blue.svg)

## ✨ Features

### 🛡️ Core Functionality
-   **User Authentication**: Secure JWT-based login and registration.
-   **My Garage**: Users can manage their own private fleet of vehicles.
-   **Detailed Car Profiles**: Track VIN, Engine Code, Transmission, Drive Type, Tire Size, and more.
-   **Expense Tracking**: Log Refueling, Services, Insurance, and Inspections.
-   **Favorites**: Pin your most used car to the top of the dashboard.

### 📊 Public Analytics
-   **Landing Page**: Aggregate statistics visible to unauthenticated users.
-   **Charts**:
    -   *Manufacturer Popularity*: Which brands are most common?
    -   *Spending Trends*: Global fuel spending over time.
    -   *Efficiency Leaderboard*: Average cost per kilometer by model.
-   **Privacy**: No personal data or license plates are exposed publicly.

## 🛠️ Tech Stack

### Frontend
-   **React 18** + **Vite**: Fast development and build.
-   **Tailwind CSS (v4)**: Utility-first styling.
-   **Recharts**: Interactive data visualization.
-   **Axios**: API integration.

### Backend
-   **FastAPI**: High-performance Python web framework.
-   **SQLAlchemy**: ORM for SQLite database interaction.
-   **Pydantic**: Data validation and serialization.
-   **Passlib (pbkdf2_sha256)**: Secure password hashing.
-   **Python-Jose**: JWT token handling.
-   **SQLite**: Lightweight, serverless database.

## 🚀 Getting Started

### Prerequisites
-   Python 3.9+
-   Node.js 18+

### 1. Backend Setup

```bash
cd server

# Install dependencies
pip install -r requirements.txt

# Run the server
# The server runs on http://0.0.0.0:8000
python -m uvicorn main:app --reload
```

### 2. Frontend Setup

```bash
cd client

# Install dependencies
npm install

# Run the development server
# The app runs on https://localhost:5173
npm run dev
```

> **Note**: The frontend uses a self-signed certificate for HTTPS. You may need to accept the browser warning when accessing `https://localhost:5173`.

### 3. Data Seeding (Optional)

Populate the database with sample Bulgarian car data (Toyota, BMW, Audi, etc.):

```bash
# From the project root
python seed_data.py
```

This will create:
-   **Users**: `demo@example.com` (password: `password123`)
-   **Cars**: Realistic models with Bulgarian plates (e.g., `CA 1234 TX`).
-   **Logs**: Random refueling and service history.

## 🧪 Usage

1.  Open **https://localhost:5173**.
2.  **Public View**: Check out the analytics charts on the landing page.
3.  **Login**: Use `demo@example.com` / `password123` (if seeded) or register a new account.
4.  **Dashboard**: Add your car, log a refueling, or star your favorite vehicle.

## 📂 Project Structure

```
MyProjects/
├── client/                 # React Frontend
│   ├── src/
│   │   ├── components/     # UI Components (Charts, Forms)
│   │   ├── context/        # Auth Context
│   │   └── ...
│   └── ...
├── server/                 # FastAPI Backend
│   ├── main.py             # App entry point & routes
│   ├── models.py           # Database models
│   ├── schemas.py          # Pydantic Key schemas
│   ├── auth.py             # JWT logic
│   └── ...
└── seed_data.py            # Data population script
```

## 📄 License

This project is open-source and available under the MIT License.
