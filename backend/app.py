from io import BytesIO

import streamlit as st
from PIL import Image, UnidentifiedImageError

from backend.api.database import get_db_connection
from backend.api.model_service import (
    MODEL_NAME,
    MODEL_VERSION,
    predict_image,
)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

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
                (limit,),
            )

            records = cursor.fetchall()

            for record in records:
                if record["created_at"] is not None:
                    record["created_at"] = (
                        record["created_at"].isoformat()
                    )

            return records

        finally:
            cursor.close()

    finally:
        if connection is not None:
            connection.close()


def process_image(uploaded_file):
    contents = uploaded_file.getvalue()

    if not contents:
        st.error("The uploaded file is empty.")
        return

    if len(contents) > MAX_FILE_SIZE:
        st.error("The image exceeds the 10 MB upload limit.")
        return

    try:
        with Image.open(BytesIO(contents)) as source_image:
            source_image.verify()

        with Image.open(BytesIO(contents)) as source_image:
            image = source_image.convert("RGB")

    except (UnidentifiedImageError, OSError, ValueError):
        st.error("The uploaded file is not a valid image.")
        return

    try:
        result = predict_image(image)

        predicted_class = str(
            result["predicted_class"]
        ).lower()

        scores = result["class_scores"]
        normal_score = float(scores["normal"])
        abnormal_score = float(scores["abnormal"])

        if predicted_class not in ("normal", "abnormal"):
            st.error("The model returned an unexpected class.")
            return

        if not all(
            0.0 <= score <= 1.0
            for score in (normal_score, abnormal_score)
        ):
            st.error("The model returned invalid class scores.")
            return

    except Exception:
        st.error("Prediction failed. Check the backend logs.")
        return

    st.image(image, caption="Uploaded chest X-ray", width=400)

    st.markdown("### Experimental model output")

    if predicted_class == "normal":
        st.success("Predicted class: NORMAL")
    else:
        st.warning("Predicted class: ABNORMAL")

    st.metric(
        "Normal score",
        f"{normal_score * 100:.2f}%",
    )
    st.metric(
        "Abnormal score",
        f"{abnormal_score * 100:.2f}%",
    )

    try:
        history_id = save_prediction_history(
            uploaded_file.name or "uploaded_image",
            predicted_class,
            normal_score,
            abnormal_score,
        )
        st.caption(f"Prediction history ID: {history_id}")

    except Exception:
        st.error(
            "Prediction completed, but saving its history failed. "
            "Check your database connection."
        )


with st.sidebar:
    st.header("Model information")
    info = get_model_info()

    st.write(f"**Model:** {info['model_name']}")
    st.write(f"**Version:** {info['model_version']}")
    st.write("**Classes:** Normal, Abnormal")
    st.write("**Device:** CPU")
    st.write("**Maximum upload:** 10 MB")

    st.divider()
    st.caption(
        "This experimental model is not a substitute for "
        "professional medical evaluation."
    )

tab_predict, tab_history = st.tabs(
    ["Image prediction", "Prediction history"]
)

with tab_predict:
    uploaded_file = st.file_uploader(
        "Upload a chest X-ray image",
        type=["jpg", "jpeg", "png"],
    )

    if uploaded_file is not None:
        if st.button("Analyze image", type="primary"):
            process_image(uploaded_file)

with tab_history:
    st.subheader("Recent predictions")

    limit = st.selectbox(
        "Number of records",
        [10, 20, 50, 100],
        index=1,
    )

    if st.button("Refresh history"):
        st.rerun()

    try:
        records = get_prediction_history(limit)

        if records:
            st.dataframe(
                records,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No prediction history found.")

    except Exception:
        st.error(
            "Could not retrieve prediction history. "
            "Check your database connection."
        )