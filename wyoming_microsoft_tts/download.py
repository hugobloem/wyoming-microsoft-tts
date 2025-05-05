"""Utility for downloading Microsoft voices."""

import json
import logging
from pathlib import Path
from typing import Any, Union
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
    """Transform the voices.json file from the Microsoft API to the format used by Wyoming."""
    json_response = json.load(response)
    voices = {}
    for entry in json_response:
        country = countries.get(alpha_2=entry["Locale"].split("-")[1])
        try:
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
            if "SecondaryLocaleList" in entry:
                for secondary_locale in entry["SecondaryLocaleList"]:
                    country = countries.get(alpha_2=secondary_locale.split("-")[1])
                    voices[
                        entry["ShortName"].replace(entry["Locale"], secondary_locale)
                    ] = {
                        "key": entry["ShortName"],
                        "name": entry["LocalName"],
                        "language": {
                            "code": secondary_locale,
                            "family": secondary_locale.split("-")[0],
                            "region": country.alpha_2,
                            "name_native": secondary_locale,
                            "name_english": secondary_locale,
                            "country_english": country.name,
                        },
                        "quality": entry["VoiceType"],
                        "num_speakers": 1,
                        "speaker_id_map": {},
                        "aliases": [],
                    }
        except Exception as e:
            _LOGGER.error("Failed to parse voice %s", entry["ShortName"])
            _LOGGER.debug("%s: %s", entry["ShortName"], e)
    return voices


def get_voices(
    download_dir: Union[str, Path],
    update_voices: bool = False,
    region: str = "westus",
    key: str = "",
) -> dict[str, Any]:
    """Load available voices from downloaded or embedded JSON file."""
    download_dir = Path(download_dir)
    download_dir.mkdir(parents=True, exist_ok=True)
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
        return transform_voices_files(voices_file)


def find_voice(name: str, download_dir: Union[str, Path]) -> dict[str, Any]:
    """Look for the files for a voice.

    Returns: Dict of voice info
    """
    voices = get_voices(download_dir)
    if name in voices:
        # Already installed
        return voices[name]

    raise VoiceNotFoundError(name)
