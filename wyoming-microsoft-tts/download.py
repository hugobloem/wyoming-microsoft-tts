"""Utility for downloading Microsoft voices."""
import json
import logging
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from pycountry import countries

URL_FORMAT = "https://{region}.tts.speech.microsoft.com/cognitiveservices/voices/list"
URL_HEADER = "Ocp-Apim-Subscription-Key"


_DIR = Path(__file__).parent
_LOGGER = logging.getLogger(__name__)

_SKIP_FILES = {"MODEL_CARD"}


class VoiceNotFoundError(Exception):
    """Raised when a voice is not found."""

    pass


def _quote_url(url: str) -> str:
    """Quote file part of URL in case it contains UTF-8 characters."""
    parts = list(urlsplit(url))
    parts[2] = quote(parts[2])
    return urlunsplit(parts)


def transform_voices_files(response):
    """Transform the voices.json file from the Microsoft API to the format used by Piper."""
    json_response = json.load(response)
    voices = {}
    for entry in json_response:
        country = countries.get(alpha_2=entry["Locale"].split("-")[1])
        voices[entry["ShortName"]] = {
            "key": entry["ShortName"],
            "name": entry["LocalName"],
            "language": {
                "code": entry["Locale"],
                "family": entry["Locale"].split("-")[0],
                "region": country.alpha_2,
                "name_native": entry["LocaleName"],
                "name_english": entry["LocaleName"],
                "country_english": country.name,
            },
            "quality": entry["VoiceType"],
            "num_speakers": 1,
            "speaker_id_map": {},
            "aliases": [],
        }
    return voices


def get_voices(
    download_dir: str | Path,
    update_voices: bool = False,
    region: str = "westus",
    key: str = "",
) -> dict[str, Any]:
    """Load available voices from downloaded or embedded JSON file."""
    download_dir = Path(download_dir)
    voices_download = download_dir / "voices.json"

    if update_voices:
        # Download latest voices.json
        try:
            voices_url = URL_FORMAT.format(region=region)
            voices_hdr = {URL_HEADER: key}
            _LOGGER.debug("Downloading %s to %s", voices_url, voices_download)
            req = Request(_quote_url(voices_url), headers=voices_hdr)
            with urlopen(req) as response, open(voices_download, "w") as download_file:
                json.dump(transform_voices_files(response), download_file, indent=4)
        except Exception:
            _LOGGER.exception("Failed to update voices list")

    # Prefer downloaded file to embedded
    if voices_download.exists():
        try:
            _LOGGER.debug("Loading %s", voices_download)
            with open(voices_download, encoding="utf-8") as voices_file:
                return json.load(voices_file)
        except Exception:
            _LOGGER.exception("Failed to load %s", voices_download)

    # Fall back to embedded
    voices_embedded = _DIR / "voices.json"
    _LOGGER.debug("Loading %s", voices_embedded)
    with open(voices_embedded, encoding="utf-8") as voices_file:
        return json.load(voices_file)


def find_voice(name: str, download_dir: str | Path) -> dict[str, Any]:
    """Look for the files for a voice.

    Returns: Dict of voice info
    """
    voices = get_voices(download_dir)
    if name in voices:
        # Already installed
        return voices[name]

    raise VoiceNotFoundError(name)
