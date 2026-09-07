"""
FaceTrace: A simple CLI utility for detecting faces in an image using InsightFace.

Usage:
    python facetrace.py --image sample/test.jpg
    python facetrace.py --image sample/test.jpg --det-size 320 320 --gpu
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from numpy.linalg import norm
from insightface.app import FaceAnalysis

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("facetrace")
def cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    return float(
        np.dot(embedding1, embedding2)
        / (norm(embedding1) * norm(embedding2))
    )

class FaceTraceError(Exception):
    """Raised for any recoverable error in the FaceTrace pipeline."""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect faces in an image using InsightFace's buffalo_l model."
    )
    parser.add_argument(
        "--image",
        type=Path,
        required=True,
        help="Path to the input image file.",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="buffalo_l",
        help="InsightFace model pack to use (default: buffalo_l).",
    )
    parser.add_argument(
        "--det-size",
        type=int,
        nargs=2,
        metavar=("WIDTH", "HEIGHT"),
        default=(640, 640),
        help="Detector input size (default: 640 640).",
    )
    parser.add_argument(
        "--gpu",
        action="store_true",
        help="Use GPU (CUDAExecutionProvider) instead of CPU.",
    )
    return parser.parse_args(argv)


def load_face_model(
    model_name: str,
    det_size: tuple[int, int],
    use_gpu: bool,
) -> FaceAnalysis:
    """Load and prepare the InsightFace model.

    Raises:
        FaceTraceError: if the model fails to load or prepare.
    """
    providers = ["CUDAExecutionProvider"] if use_gpu else ["CPUExecutionProvider"]
    logger.info("Loading model '%s' with providers=%s ...", model_name, providers)

    try:
        app = FaceAnalysis(name=model_name, providers=providers)
        app.prepare(ctx_id=0 if use_gpu else -1, det_size=det_size)
    except Exception as exc:  # noqa: BLE001 - surfaced as a domain error
        raise FaceTraceError(f"Failed to load/prepare model '{model_name}': {exc}") from exc

    logger.info("Model loaded successfully.")
    return app


def load_image(image_path: Path) -> np.ndarray:
    """Load an image from disk.

    Raises:
        FaceTraceError: if the file doesn't exist or can't be decoded.
    """
    if not image_path.is_file():
        raise FaceTraceError(f"Image not found: {image_path}")

    image = cv2.imread(str(image_path))
    if image is None:
        raise FaceTraceError(
            f"Image could not be decoded (unsupported format or corrupt file): {image_path}"
        )

    logger.info("Image loaded: %s (shape=%s)", image_path, image.shape)
    return image


def detect_faces(app: FaceAnalysis, image: np.ndarray) -> list[Any]:
    """Run face detection/analysis on an image."""
    faces = app.get(image)
    logger.info("Faces detected: %d", len(faces))
    return faces
def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        face_app = load_face_model(
            model_name=args.model_name,
            det_size=tuple(args.det_size),
            use_gpu=args.gpu,
        )

        image = load_image(args.image)
        faces = detect_faces(face_app, image)

        reference_image = load_image(Path("reference/reference.jpg"))
        reference_faces = detect_faces(face_app, reference_image)

        if not reference_faces:
            raise FaceTraceError("No face detected in reference image.")

        reference_embedding = reference_faces[0].embedding

    except FaceTraceError as exc:
        logger.error(str(exc))
        return 1

    if faces:
        logger.info("Face detected successfully! ✓")

        similarity = cosine_similarity(
            faces[0].embedding,
            reference_embedding
        )

        logger.info("Face similarity: %.2f%%", similarity * 100)
        if similarity >= 0.50:
            logger.info("MATCH CONFIRMED ✓")
        else:
            logger.info("NO MATCH ✗")
        bbox = faces[0].bbox.astype(int)

        cv2.rectangle(
            image,
            (bbox[0], bbox[1]),
            (bbox[2], bbox[3]),
            (0, 255, 0),
            2,
        )

        cv2.imwrite("sample/detected_face.jpg", image)

        logger.info(
            "Detected face image saved to sample/detected_face.jpg ✓"
        )

        embedding = faces[0].embedding

        logger.info("Face embedding generated successfully! ✓")
        logger.info("Embedding dimensions: %s", embedding.shape)

        return 0

    logger.warning("No face detected.")
    return 0
if __name__ == "__main__":
    sys.exit(main())