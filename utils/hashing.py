import hashlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_CHUNK_SIZE = 8192  # bytes


def sha256_file(file_path: str | Path, chunk_size: int = DEFAULT_CHUNK_SIZE) -> str:
    """Compute the SHA-256 hex digest of a file's contents.

    Args:
        file_path: Path to the file to hash.
        chunk_size: Number of bytes to read per iteration (default 8192).
            Larger values trade memory for slightly faster I/O on big files.

    Returns:
        The SHA-256 hash as a lowercase hex string.

    Raises:
        FileNotFoundError: If the path does not exist.
        IsADirectoryError: If the path points to a directory.
        PermissionError: If the file can't be read due to permissions.
        ValueError: If chunk_size is not a positive integer.
    """
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be positive, got {chunk_size}")

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if path.is_dir():
        raise IsADirectoryError(f"Expected a file, got a directory: {path}")

    sha256 = hashlib.sha256()
    try:
        with path.open("rb") as file:
            for chunk in iter(lambda: file.read(chunk_size), b""):
                sha256.update(chunk)
    except PermissionError:
        logger.error("Permission denied reading file: %s", path)
        raise

    digest = sha256.hexdigest()
    logger.debug("Computed SHA-256 for %s: %s", path, digest)
    return digest