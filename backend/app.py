```python
from io import BytesIO

import streamlit as st
from PIL import Image, UnidentifiedImageError

from api.database import get_db_connection
from api.model_service import (
    MODEL_NAME,
    MODEL_VERSION,
    predict_image,
)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# Database history is disabled for the deployed demo.
ENABLE_DB_HISTORY = False

st.set_page_config(
    page_title="MedAI - Chest X-ray Assistant",
    page_icon="🩻",
    layout="centered",
)

st.title("🩻 MedAI")
st.subheader("Experimental Chest X-ray Classification")

st.warning(
    "Research and educational use only. This tool does not provide "
    "a medical diagnosis and must not be used to make treatment decisions."
)


def get_model_info():
    return {
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "classes": ["normal", "abnormal"],
        "input_format": ["JPEG", "PNG"],
        "maximum_upload_size_mb": 10,
        "device": "cpu",
        "intended_use": "Research and educational purposes only",
    }


def save_prediction_history(
    filename,
    predicted_class,
    normal_score,
    abnormal_score,
):
    connection = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO prediction_history (
                    image_filename,
                    predicted_class,
                    normal_score,
                    abnormal_score,
                    model_name,
                    model_version
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    filename[:255],
                    predicted_class,
                    normal_score,
                    abnormal_score,
                    MODEL_NAME,
                    MODEL_VERSION,
                ),
            )

            connection.commit()
            return cursor.lastrowid

        finally:
            cursor.close()

    except Exception:
        if connection is not None:
            try:
                connection.rollback()
            except Exception:
                pass
        raise

    finally:
        if connection is not None:
            connection.close()


def get_prediction_history(limit=20):
    connection = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT id, image_filename, predicted_class,
                       normal_score, abnormal_score, model_name,
                       model_version, created_at
                FROM prediction_history
                ORDER BY id DESC
                LIMIT %s
                """,
               