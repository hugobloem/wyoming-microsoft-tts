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


def _get_country_from_locale(locale: str):
    """Extract country information from a locale string.

    Handles both standard (lang-COUNTRY) and extended (lang-script-COUNTRY) locale formats.
    """
    parts = locale.split("-")

    # For extended locales like "iu-Cans-CA", the country code is the last part
    if len(parts) >= 3:
        country_code = parts[-1]
    elif len(parts) == 2:
        country_code = parts[1]
    else:
        return None

    return countries.get(alpha_2=country_code)


def transform_voices_files(response):
    """Transform the voices.json file from the Microsoft API to the format used by Wyoming."""
    json_response = json.load(response)
    voices = {}
    for entry in json_response:
        if not isinstance(entry, dict):
            continue

        try:
            country = _get_country_from_locale(entry["Locale"])
            # Use fallback values if country lookup fails
            if country is None:
                region = entry["Locale"].split("-")[-1]  # Use the last part as region
                country_name = "Unknown"
                _LOGGER.warning(
                    "Could not find country for locale %s, using fallback values",
                    entry["Locale"],
                )
            else:
                region = country.alpha_2
                country_name = country.name

            voices[entry["ShortName"]] = {
                "key": entry["ShortName"],
                "name": entry["LocalName"],
                "language": {
                    "code": entry["Locale"],
                    "family": entry["Locale"].split("-")[0],
                    "region": region,
                    "name_native": entry["LocaleName"],
                    "name_english": entry["LocaleName"],
                    "country_english": country_name,
                },
                "quality": entry["VoiceType"],
                "num_speakers": 1,
                "speaker_id_map": {},
                "aliases": [],
            }
            if "SecondaryLocaleList" in entry:
                for secondary_locale in entry["SecondaryLocaleList"]:
                    secondary_country = _get_country_from_locale(secondary_locale)

                    # Use fallback values if country lookup fails
                    if secondary_country is None:
                        secondary_region = secondary_locale.split("-")[-1]
                        secondary_country_name = "Unknown"
                        _LOGGER.warning(
                            "Could not find country for secondary locale %s, using fallback values",
                            secondary_locale,
                        )
                    else:
                        secondary_region = secondary_country.alpha_2
                        secondary_country_name = secondary_country.name

                    voices[
                        entry["ShortName"].replace(entry["Locale"], secondary_locale)
                    ] = {
                        "key": entry["ShortName"],
                        "name": entry["LocalName"],
                        "language": {
                            "code": secondary_locale,
                            "family": secondary_locale.split("-")[0],
                            "region": secondary_region,
                            "name_native": secondary_locale,
                            "name_english": secondary_locale,
                            "country_english": secondary_country_name,
                        },
                        "quality": entry["VoiceType"],
                        "num_speakers": 1,
                        "speaker_id_map": {},
                        "aliases": [],
                    }
        except Exception as e:
            _LOGGER.exception(
                "Failed to parse voice %s", entry.get("ShortName", "Unknown")
            )
            _LOGGER.debug("%s: %s", entry.get("ShortName", "Unknown"), e)
    return voices


def get_voices(
    download_dir: str | Path,
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
            _LOGGER.debug("Loading downloaded file: %s", voices_download)
            with open(voices_download, encoding="utf-8") as voices_file:
                return json.load(voices_file)
        except Exception:
            _LOGGER.exception("Failed to load %s", voices_download)

    # Fall back to embedded
    voices_embedded = _DIR / "voices.json"
    _LOGGER.debug("Loading embedded file: %s", voices_embedded)
    with open(voices_embedded, encoding="utf-8") as voices_file:
        return transform_voices_files(voices_file)


def find_voice(name: str, download_dir: str | Path) -> dict[str, Any]:
    """Look for the files for a voice.

    Returns: Dict of voice info
    """
    voices = get_voices(download_dir)
    if name in voices:
        # Already installed
        return voices[name]

    raise VoiceNotFoundError(name)
