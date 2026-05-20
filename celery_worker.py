import os

import cv2
import numpy as np
from celery import Celery
from dotenv import load_dotenv

# Load models and analysis functions from the main app
from app import analyze_image, load_models, logger

load_dotenv()

# Initialize Celery with Redis as the message broker
celery = Celery(
    "agri_vision_tasks",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
)

# Load AI models once when the worker starts, not per request
load_models()


@celery.task(bind=True)
def process_inference_task(self, image_bytes_list, lat=None, lon=None):
    """
    Background task to run AI inference on the uploaded image.
    Takes image bytes (converted to list for JSON serialization), reconstructs it,
    runs the YOLO and ResNet models, and returns the result.
    """
    try:
        self.update_state(state="PROCESSING", meta={"status": "Analyzing image..."})

        # Reconstruct image from bytes list
        file_bytes = np.array(image_bytes_list, dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if image is None:
            return {"error": "Invalid image data"}

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Run heavy ML inference
        results = analyze_image(image_rgb)

        # Note: Weather logic could also be injected here if needed,
        # but for now we focus on the heavy AI lifting.

        return results

    except Exception as e:
        logger.error(f"Celery task failed: {e}")
        return {"error": str(e)}
