# 📦 Supply Chain Analysis

An end-to-end **Supply Chain Analytics project** that uses Machine Learning and Data Visualization to analyze supply chain performance and predict revenue. The project includes a Flask-based interactive dashboard where users can explore insights and generate predictions.

---

## 🚀 Project Overview

Supply Chain Analysis helps businesses understand operational performance, identify trends, optimize inventory decisions, and improve revenue forecasting.

This project uses historical supply chain data to:

- Analyze supply chain performance
- Perform data preprocessing
- Train machine learning models
- Predict revenue outcomes
- Visualize important business insights
- Provide an interactive dashboard using Flask

---

## ✨ Features

### 📊 Analytics Dashboard
- Interactive supply chain insights
- Data visualization
- Performance analysis
- Business metrics overview

### 🤖 Machine Learning
- Revenue prediction model
- Data preprocessing pipeline
- Feature encoding
- Data scaling
- Saved trained ML models using Joblib

### 🌐 Web Application
- Flask backend
- HTML/CSS dashboard interface
- User input prediction system
- Interactive visualizations

---

## 🛠️ Technology Stack

### Programming Language
- Python

### Data Analysis
- Pandas
- NumPy

### Machine Learning
- Scikit-learn
- Joblib

### Visualization
- Plotly
- Matplotlib

### Web Framework
- Flask

### Frontend
- HTML
- CSS
- JavaScript

---

## 📂 Project Structure

```
Supply_Chain_Analysis/

│
├── app.py                         # Flask application
│
├── dataset/
│   └── supply_chain_data.csv      # Dataset
│
├── model/
│   ├── revenue_model.pkl          # Trained ML model
│   ├── encoder.pkl                # Label encoder
│   └── scaler.pkl                 # Feature scaler
│
├── src/
│   ├── train_model.py             # Model training
│   ├── prediction.py              # Prediction logic
│   ├── data_preprocessing.py      # Data cleaning & preparation
│   ├── visualization.py           # Data visualization
│   └── __init__.py
│
├── templates/
│   └── dashboard.html             # Dashboard UI
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       └── dashboard.js
│
├── reports/
│   └── training_report.txt
│
└── requirements.txt
```

---

## ⚙️ Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/Supply_Chain_Analysis.git
```

### 2. Navigate to Project Folder

```bash
cd Supply_Chain_Analysis
```

### 3. Create Virtual Environment

```bash
python -m venv venv
```

Activate environment:

**Windows**
```bash
venv\Scripts\activate
```

**Mac/Linux**
```bash
source venv/bin/activate
```

---

## 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run Application

Start Flask server:

```bash
python app.py
```

Application will run on:

```
http://127.0.0.1:5000/
```

---

## 🧠 Machine Learning Workflow

```
Dataset
   |
   ↓
Data Cleaning
   |
   ↓
Feature Engineering
   |
   ↓
Encoding & Scaling
   |
   ↓
Model Training
   |
   ↓
Model Saving (Joblib)
   |
   ↓
Revenue Prediction
```

---

## 📈 ML Model Pipeline

The project includes:

- Data preprocessing
- Feature transformation
- Model training
- Model evaluation
- Prediction system

Saved models:

- `revenue_model.pkl`
- `encoder.pkl`
- `scaler.pkl`

---

## 📊 Dashboard Modules

The dashboard provides:

- Supply chain data overview
- Revenue prediction
- Interactive charts
- Business insights
- Performance visualization

---

## 📌 Dataset

The project uses a supply chain dataset containing information related to:

- Product details
- Sales information
- Logistics data
- Operational factors
- Revenue-related features

---

## 🔮 Future Improvements

- Add more ML algorithms comparison
- Deploy using cloud platforms
- Add real-time supply chain monitoring
- Add inventory demand forecasting
- Add user authentication
- Improve dashboard UI

---

## 👨‍💻 Author

**Anish Sahu**

Data Analyst | Python | Machine Learning | Data Visualization

---

## ⭐ If you like this project

Give this repository a ⭐ on GitHub!
