# AllTalk TTS API Documentation

## Overview

AllTalk TTS API provides high-quality text-to-speech generation with support for multiple engines and voices. This API is now fully operational with both Piper (fast) and XTTS (high-quality) engines working correctly.

## Base URL

```
http://localhost:7851
```

## Available Endpoints

### Main TTS Generation
- **POST** `/api/tts-generate` - Generate TTS audio

### System Information
- **GET** `/api/currentsettings` - Get current engine status and settings
- **GET** `/api/voices` - List available voices
- **GET** `/api/ready` - Health check endpoint

### Additional Endpoints
- **GET** `/api/rvcvoices` - List RVC voices (if available)
- **POST** `/api/enginereload` - Reload engine configuration
- **POST** `/api/reload_config` - Reload configuration

## TTS Generation API

### Endpoint
```
POST /api/tts-generate
```

### Headers
```
Content-Type: application/x-www-form-urlencoded
```

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `text_input` | string | Yes | - | Text to convert to speech |
| `character_voice_gen` | string | No | System default | Voice identifier |
| `speed` | float | No | 1.0 | Speech speed (0.25 - 4.0) |
| `temperature` | float | No | 0.75 | Generation temperature |
| `repetition_penalty` | float | No | 10.0 | Repetition penalty |
| `output_file_name` | string | No | Auto-generated | Output filename |
| `output_file_timestamp` | boolean | No | true | Add timestamp to filename |
| `autoplay` | boolean | No | false | Autoplay generated audio |
| `autoplay_volume` | float | No | 1.0 | Autoplay volume |
| `streaming` | boolean | No | false | Enable streaming mode |

### Response Format

**Success (200):**
```json
{
  "status": "generate-success",
  "output_file_path": "/home/alltalk/config/app/outputs/filename.wav",
  "output_file_url": "/audio/filename.wav",
  "output_cache_url": "/audiocache/filename.wav"
}
```

**Error (500):**
```json
{
  "detail": "Error description",
  "status": "error"
}
```

## Voice Options

### Piper Engine (Fast - Recommended for most applications)

**Available Voices:**
- `en_US-joe-medium.onnx` - Default male voice
- `en_US-lessac-high.onnx` - High quality male voice
- `en_US-kristin-medium.onnx` - Female voice
- `en_US-lessac-low.onnx` - Low quality male voice
- `en_US-ryan-low.onnx` - Male voice

**Usage Example:**
```bash
curl -X POST "http://localhost:7851/api/tts-generate" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text_input=Hello world, this is Piper TTS." \
  -d "character_voice_gen=en_US-joe-medium.onnx"
```

### XTTS Engine (High Quality)

**Available Builtin Voices:**
- `builtin:Aaron Dreschner` - Male voice
- `builtin:Claribel Dervla` - Female voice
- `builtin:Daisy Studious` - Female voice
- `builtin:Gracie Wise` - Female voice
- `builtin:Tammie Ema` - Female voice
- `builtin:Alison Dietlinde` - Female voice
- `builtin:Ana Florence` - Female voice
- `builtin:Annmarie Nele` - Female voice
- `builtin:Asya Anara` - Female voice
- `builtin:Brenda Stern` - Female voice
- `builtin:Gitta Nikolina` - Female voice

**Usage Example:**
```bash
curl -X POST "http://localhost:7851/api/tts-generate" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text_input=Hello world, this is XTTS high quality." \
  -d "character_voice_gen=builtin:Aaron Dreschner"
```

## API Usage Examples

### Basic TTS Generation

```bash
curl -X POST "http://localhost:7851/api/tts-generate" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text_input=Hello, this is a test of the AllTalk TTS API."
```

### With Specific Voice

```bash
curl -X POST "http://localhost:7851/api/tts-generate" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text_input=Testing with a specific voice." \
  -d "character_voice_gen=en_US-joe-medium.onnx"
```

### With Speed Control

```bash
curl -X POST "http://localhost:7851/api/tts-generate" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text_input=This is faster speech." \
  -d "character_voice_gen=en_US-joe-medium.onnx" \
  -d "speed=1.5"
```

### Download Generated Audio

```bash
# First generate TTS
curl -X POST "http://localhost:7851/api/tts-generate" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text_input=Download this audio file." \
  --output response.json

# Extract audio URL from response and download
AUDIO_URL=$(cat response.json | jq -r '.output_file_url')
curl "http://localhost:7851$AUDIO_URL" --output generated_audio.wav
```

## System Information

### Get Current Settings

```bash
curl -s "http://localhost:7851/api/currentsettings" | jq '.'
```

**Response:**
```json
{
  "engines_available": ["piper", "xtts"],
  "current_engine_loaded": "piper",
  "models_available": [{"name": "piper"}],
  "current_model_loaded": "piper",
  "manufacturer_name": "Piper",
  "audio_format": "wav",
  "deepspeed_capable": false,
  "deepspeed_available": true,
  "deepspeed_enabled": false,
  "generationspeed_capable": true,
  "generationspeed_set": 1,
  "lowvram_capable": false,
  "lowvram_enabled": false,
  "pitch_capable": false,
  "pitch_set": 0,
  "repetitionpenalty_capable": false,
  "repetitionpenalty_set": 10,
  "streaming_capable": false,
  "temperature_capable": false,
  "temperature_set": 0.75,
  "ttsengines_installed": true,
  "languages_capable": false,
  "multivoice_capable": true,
  "multimodel_capable": true
}
```

### Get Available Voices

```bash
curl -s "http://localhost:7851/api/voices" | jq '.voices'
```

**Response:**
```json
{
  "voices": [
    "en_US-libritts-high.onnx",
    "en_US-lessac-high.onnx",
    "en_US-lessac-low.onnx",
    "en_US-kristin-medium.onnx",
    "en_US-lessac-medium.onnx",
    "en_US-ryan-low.onnx",
    "en_US-joe-medium.onnx"
  ]
}
```

### Health Check

```bash
curl -s "http://localhost:7851/api/ready"
```

**Response:**
```
Ready
```

## Integration Examples

### Python Integration

```python
import requests
import json

class AllTalkTTSClient:
    def __init__(self, base_url="http://localhost:7851"):
        self.base_url = base_url
        self.endpoint = "/api/tts-generate"
    
    def generate_speech(self, text, voice="en_US-joe-medium.onnx", speed=1.0):
        """Generate TTS audio and return download URL"""
        params = {
            "text_input": text,
            "character_voice_gen": voice,
            "speed": speed
        }
        
        try:
            response = requests.post(
                f"{self.base_url}{self.endpoint}",
                data=params,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return f"{self.base_url}{result['output_file_url']}"
            else:
                raise Exception(f"TTS generation failed: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {e}")
    
    def download_audio(self, audio_url, output_path):
        """Download generated audio file"""
        response = requests.get(audio_url)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        return output_path
    
    def generate_and_download(self, text, voice="en_US-joe-medium.onnx", output_path="output.wav"):
        """Generate TTS and download in one step"""
        audio_url = self.generate_speech(text, voice)
        return self.download_audio(audio_url, output_path)

# Usage Examples
tts = AllTalkTTSClient()

# Fast generation with Piper
audio_url = tts.generate_speech("Hello from MoneyPrinterTurbo!", "en_US-joe-medium.onnx")
print(f"Audio URL: {audio_url}")

# High quality generation with XTTS
tts.generate_and_download(
    "This is high quality XTTS speech.", 
    "builtin:Aaron Dreschner", 
    "xtts_output.wav"
)
```

### JavaScript Integration

```javascript
class AllTalkTTSClient {
    constructor(baseUrl = 'http://localhost:7851') {
        this.baseUrl = baseUrl;
        this.endpoint = '/api/tts-generate';
    }

    async generateSpeech(text, voice = 'en_US-joe-medium.onnx', options = {}) {
        const params = new URLSearchParams({
            text_input: text,
            character_voice_gen: voice,
            ...options
        });

        try {
            const response = await fetch(`${this.baseUrl}${this.endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: params
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return `${this.baseUrl}${result.output_file_url}`;
        } catch (error) {
            console.error('Error generating TTS:', error);
            throw error;
        }
    }

    async downloadAudio(audioUrl, filename = 'output.wav') {
        try {
            const response = await fetch(audioUrl);
            const blob = await response.blob();
            
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error('Error downloading audio:', error);
            throw error;
        }
    }
}

// Usage
const tts = new AllTalkTTSClient();

// Generate TTS
tts.generateSpeech('Hello from JavaScript!', 'en_US-joe-medium.onnx')
    .then(audioUrl => {
        console.log('Audio URL:', audioUrl);
        return tts.downloadAudio(audioUrl, 'speech.wav');
    })
    .catch(error => console.error('Error:', error));
```

## Configuration for Applications

### Environment Variables

```bash
# AllTalk TTS Configuration
ALLTALK_API_BASE_URL=http://localhost:7851
ALLTALK_DEFAULT_VOICE=en_US-joe-medium.onnx
ALLTTS_FALLBACK_VOICE=builtin:Aaron Dreschner
ALLTALK_TIMEOUT=30
ALLTTS_MAX_RETRIES=3
```

### Configuration File (JSON)

```json
{
  "tts_provider": "alltalk",
  "api_base_url": "http://localhost:7851",
  "default_engine": "piper",
  "default_voice": "en_US-joe-medium.onnx",
  "fallback_engine": "xtts",
  "fallback_voice": "builtin:Aaron Dreschner",
  "timeout": 30,
  "max_text_length": 1000,
  "supported_voices": {
    "piper": [
      "en_US-joe-medium.onnx",
      "en_US-lessac-high.onnx",
      "en_US-kristin-medium.onnx",
      "en_US-lessac-low.onnx",
      "en_US-ryan-low.onnx"
    ],
    "xtts": [
      "builtin:Aaron Dreschner",
      "builtin:Claribel Dervla",
      "builtin:Daisy Studious",
      "builtin:Gracie Wise",
      "builtin:Tammie Ema",
      "builtin:Alison Dietlinde",
      "builtin:Ana Florence",
      "builtin:Annmarie Nele",
      "builtin:Asya Anara",
      "builtin:Brenda Stern",
      "builtin:Gitta Nikolina"
    ]
  },
  "performance": {
    "piper_response_time": "~2 seconds",
    "xtts_response_time": "~3.5 seconds",
    "piper_audio_quality": "Good",
    "xtts_audio_quality": "Excellent",
    "sample_rates": {
      "piper": "22050 Hz",
      "xtts": "24000 Hz"
    }
  }
}
```

## Performance Considerations

### Response Times
- **Piper Engine**: ~2 seconds
- **XTTS Engine**: ~3.5 seconds

### Audio Quality
- **Piper**: Good quality, smaller files (~160KB)
- **XTTS**: Excellent quality, larger files (~580KB)

### Sample Rates
- **Piper**: 22.05 kHz
- **XTTS**: 24 kHz

### Resource Usage
- **Piper**: Low GPU/CPU usage
- **XTTS**: Higher GPU usage (~2GB VRAM)

## Error Handling

### Common HTTP Status Codes

| Status | Description | Solution |
|--------|-------------|----------|
| 200 | Success | Audio generated successfully |
| 422 | Unprocessable Entity | Invalid parameters or missing required fields |
| 500 | Internal Server Error | TTS generation failed (check logs) |

### Common Errors

**"Model file not found"**
- Check if the voice identifier is correct
- Verify the voice is available in the system

**"Error opening voice file"**
- Voice parameter not being passed correctly
- Use proper voice format (e.g., `en_US-joe-medium.onnx` or `builtin:Aaron Dreschner`)

**"Connection refused"**
- AllTalk service is not running
- Check if the container is started

## Health Monitoring

### Health Check Script

```python
import requests
import time

def check_tts_health():
    try:
        response = requests.get("http://localhost:7851/api/ready", timeout=5)
        if response.status_code == 200:
            return True, "AllTalk TTS is ready"
        else:
            return False, f"Health check failed: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {e}"

def monitor_tts(interval=60):
    """Monitor TTS service health"""
    while True:
        is_healthy, message = check_tts_health()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        if is_healthy:
            print(f"[{timestamp}] ✅ {message}")
        else:
            print(f"[{timestamp}] ❌ {message}")
        
        time.sleep(interval)

# Usage
if __name__ == "__main__":
    monitor_tts()
```

## Troubleshooting

### Check Service Status
```bash
# Check if AllTalk is running
docker ps | grep alltalk

# Check container logs
docker logs alltalk-dev --tail 20

# Health check
curl -s "http://localhost:7851/api/ready"
```

### Verify Voice Availability
```bash
# Check current engine
curl -s "http://localhost:7851/api/currentsettings" | jq '.current_engine_loaded'

# Check available voices
curl -s "http://localhost:7851/api/voices" | jq '.voices'
```

### Test Basic Functionality
```bash
# Simple test
curl -X POST "http://localhost:7851/api/tts-generate" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text_input=Health check test."
```

## Support

### Documentation Files
- Configuration Architecture: `/mnt/samsungssd/repo/alltalk_tts/config/system/CONFIGURATION_ARCHITECTURE.md`
- Change Log: `/mnt/samsungssd/repo/alltalk_tts/config/system/CHANGELOG_v2.1.md`
- Docker Volume Issue Documentation: `/mnt/samsungssd/repo/alltalk_tts/config/system/DOCKER_VOLUME_MOUNT_ISSUE.md`

### Container Management
```bash
# Restart service
docker restart alltalk-dev

# Stop service
docker stop alltalk-dev

# View logs
docker logs alltalk-dev -f
```

---

**Last Updated**: 2026-06-14  
**Version**: 2.1.0  
**Status**: Fully Operational - Both Piper and XTTS engines working correctly