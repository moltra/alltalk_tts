# Security Notes

Generated for the commercial-readiness pass (branch feature/commercial-readiness).

## Dependency audit status

pip-audit could not be executed in the review sandbox (no Python runtime
available). It MUST be run before shipping:

    pip install pip-audit
    pip-audit -r system/requirements/requirements_standalone.txt
    pip-audit -r system/requirements/requirements_f5tts.txt
    pip-audit -r system/requirements/requirements_parler.txt

A non-blocking pip-audit step now runs in CI
(.github/workflows/python-ci.yml), and Dependabot is configured for pip
and github-actions.

## Known advisories (from BUSINESS_READINESS_REVIEW.md)

- gradio==4.44.1 - published CVEs in the path traversal / SSRF class.
  A Gradio 4 to 5 upgrade is a deliberate follow-up, OUT OF SCOPE for this
  branch. Interim mitigation: keep the Gradio port (7852) off the public
  internet - bind or proxy only on trusted networks.
- fastapi==0.112.2, pydantic==2.10.6, coqui-tts==0.24.3, pillow==10.3.0 -
  check pip-audit output for advisories against these pins.

## Security posture notes for deployment

- API auth is OPTIONAL (api_key in confignew.json, or ALLTALK_API_KEY env var).
  Empty means disabled. Enable it, or put the API behind an authenticating
  reverse proxy, before exposing it beyond localhost.
- CORS defaults to localhost origins only - do not widen.
- Diagnostics and admin endpoints can inspect the environment and run pip
  commands; restrict network access to them.
- delete_output_wavs remains Disabled by default; generated audio may
  contain customer text. Set an "X Days" retention value for deployments
  with data-retention requirements.
- Bundled binaries: see THIRD_PARTY_LICENSES.md (ffmpeg.exe flagged as a
  probable GPL build pending verification; espeak-ng GPLv3).

## Follow-ups (out of scope here)

- Gradio 5 or later upgrade.
- Container image scan (trivy) before shipping Docker images.
- CODE_REVIEW_ISSUES.md structural items (global state, bare excepts).
- Run pip-audit and record its full output here.
