from __future__ import annotations

import logging
import os
from dataclasses import dataclass

import cv2
import numpy as np
import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger("reverse_search")

API_URL = "https://api.quanticdata.io/v1/serp"

# Demo threshold only. This should be calibrated before real-world use.
FACE_MATCH_THRESHOLD = 0.50


class ReverseSearchError(Exception):
    """Raised when reverse image search fails."""


@dataclass(frozen=True)
class SearchResult:
    title: str
    link: str
    source: str
    domain: str
    image: str | None = None
    thumbnail: str | None = None


def download_image(image_url: str) -> bytes:
    """Download a candidate image from a public URL."""

    try:
        response = requests.get(
            image_url,
            timeout=30,
            headers={"User-Agent": "FaceTrace/1.0"},
        )
        response.raise_for_status()

    except requests.RequestException as exc:
        raise ReverseSearchError(
            f"Could not download candidate image: {exc}"
        ) from exc

    content_type = response.headers.get("Content-Type", "")

    if not content_type.startswith("image/"):
        raise ReverseSearchError(
            f"URL did not return an image. Content-Type: {content_type}"
        )

    return response.content


def decode_image(image_data: bytes) -> np.ndarray:
    """Decode downloaded image bytes into an OpenCV image."""

    buffer = np.frombuffer(image_data, dtype=np.uint8)

    image = cv2.imdecode(
        buffer,
        cv2.IMREAD_COLOR,
    )

    if image is None:
        raise ReverseSearchError(
            "Downloaded data could not be decoded as an image."
        )

    return image


def load_reference_embedding(
    reference_path: str = "reference/reference.jpg",
) -> np.ndarray:
    """Load the reference image and generate its face embedding."""

    image = cv2.imread(reference_path)

    if image is None:
        raise ReverseSearchError(
            f"Reference image could not be loaded: {reference_path}"
        )

    from insightface.app import FaceAnalysis

    app = FaceAnalysis(
        name="buffalo_l",
        providers=["CPUExecutionProvider"],
    )

    app.prepare(
        ctx_id=-1,
        det_size=(640, 640),
    )

    faces = app.get(image)

    if not faces:
        raise ReverseSearchError(
            "No face detected in the reference image."
        )

    return faces[0].embedding


def verify_face(
    image: np.ndarray,
    reference_embedding: np.ndarray,
) -> float:
    """Return cosine similarity between candidate and reference face."""

    from insightface.app import FaceAnalysis

    app = FaceAnalysis(
        name="buffalo_l",
        providers=["CPUExecutionProvider"],
    )

    app.prepare(
        ctx_id=-1,
        det_size=(640, 640),
    )

    faces = app.get(image)

    if not faces:
        logger.info("No face detected in candidate image.")
        return 0.0

    embedding = faces[0].embedding

    denominator = (
        np.linalg.norm(embedding)
        * np.linalg.norm(reference_embedding)
    )

    if denominator == 0:
        return 0.0

    similarity = float(
        np.dot(
            embedding,
            reference_embedding,
        )
        / denominator
    )

    if similarity >= FACE_MATCH_THRESHOLD:
        logger.info(
            "Face match confirmed: %.4f",
            similarity,
        )
    else:
        logger.info(
            "Face match rejected: %.4f",
            similarity,
        )

    return similarity


def reverse_image_search(
    image_url: str,
    max_results: int = 10,
) -> list[SearchResult]:
    """Search the public web and verify returned candidates by face."""

    api_key = os.getenv("QD_API_KEY")

    if not api_key:
        raise ReverseSearchError(
            "QD_API_KEY is not configured."
        )

    if not image_url.startswith(
        ("http://", "https://")
    ):
        raise ReverseSearchError(
            "image_url must be a public HTTP/HTTPS URL."
        )

    if not 1 <= max_results <= 40:
        raise ReverseSearchError(
            "max_results must be between 1 and 40."
        )

    # ---------------------------------------------------------
    # STEP 1: Genuine reverse-image search
    # ---------------------------------------------------------

    try:
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "engine": "google",
                "search_type": "lens",
                "image_url": image_url,
                "num": max_results,
            },
            timeout=120,
        )

        response.raise_for_status()
        data = response.json()

    except requests.RequestException as exc:
        raise ReverseSearchError(
            f"Reverse image search request failed: {exc}"
        ) from exc

    if data.get("type") == "error":
        raise ReverseSearchError(
            data.get(
                "message",
                "QuanticData returned an error.",
            )
        )

    payload = data.get("payload", {})

    # IMPORTANT:
    # Only visual_matches are treated as reverse-image
    # candidates. Ordinary web/organic results are NOT
    # considered image matches.
    results = payload.get(
        "visual_matches",
        [],
    )

    logger.info(
        "Reverse search returned %d visual match(es).",
        len(results),
    )

    # ---------------------------------------------------------
    # STEP 2: Load our reference face
    # ---------------------------------------------------------

    reference_embedding = load_reference_embedding()

    verified_results: list[SearchResult] = []

    # ---------------------------------------------------------
    # STEP 3: Verify every candidate using InsightFace
    # ---------------------------------------------------------

    for result in results:

        candidate_image_url = result.get("image")

        if not candidate_image_url:
            logger.warning(
                "Skipping candidate without image URL."
            )
            continue

        try:
            image_data = download_image(
                candidate_image_url
            )

            candidate_image = decode_image(
                image_data
            )

            similarity = verify_face(
                candidate_image,
                reference_embedding,
            )

            logger.info(
                "Candidate: %s | Face similarity: %.2f%%",
                result.get("title", ""),
                similarity * 100,
            )

            # Only accept the result if the detected face
            # is sufficiently similar to the reference face.
            if similarity >= FACE_MATCH_THRESHOLD:

                verified_results.append(
                    SearchResult(
                        title=result.get("title") or "",
                        link=result.get("link") or "",
                        source=result.get("source") or "",
                        domain=result.get("domain") or "",
                        image=result.get("image"),
                        thumbnail=result.get("thumbnail"),
                    )
                )

        except ReverseSearchError as exc:

            logger.warning(
                "Could not verify candidate image: %s",
                exc,
            )

    # ---------------------------------------------------------
    # STEP 4: Return only face-verified results
    # ---------------------------------------------------------

    logger.info(
        "Verified face matches: %d",
        len(verified_results),
    )

    return verified_results


if __name__ == "__main__":

    image_url = input(
        "Enter public image URL: "
    ).strip()

    try:

        results = reverse_image_search(
            image_url
        )

        print(
            f"\nFound {len(results)} verified face match(es):\n"
        )

        for result in results:

            print(
                f"Title:  {result.title}"
            )

            print(
                f"Link:   {result.link}"
            )

            print(
                f"Source: {result.source}"
            )

            print(
                f"Domain: {result.domain}"
            )

            print(
                f"Image:  {result.image}"
            )

            print("-" * 60)

    except ReverseSearchError as exc:

        print(
            f"ERROR: {exc}"
        )