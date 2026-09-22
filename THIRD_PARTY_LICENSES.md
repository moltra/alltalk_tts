# Third-Party Licenses and Notices

This document inventories the licenses of AllTalk TTS itself, the TTS engines
and model weights it can download at runtime, and the third-party binaries
bundled in this repository. Provided for compliance convenience - not legal advice.

## 1. AllTalk TTS code

- License: GNU Affero General Public License v3.0 (AGPL-3.0). See LICENSE.
- Upstream: erew123/alltalk_tts. Fork: moltra/alltalk_tts.
- If you modify AllTalk and let users interact with it over a network, AGPL
  section 13 requires offering those users the complete corresponding source.
  Keeping the fork public satisfies this for customer-self-hosted deployments.

## 2. TTS engines - code licenses vs model-weight licenses

Model weights are downloaded at runtime and carry their own licenses,
independent of the engine code. Weight licenses are also recorded per-model
in each engine available_models.json manifest.

### XTTS (xtts)
- Engine code: coqui-tts library, MPL-2.0.
- Weights (xttsv2_2.0.x): Coqui Public Model License (CPML) 1.0.0 - NON-COMMERCIAL.
- Do NOT ship or default-enable for commercial use without a separate Coqui license.

### F5-TTS / E2-TTS (f5tts)
- Engine code: MIT.
- Weights (f5tts_v1a, e2tts_v1a): CC-BY-NC-4.0 - NON-COMMERCIAL (Emilia dataset).
- Commercial use requires self-training on appropriately licensed data.

### Parler TTS (parler)
- Engine code: Apache-2.0. Weights (parler-tts-mini-v1, -large-v1): Apache-2.0.
- Commercial use: permitted.

### VITS (vits)
- Engine code: MPL-2.0 (coqui-tts).
- Weights: Apache-2.0 per the coqui model index for the bundled vctk model;
  verify each additional model before enabling it commercially.
- Commercial use: permitted for the bundled vctk model.

### Piper (piper)
- Engine code and bundled binary: MIT.
- Voices: per-voice licenses (rhasspy/piper-voices; mostly MIT or CC-BY,
  a few restricted). Check the specific voices you ship or enable.
- Commercial use: generally permitted - this is the default engine.

### RVC voice conversion (rvc)
- Code: MIT. Pretrained components (HuBERT, ContentVec, RMVPE, FCPE):
  permissive research licenses but murky provenance - low-quality audit trail.
- Caution: voice-converting a real person raises separate publicity issues.

### Whisper (transcription helper)
- Code and weights: MIT. Commercial use permitted.

## 3. Third-party binaries committed to this repository

- system/win_ffmpeg/ffmpeg.exe - PROBABLE GPL BUILD (typical Windows static
  ffmpeg builds include GPL components such as libx264). If GPL,
  redistribution requires the license text plus a source offer.
  ACTION REQUIRED: verify build provenance; consider an LGPL build or a
  download-at-install step. Tracked as a follow-up in
  tasks/commercial-readiness.md.

- system/espeak-ng/*.msi and system/tts_engines/piper/engine/espeak-ng.dll
  - GPL-3.0 (espeak-ng). Shipping these binaries requires GPL notices and a
  source offer. Invoking as a subprocess does not affect your code, but the
  redistribution obligations still apply. Source: https://github.com/espeak-ng/espeak-ng

- system/tts_engines/piper/engine/piper.exe, piper_phonemize.dll - MIT (Piper).
  Source: https://github.com/rhasspy/piper

- system/tts_engines/piper/engine/onnxruntime*.dll - MIT (ONNX Runtime).
  Source: https://github.com/microsoft/onnxruntime

## 4. Voice samples

- voices/ ships generic synthetic samples only (female_0x, male_0x).
- Celebrity voice-clone samples were removed from this distribution
  (see commit history). Do not re-add recognizable-person voice samples
  without documented consent - right-of-publicity and voice-clone laws
  apply (EU AI Act deepfake provisions; e.g. CA AB-1836, TN ELVIS Act).













































































































