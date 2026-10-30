import os
import logging
from enum import Enum
from functools import lru_cache
from pathlib import Path

from PIL import Image, UnidentifiedImageError
from ultralytics import YOLO

logger = logging.getLogger(__name__)


class ImageVerdict(str, Enum):
    VALID = "valid"
    INVALID = "invalid"
    UNCERTAIN = "uncertain"


VEHICLE_CLASSES = {"car", "motorcycle", "truck", "bus"}
CONFIDENCE_THRESHOLD = 0.40
DEBUG_CONFIDENCE = 0.05  


@lru_cache(maxsize=1)
def get_model():
    default_path = Path(__file__).resolve().parents[2] / "yolo11n.pt"
    model_path = Path(
        os.environ.get("YOLO_MODEL_PATH", str(default_path))
    )
    return YOLO(str(model_path))


def validate_vehicle_image(image_file) -> ImageVerdict:
    try:
        image_file.seek(0)

        with Image.open(image_file) as source:
            image = source.convert("RGB")

        results = get_model().predict(
            source=image,
            conf=DEBUG_CONFIDENCE,
            device="cpu",
            verbose=False,
        )

        if not results:
            logger.warning("YOLO returned no results object")
            return ImageVerdict.UNCERTAIN

        result = results[0]
        seen = [
            (result.names[int(box.cls.item())], round(box.conf.item(), 2))
            for box in result.boxes
        ]
        logger.warning(
            "YOLO DETECTIONS: %s | image size: %s", seen, image.size
        )

        detected = {
            name for name, conf in seen if conf >= CONFIDENCE_THRESHOLD
        }

        return (
            ImageVerdict.VALID
            if detected & VEHICLE_CLASSES
            else ImageVerdict.INVALID
        )

    except (UnidentifiedImageError, OSError):
        logger.warning("Could not open image", exc_info=True)
        return ImageVerdict.INVALID

    except Exception:
        logger.exception("Vehicle image validation failed")
        return ImageVerdict.UNCERTAIN

    finally:
        image_file.seek(0)