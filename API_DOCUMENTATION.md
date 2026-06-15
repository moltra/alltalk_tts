# AllTalk TTS API Documentation

## Overview

AllTalk TTS provides a REST API compatible with OpenAI's API format, making it easy to integrate with various TTS clients and applications. The API supports text-to-speech generation, voice listing, and model management.

## API Discovery

**Automatic API Discovery**: `GET /api/info`

AllTalk TTS provides an API discovery endpoint that clients can use to automatically discover available endpoints and their URLs:

```bash
curl http://localhost:7851/api/info
```

This endpoint returns:
- All available endpoints with their URLs and methods
- Server capabilities and current status
- Links to documentation (Swagger UI, OpenAPI spec, manual docs)
- Current engine and model information

**Recommended**: Use this endpoint for automatic configuration rather than hardcoding URLs.

## Base URL

The API is typically available at:
- `http://localhost:7851` (default)
- `http://alltalk-dev:7851` (Docker environment)
- `http://your-server-ip:7851` (remote deployment)

## Recent Fixes

### Pydantic v2 Compatibility (2024-01-XX)

Fixed Pydantic v2 compatibility issues that were causing `AttributeError: 'FieldInfo' object has no attribute 'field_info'` errors:

- **Line 1228**: Changed `OpenAIInput.model_fields[field].field_info.description` to `OpenAIInput.model_fields[field].description`
- **Line 1436**: Changed `mappings.dict()` to `mappings.model_dump()`

These fixes ensure proper compatibility with Pydantic v2.x, which is required for the OpenAI-compatible API endpoints.

## OpenAI-Compatible Endpoints

### 1. Generate Speech - `POST /v1/audio/speech`

Generates audio from text using the specified voice.

**Endpoint:** `POST /v1/audio/speech`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "input": "Hello, this is a test.",
  "voice": "alloy",
  "response_format": "wav",
  "speed": 1.0
}
```

**Parameters:**
- `input` (string, required): The text to convert to speech
- `voice` (string, required): The voice to use (see available voices below)
- `response_format` (string, optional): Audio format - `wav`, `mp3`, `opus`, `flac`, `aac` (default: `wav`)
- `speed` (number, optional): Speed of the audio (default: `1.0`)

**Available Voices:**
- Standard OpenAI voices: `alloy`, `echo`, `fable`, `nova`, `onyx`, `shimmer`
- Engine-specific voices: Use `/v1/voices` endpoint to get engine-specific voices

**Response:**
- Returns the audio file in the specified format
- Content-Type depends on the requested format

**Example using curl:**
```bash
curl -X POST http://localhost:7851/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Hello, this is a test.",
    "voice": "alloy",
    "response_format": "wav"
  }' \
  --output output.wav
```

### 2. List Models - `GET /v1/models`

Lists available TTS models/voices in OpenAI API format.

**Endpoint:** `GET /v1/models`

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "alloy",
      "object": "model",
      "created": 1234567890,
      "owned_by": "alltalk-openai"
    },
    {
      "id": "echo",
      "object": "model",
      "created": 1234567890,
      "owned_by": "alltalk-openai"
    },
    {
      "id": "engine_specific_voice",
      "object": "model",
      "created": 1234567890,
      "owned_by": "alltalk"
    }
  ]
}
```

**Example using curl:**
```bash
curl http://localhost:7851/v1/models
```

### 3. List Voices - `GET /v1/voices`

Lists available TTS voices in a simplified format compatible with various TTS clients.

**Endpoint:** `GET /v1/voices`

**Response:**
```json
{
  "voices": [
    "alloy",
    "echo",
    "fable",
    "nova",
    "onyx",
    "shimmer",
    "engine_specific_voice_1",
    "engine_specific_voice_2"
  ]
}
```

**Example using curl:**
```bash
curl http://localhost:7851/v1/voices
```

## Native AllTalk API Endpoints

### 4. Get Voices - `GET /api/voices`

Returns available voices for the current TTS engine.

**Endpoint:** `GET /api/voices`

**Response:**
```json
{
  "status": "success",
  "voices": ["voice1", "voice2", "voice3"]
}
```

### 5. Get RVC Voices - `GET /api/rvcvoices`

Returns available RVC voice models if RVC is enabled.

**Endpoint:** `GET /api/rvcvoices`

**Response:**
```json
{
  "status": "success",
  "rvcvoices": ["Disabled", "rvc_model_1", "rvc_model_2"]
}
```

### 6. Check Ready Status - `GET /api/ready`

Checks if the TTS engine is ready and initialized.

**Endpoint:** `GET /api/ready`

**Response:**
```json
{
  "status": "ready",
  "engine": "xtts",
  "model": "your_model_name"
}
```

### 7. Get Current Settings - `GET /api/currentsettings`

Returns comprehensive current engine settings and capabilities.

**Endpoint:** `GET /api/currentsettings`

**Response:**
```json
{
  "engine": "xtts",
  "model": "your_model_name",
  "voice": "default_voice",
  "language": "en",
  "capabilities": {
    "multivoice": true,
    "streaming": true,
    "low_vram": false
  }
}
```

### 8. Generate TTS (Standard) - `POST /api/tts-generate`

Standard TTS generation endpoint with form data.

**Endpoint:** `POST /api/tts-generate`

**Request Body (form-data):**
- `text_input`: Text to convert to speech
- `voice`: Voice to use
- `language`: Language code
- `output_file`: Output filename

**Response:**
```json
{
  "status": "success",
  "audio_file": "output.wav",
  "duration": 5.2
}
```

## Integration with moneyprinterturbo WebUI

### Connection Settings

When configuring moneyprinterturbo webui to connect to AllTalk TTS:

**API URL:** `http://alltalk-dev:7851/api` (or your server address)

**API Version:** v2 (OpenAI)

**Base Endpoint:** `/v1/audio/speech`

### Connection Test

The moneyprinterturbo webui will perform the following checks:

1. **URL Format Validation**: Validates the API URL format
2. **Network Connectivity**: Tests if the server is reachable
3. **Voices API**: Calls `/v1/voices` to get available voices
4. **Connection Summary**: Displays the connection status

### Expected Response

AllTalk TTS now properly implements the required endpoints:

- ✅ `/v1/audio/speech` - For TTS generation
- ✅ `/v1/models` - For listing available models
- ✅ `/v1/voices` - For listing available voices

### Troubleshooting

If you encounter connection issues:

1. **Check server status**: Ensure AllTalk TTS is running
   ```bash
   curl http://localhost:7851/api/ready
   ```

2. **Verify voices endpoint**: Test the voices endpoint
   ```bash
   curl http://localhost:7851/v1/voices
   ```

3. **Check TTS generation**: Test speech generation
   ```bash
   curl -X POST http://localhost:7851/v1/audio/speech \
     -H "Content-Type: application/json" \
     -d '{"input":"Test","voice":"alloy"}' \
     --output test.wav
   ```

4. **Review logs**: Check AllTalk TTS console output for errors

## Voice Mapping

AllTalk TTS maps OpenAI voice names to engine-specific voices:

- `alloy` → Engine voice 1
- `echo` → Engine voice 2
- `fable` → Engine voice 3
- `nova` → Engine voice 4
- `onyx` → Engine voice 5
- `shimmer` → Engine voice 6

You can customize these mappings using the `/api/openai-voicemap` endpoint.

## Error Handling

The API returns standard HTTP status codes:

- `200` - Success
- `400` - Bad request (invalid parameters)
- `404` - Not found (voice or model not found)
- `500` - Internal server error

Error responses follow this format:
```json
{
  "error": {
    "message": "Error description",
    "type": "error_type"
  }
}
```

## Audio Formats

Supported audio formats for TTS generation:

- `wav` - WAV format (default)
- `mp3` - MP3 format
- `opus` - Opus format
- `flac` - FLAC format
- `aac` - AAC format

## Rate Limiting

There are no built-in rate limits, but performance depends on:
- Your hardware (CPU/GPU)
- The TTS engine being used
- Audio length and format

## Streaming Support

AllTalk TTS supports streaming audio generation for real-time applications. Use the streaming endpoints:
- `GET /api/tts-generate-streaming`
- `POST /api/tts-generate-streaming`

## Additional Resources

- **GitHub Repository**: https://github.com/moltra/alltalk_tts
- **Wiki**: https://github.com/moltra/alltalk_tts/wiki
- **Issues**: https://github.com/moltra/alltalk_tts/issues

## Support

For issues or questions:
1. Check the built-in documentation in the Gradio interface
2. Review the GitHub Wiki
3. Open a support ticket on GitHub Issues
4. Check the Known Errors page in the wiki
