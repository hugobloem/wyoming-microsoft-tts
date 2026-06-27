# Wyoming Microsoft TTS
Wyoming protocol server for Microsoft Azure text-to-speech.

This Python package provides a Wyoming integration for Microsoft Azure text-to-speech and can be directly used with [Home Assistant](https://www.home-assistant.io/) voice and [Rhasspy](https://github.com/rhasspy/rhasspy3).

## Azure Speech Service
This program uses [Microsoft Azure Speech Service](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/). You can sign up to a free Azure account which comes with free tier of 500K characters per month, this should be enough for running a voice assistant as each command is relatively short. Plus, on Home Assistant the outputs are cached so each response will only be requested once. Once this amount is exceeded Azure could charge you for each second used (Current pricing is $0.36 per audio hour). I am not responsible for any incurred charges and recommend you set up a spending limit to reduce your exposure. However, for normal usage the free tier could suffice and the resource should not switch to a paid service automatically.

If you have not set up a speech resource, you can follow the instructions below. (you only need to do this once and works both for [Speech-to-Text](https://github.com/hugobloem/wyoming-microsoft-stt) and [Text-to-Speech](https://github.com/hugobloem/wyoming-microsoft-tts))

1. Sign in or create an account on [portal.azure.com](https://portal.azure.com).
2. Create a subscription by searching for `subscription` in the search bar. [Consult Microsoft Learn for more information](https://learn.microsoft.com/en-gb/azure/cost-management-billing/manage/create-subscription#create-a-subscription-in-the-azure-portal).
3. Create a speech resource by searching for `speech service`.
4. Select the subscription you created, pick or create a resource group, select a region, pick an identifiable name, and select the pricing tier (you probably want Free F0)
5. Once created, copy one of the keys from the speech service page. You will need this to run this program.


## Installation
Depending on your use case there are different installation options.

- **Using pip**
  Clone the repository and install the package using pip. Please note the platform requirements as noted [here](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/quickstarts/setup-platform?tabs=linux%2Cubuntu%2Cdotnetcli%2Cdotnet%2Cjre%2Cmaven%2Cnodejs%2Cmac%2Cpypi&pivots=programming-language-python#platform-requirements).
  ```sh
  pip install .
  ```

- **Home Assistant Add-On**
  Add the following repository as an add-on repository to your Home Assistant, or click the button below.
  [https://github.com/hugobloem/homeassistant-addons](https://github.com/hugobloem/homeassistant-addons)

  [![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fhugobloem%2Fhomeassistant-addons)

- **Docker container**
  To run as a Docker container use the following command:
  ```bash
  docker run ghcr.io/hugobloem/wyoming-microsoft-tts-noha:latest --<key> <value>
  ```
  For the relevant keys please look at [the table below](#usage)

- **docker compose**

  Below is a sample for a docker compose file. The azure region + subscription key can be set in environment variables. Everything else needs to be passed via command line arguments.
  
  ```yaml
  wyoming-proxy-azure-tts:
    image: ghcr.io/hugobloem/wyoming-microsoft-tts-noha
    container_name: wyoming-azure-tts
    ports:
      - "10200:10200"
    environment:
      AZURE_SERVICE_REGION: swedencentral
      AZURE_SUBSCRIPTION_KEY: XXX
    command: --voice=en-GB-SoniaNeural --uri=tcp://0.0.0.0:10200
  ```

## Usage
Depending on the installation method parameters are parsed differently. However, the same options are used for each of the installation methods and can be found in the table below. Your service region and subscription key can be found on the speech service resource page (step 5 the Azure Speech service instructions).

For the bare-metal Python install the program is run as follows:
```python
python -m wyoming-microsoft-tts --<key> <value>
```

| Key | Optional | Description |
|---|---|---|
| `service-region` | No | Azure service region e.g., `uksouth` |
| `subscription-key` | No | Azure subscription key |
| `uri` | No | Uri where the server will be broadcasted e.g., `tcp://0.0.0.0:10200` |
| `download-dir` | Yes | Directory to download voices.json into (default: /tmp/) |
| `voice` | Yes | Default voice to set for transcription, default: `en-GB-SoniaNeural` |
| `auto-punctuation` | Yes | Automatically add punctuation (default: `".?!"`) |
| `samples-per-chunk` | Yes | Number of samples per audio chunk (default: 1024) |
| `update-voices` | Yes | Download latest languages.json during startup |
| `debug` | Yes | Log debug messages |
| `rate` | Yes | Default speech rate (e.g., `+30%`, `0.5`, `fast`, `slow`) |
| `pitch` | Yes | Default speech pitch (e.g., `+10%`, `high`, `low`, `+80Hz`) |
| `volume` | Yes | Default speech volume (e.g., `+20%`, `loud`, `soft`, `75`) |
| `style` | Yes | Default speaking style (e.g., `cheerful`, `sad`, `angry`, `calm`) |
| `style-degree` | Yes | Default style intensity from `0.01` to `2` (default: `1`) |

## Per-Call SSML Overrides from Home Assistant

In addition to setting default prosody and style at the server level (via `--rate`, `--pitch`, `--volume`, `--style`, `--style-degree`), you can override these values **per TTS call** by embedding Azure SSML tags directly in the message text from Home Assistant. This works through the `tts.speak` action without any changes to the Home Assistant Wyoming integration.

### Basic usage

```yaml
action: tts.speak
target:
  entity_id: tts.microsoft_tts
data:
  media_player_entity_id: media_player.living_room
  message: "<prosody rate='+50%'>This is extra fast!</prosody>"
```

### Style override

```yaml
message: "<mstts:express-as style='cheerful'>Have a great day!</mstts:express-as>"
```

### Multiple tags in one message

```yaml
message: "<prosody rate='+50%'>URGENT</prosody> announcement: <prosody pitch='high'>heads up</prosody>"
```

### Hybrid mode — server defaults + per-call overrides

When a `<prosody>` or `<mstts:express-as>` tag is found in the message text, the server **merges** its own defaults into the inline tags for any attribute **not already specified** on that tag. This gives you fine-grained control without repeating shared settings.

**Example:** Server started with `--rate +30% --pitch low --volume +10% --style excited`

```yaml
message: "<prosody rate='+50%'>override rate only</prosody>"
```

In this call:
- The inner `<prosody>` gets `rate="+50%"` (from message), `pitch="low"` and `volume="+10%"` (inherited from server defaults)
- Azure supports nested `<prosody>` — the outer wrapper supplies the server defaults as a fallback, and the inner tag overrides only the attributes it specifies
- Since no `<mstts:express-as>` is in the message, the server wraps the entire output with `<mstts:express-as style="excited">`

### Complete SSML passthrough

If you send a full SSML document (starting with `<speak`), it is passed to Azure **as-is**, ignoring all server defaults. This gives you complete control when needed:

```yaml
message: "<?xml version='1.0'?><speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'><voice name='en-US-JennyNeural'>Hello</voice></speak>"
```

### How merging works (edge cases)

| Case | Behavior |
|---|---|
| Plain text, no CLI args | Sent as plain text to Azure (no SSML) |
| Plain text, CLI args set | Wrapped with server defaults (existing behavior, unchanged) |
| SSML fragment (`<prosody>`, `<mstts:express-as>`) | Parsed; missing attrs filled from server defaults; wrapped in `<speak>` + `<voice>` |
| SSML fragment with invalid XML | Falls back to plain text treatment (server defaults applied) |
| Complete `<speak>` document | Passed through as-is, server defaults ignored |
| `<prosody>` in message + server prosody defaults | Nested `<prosody>`: outer has all server defaults, inner overrides specific attrs |
| `<mstts:express-as>` in message + server style | Missing attrs (`style`, `styledegree`) injected inline; no outer wrapper added |
| `<prosody>` in message, no server defaults | Used as-is with no additional wrapping |

### Reference: Supported Azure SSML tags

For the full list of supported styles, roles, prosody values, and SSML elements, see the [Microsoft SSML documentation](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-synthesis-markup-voice).
