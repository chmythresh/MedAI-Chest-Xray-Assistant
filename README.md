# 🩻 Medical Image Diagnostic Assistant

An experimental **chest X-ray classification system** using **Python, PyTorch, ResNet18, FastAPI, MySQL, and Streamlit**.

The application allows users to upload a chest X-ray image and receive an experimental **Normal / Abnormal classification** with confidence scores.

> ⚠️ **For educational and research purposes only. This system does not provide a medical diagnosis.**

## 🚀 Live Demo

🔗 **Streamlit Application:**  
**[Add your Streamlit live link here]**

The live application provides:
- Chest X-ray image upload
- Image validation
- ResNet18-based classification
- Normal / Abnormal prediction
- Confidence scores
- Model information

## 📸 Screenshots

### 1. Streamlit Application

![MedAI Streamlit Application](screenshots/streamlit-home.png)

### 2. Chest X-ray Upload

![Chest X-ray Upload](screenshots/xray-upload.png)

### 3. Prediction Result

![Prediction Result](screenshots/prediction-result.png)

## 🧠 Machine Learning Model

The project uses a **fine-tuned ResNet18** model for experimental chest X-ray classification.

### Classes

- Normal
- Abnormal

### Model Evaluation

The fine-tuned ResNet18 achieved approximately:

- **Accuracy:** 0.85
- **Macro F1:** 0.849

These results are based on a 100-image test split used during model comparison and do not represent independent clinical validation.

## 🛠️ Technologies Used

- Python 3.11
- PyTorch
- ResNet18
- Streamlit
- FastAPI
- MySQL
- Pillow
- Uvicorn

## 📁 Project Structure

```text
medical-image-diagnostic-assistant/
│
├── backend/
│   ├── api/
│   ├── artifacts/
│   ├── data/
│   ├── ml/
│   ├── tests/
│   └── app.py
│
├── screenshots/
│   ├── streamlit-home.png
│   ├── xray-upload.png
│   └── prediction-result.png
│
├── .env
├── .gitignore
├── README.md
└── .venv/
```

## ⚙️ Local Setup

### 1. Create and activate virtual environment

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies

```powershell
pip install -r backend\requirements.txt
```

### 3. Run Streamlit

From the project root:

```powershell
$env:PYTHONPATH = (Get-Location).Path
python -m streamlit run backend\app.py
```

The application will open in your browser.

## 🔌 FastAPI Backend

The project also contains a FastAPI backend.

Start the API using:

```powershell
python -m uvicorn backend.api.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

### API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/model-info` | Model information |
| POST | `/predict` | Classify an uploaded image |
| GET | `/history?limit=20` | Prediction history |

## 🔄 Application Workflow

```text
Chest X-ray Dataset
        ↓
Data Preprocessing
        ↓
ResNet18 Fine-tuning
        ↓
Trained Model
        ↓
Streamlit Application
        ↓
Upload Chest X-ray
        ↓
Image Preprocessing
        ↓
ResNet18 Prediction
        ↓
Normal / Abnormal Classification
        ↓
Confidence Score
```

## 🔐 Security

Never commit the following files or data:

- `.env`
- Datasets
- Virtual environments
- Private medical images
- Database credentials

## ⚠️ Disclaimer

This project is intended **only for educational and research purposes**.

It is not a medical device and must not be used to diagnose, treat, or make clinical decisions about any disease. Model predictions may be incorrect and must not replace assessment by a qualified medical professional.

## 📄 License

No license has been specified for this project.
