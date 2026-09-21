# Commercial Readiness - Spec and Task Tracker

**Branch:** feature/commercial-readiness - branched from Claude_testing @ ee243c4
**Goal:** make the repo safe to ship as a customer-self-hosted TTS backend for a commercial product.
**Authoritative findings:** BUSINESS_READINESS_REVIEW.md

## Boundaries
- Do NOT push to remote. Do NOT modify LICENSE - it stays AGPL-3.0.
- Do NOT delete or commit untracked generated outputs in config/app/outputs/ - gitignore them instead.
- Do NOT refactor global-state or bare-except issues from CODE_REVIEW_ISSUES.md - out of scope, follow-up.
- Gradio 4 to 5 upgrade is OUT OF SCOPE - documented follow-up.
- Keep changes backward compatible: no-auth default equals current behavior.

## Work items and file ownership - all items executed by coordinator

### A. License metadata
- pyproject.toml: license text MIT to AGPL-3.0-only; classifier MIT License to GNU Affero General Public License v3.
- Verify no README or docs claim MIT for this project.
- Acceptance: pyproject metadata agrees with LICENSE.

### B. Remove celebrity voice clones - legal blocker
- git rm tracked files in voices/: Arnold, Clint_Eastwood CC3, David_Attenborough CC3, Morgan_Freeman CC3, Morgan Freeman CC3.txt, James_Earl_Jones CC3, Sophie_Anderson CC3. Keep female_0x and male_0x.
- Update references in config/engines/xtts/model_settings.json and config/engines/f5tts/model_settings.json.
- Acceptance: git ls-files voices/ shows no celebrity names; no tracked file references them.

### C. Commercially-safe default engine plus non-commercial gating
- Default engine xtts to piper in: Dockerfile, Dockerfile.dev, Dockerfile.prod, docker-build.sh, docker-build-dev.sh, docker-build-prod.sh, docker-compose.dev.yml, config/system/tts_engines.json, docs DOCKER_README.md, MODEL_DOWNLOAD_README.md, DOCKER_DEV_README.md.
- Add license and commercial_use fields to model entries in system/tts_engines/xtts and f5tts available_models.json plus config/engines copies. Schema is lenient - plain json.load.
- Add visible NON-COMMERCIAL warning to HELP_PAGE in system/tts_engines/xtts/help_content.py and f5tts/help_content.py.
- Add THIRD_PARTY_LICENSES.md at repo root: code licenses, weight licenses, bundled binaries - ffmpeg.exe flagged probable GPL build needing verification, espeak-ng GPLv3, onnxruntime MIT, piper MIT.
- Acceptance: fresh clone defaults to piper; non-commercial engines visibly labeled.

### D. Optional API-key auth
- config/app/config.py: api_key str field in AlltalkConfigApiDef plus ALLTALK_API_KEY env override, same pattern as ALLTALK_ALLOWED_ORIGINS.
- config/app/confignew.json: api_key empty string under api_def. Update docker-init-config.sh heredoc template too.
- tts_server.py: verify_api_key dependency accepting X-API-Key or Authorization Bearer, hmac.compare_digest, 401 with OpenAI error shape on /v1/ routes. Protected generation endpoints: /v1/audio/speech, /api/tts-generate, /api/tts-generate-streaming GET and POST, /api/previewvoice/. Gradio UI and docs unaffected - separate process.
- tests/test_api_key_auth.py: disabled mode, missing key 401, wrong key 401, correct key via both headers.
- Docs: API_DOCUMENTATION.md, TTS_API_DOCUMENTATION.md, DOCKER_README.md ALLTALK_API_KEY.
- Acceptance: empty key means zero behavior change; set key returns 401 without it on protected routes only.

### E. CI fixes
- .github/workflows/python-ci.yml: run pytest tests/ and test/, fix bogus --cov=com, add non-blocking pip-audit step.
- Add .github/dependabot.yml for pip and github-actions.
- Acceptance: workflow YAML valid; covers both suites.

### F. Repo hygiene
- .gitignore: add config/app/outputs/, logs/, temp/, star.backup entries.
- git rm committed backups: config/system/new_engines.json.backup, config/system/tts_engines.json.backup, config/system/tts_engines.json.force_backup, system/new_engines.json.backup, system/tts_engines/xtts/model_engine.py.backup.
- delete_output_wavs: code expects Disabled or X Days at script.py line 877; Enabled is invalid, so leave Disabled and document the retention recommendation.
- Acceptance: outputs logs temp ignored; no backup files tracked.

### G. Dependency and security documentation
- Run pip-audit against system/requirements/requirements_standalone.txt; record findings in SECURITY_NOTES.md. No mass upgrades.

## Follow-ups - explicitly out of scope
- Gradio 5 upgrade - CVE class path traversal and SSRF in 4.44.x.
- CODE_REVIEW_ISSUES.md high-severity structural items - global state, bare excepts.
- ffmpeg.exe provenance verification or possible LGPL rebuild or download-at-install.
- Purging celebrity voices from git history - removed going forward; history purge needs force-push, maintainer decision.
- Rate limiting and multi-tenancy - single-tenant appliance by design.

## Verification
- pytest tests/ and test/ green; ruff check clean on changed files; config JSONs valid.































































































































