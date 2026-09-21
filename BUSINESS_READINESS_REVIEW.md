# AllTalk TTS (moltra fork) — Business / Self-Hosted Readiness Review

**Review date:** 2026-09-21
**Repo:** `https://github.com/moltra/alltalk_tts` (fork of `erew123/alltalk_tts`)
**Branch reviewed:** `Claude_testing` @ `ee243c4`
**Intended use:** Self-hosted TTS backend for a commercial product ("text → speech" in a business environment, deployed on the end user's infrastructure).

> **Disclaimer:** This is a technical and licensing review, not legal advice. The
> licensing section identifies obligations and risks, but a lawyer should
> sign off before commercial distribution.

---

## 1. Executive Summary

| Question | Answer |
|---|---|
| Can this repo be self-hosted inside a customer's business environment? | **Yes**, with caveats. It is a functional, API-first TTS server with Docker support. |
| Can it be used commercially as-is? | **Not without work.** The default/best TTS engine weights (XTTS-v2, F5-TTS) are **non-commercial**, and the repo ships celebrity voice-clone samples. Both must be addressed before any commercial deployment. |
| Is the code license a problem? | **Manageable.** AllTalk is **AGPL-3.0**. In a *customer-self-hosted* model this is nearly a non-issue — the customer receives the source anyway. It only bites if you host it as a hidden SaaS backend or ship modified AllTalk code closed-source. |
| Is there a license bug to fix? | **Yes.** `pyproject.toml` declares **MIT**, but `LICENSE` is **AGPL-3.0**. Fix this before packaging/distributing. |
| Overall verdict | **Usable as a self-hosted component** if you (a) restrict the engine to commercially-licensed weights (Piper / Parler / VITS, or self-trained), (b) remove the celebrity voice files, (c) fix the license metadata, and (d) treat the API as **unauthenticated internal-only** — never expose it directly to the internet. |

---

## 2. What This Repo Is

- **Upstream:** `erew123/alltalk_tts` — a hobbyist-grade but feature-rich FastAPI/Gradio TTS server wrapping multiple engines.
- **This fork (~1,055 commits):** substantially hardened for use as a backend service (refactored XTTS engine, custom exception hierarchy, on-demand model downloads, Docker dev/prod split, security fixes, extensive docs).
- **Entry points:**
  - `tts_server.py` (~137 KB) — FastAPI API server + Gradio UI launcher (port 7851 API, 7852 UI by default).
  - `script.py` (~215 KB) — monolithic startup/config/diagnostics.
  - `tts_mem.py` (~80 KB) — experimental Multi-Engine Manager.
  - `finetune.py` (~183 KB) — XTTS fine-tuning UI/pipeline.
- **Engines** (`system/tts_engines/`): `xtts`, `vits`, `piper`, `parler`, `f5tts`, `rvc` (voice conversion), plus a `template-tts-engine` for adding more.
- **APIs:** native JSON API + **OpenAI-compatible `POST /v1/audio/speech`** — the endpoint a commercial app would call.

---

## 3. Repository State Assessment

### 3.1 Strengths

- **Docker-ready**: `Dockerfile`, `Dockerfile.dev`, `Dockerfile.prod`, `docker-compose.dev.yml`, build/start scripts, external volume mounts for models/voices/outputs → stateless container.
- **Hybrid on-demand model download** (commit `ead3f68`) — no multi-GB upfront pull; models fetched per-engine on first use.
- **Security fixes already applied in this fork** (upstream still has some):
  - CORS no longer wildcard — `tts_server.py:261` uses `config.cors_settings.allowed_origins` (defaults to localhost origins in `config/app/confignew.json`).
  - `shell=True` subprocess and `os.system()` removed from `diagnostics.py`; regression tests exist in `tests/test_subprocess_security.py`.
  - Gradio SSRF and Piper tuple-unpacking fixes (per `MONETIZATION_README.md` / commit `b0620c7`).
- **Pydantic-based config** with file locking and hot-reload.
- **Documentation is unusually good** for a fork: `API_DOCUMENTATION.md`, `TTS_API_DOCUMENTATION.md`, `DEEPWIKI.md`, `CODEMAP.md`, Docker guides.
- **Text filtering/input sanitization** on the API (`api_allowed_filter` regex, `api_max_characters`, `api_text_filtering`).

### 3.2 Weaknesses / Risks

| Area | Finding | Severity for business use |
|---|---|---|
| **Authentication** | **None.** The API and OpenAI-compatible endpoint have no API key, token, or auth middleware. Anyone who can reach port 7851 can generate TTS, hit admin endpoints, and invoke the Gradio UI. | **High** — fine on localhost/trusted LAN; must sit behind a reverse proxy (nginx/Traefik + auth) or on an isolated network segment before any real deployment. |
| **Network exposure** | Server binds `0.0.0.0` by design (`GRADIO_SERVER_NAME="0.0.0.0"` in Dockerfile). Proxy module exists (TLS termination on 443/444) but is off by default. | High if exposed; fine behind firewall/proxy. |
| **Code quality** | Prior full review (`CODE_REVIEW_ISSUES.md`) found **23 issues: 3 critical, 7 high** — global state everywhere, bare `except:`, `print()`-instead-of-logging, ~5K-line files. Criticals are fixed in this fork; high-severity structural issues largely remain. | Medium — affects maintainability/reliability more than correctness. |
| **Test coverage** | New suite in `tests/` (API endpoints, CORS, XTTS, Piper, Gradio, state manager, subprocess security, integration). But CI (`python-ci.yml`) only runs `pytest test` (the legacy single-file suite) and has a stale `--cov=com` flag — **the new tests are not exercised in CI.** | Medium — fix CI to run `tests/`. |
| **Dependency age** | Pins: `gradio==4.44.1`, `fastapi==0.112.2`, `pydantic==2.10.6`, `coqui-tts==0.24.3`. Gradio 4.44.x has published CVEs (path traversal/SSRF class). No `pip-audit`/Dependabot in CI. | Medium — run `pip-audit` and plan a Gradio 5.x upgrade before production. |
| **Repo hygiene** | • **Celebrity voice-clone samples committed to git** (`voices/`: "Arnold", "Clint_Eastwood", "David_Attenborough", "Morgan_Freeman", "James_Earl_Jones", "Sophie_Anderson" WAVs + reference texts) — inherited from upstream.<br>• `.backup` files committed (`*.json.backup`, `model_engine.py.backup`).<br>• 400+ untracked generated outputs in `config/app/outputs/`; `logs/` and `temp/` root-owned.<br>• Bundled binaries committed: `ffmpeg.exe`, `espeak-ng` MSIs, Piper engine DLLs/EXE. | Medium (hygiene) / **High (legal)** for the voice files — see §5. |
| **Single maintainer** | Upstream author has stepped back (README notice); this fork is essentially a solo project. No signed releases; Docker publish workflow is manual/release-triggered. | Medium — you own maintenance. Budget for it. |
| **Platform support** | Windows + Linux first-class; AMD GPU experimental; Mac theoretical/no GPU accel. | Low–Medium depending on customer hardware. |

### 3.3 Operational notes for self-hosting

- **Hardware:** realistically needs an NVIDIA GPU for XTTS/F5/Parler quality+speed; **Piper runs fine on CPU** and is the practical choice for low-end customer hardware.
- **VRAM management** exists (low-VRAM mode, DeepSpeed option, engine unload) — relevant if the customer's box shares a GPU with other services.
- **State on disk:** models (`models/`), voices (`voices/`), outputs — all volume-mountable; container itself can be stateless.
- **Rate limiting / multi-tenancy:** none. It's a single-tenant appliance; queueing is via the experimental MEM (`tts_mem.py`) — treat as beta.
- **Output lifecycle:** `delete_output_wavs` is `Disabled` by default — outputs accumulate; enable cleanup or mount an ephemeral volume.

---

## 4. Security Checklist Before Business Deployment

- [ ] Put AllTalk behind a reverse proxy with auth (or restrict to localhost + SSH tunnel / private network). **Do not expose 7851/7852 to the internet.**
- [ ] Keep CORS restricted (current default is localhost-only — good; don't widen it).
- [ ] Enable TLS via the built-in proxy module or your reverse proxy; verify `proxy_settings.cert_validation`.
- [ ] Run `pip-audit` / `uvx safety` against `system/requirements/*.txt`; upgrade Gradio past 4.44.x advisories.
- [ ] Turn on `delete_output_wavs` or cron-clean `outputs/` (generated audio may contain customer text → data-retention implications).
- [ ] Review the diagnostics/admin endpoints — they can execute pip commands / inspect the environment; ensure they're not reachable by untrusted users.
- [ ] Scan container image (`trivy`) if shipping the Docker build to customers.

---

## 5. Licensing Review — what you actually need to do

### 5.1 The code: AGPL-3.0 (and a bug to fix)

- `LICENSE` = **GNU AGPL v3** (added upstream 2023-12-19, inherited by this fork). All fork modifications are equally AGPL — there is no dual licensing, and the fork owner cannot remove it from inherited code.
- ⚠️ **`pyproject.toml` says `license = {text = "MIT"}` and `License :: OSI Approved :: MIT License`.** This contradicts `LICENSE` and was introduced by the fork's tooling commit (`7ba28b4`). If you package this via `pip`/PyPI metadata, it would falsely advertise MIT.
  - **Action:** change to `license = {text = "AGPL-3.0-only"}` and classifier `"License :: OSI Approved :: GNU Affero General Public License v3"`. This is the one concrete "fix the license" item.

**What AGPL means per deployment model:**

| Model | Obligation |
|---|---|
| **Customer self-hosts AllTalk** (your stated plan) | Cleanest path. The customer is the "user interacting remotely"; they receive the source inside the container/repo. You must not strip the license or copyright notices, and if *you* modify AllTalk, those modifications must be offered to users under AGPL — easiest satisfied by keeping your fork public (it already is). |
| Your internal use only | No disclosure obligation. |
| You host it as a hidden SaaS backend | **AGPL §13 triggers** — you must offer the complete AllTalk source (incl. your modifications) to every user who interacts with it over the network. Keep AllTalk unmodified and link to the public repo, or accept disclosure. |
| Proprietary app calling it | **Not affected** — a separate process talking HTTP to AllTalk is not a derivative work (same principle as an app talking to PostgreSQL/GPL). Keep your commercial code on your side of the HTTP boundary — do not import/link AllTalk code into it. |

**Rules of thumb:** keep custom logic (chunking, orchestration, voice management) in *your* application, not inside AllTalk. Voice *weights/presets* you train are data, not AGPL'd code — they can stay proprietary.

### 5.2 The real blocker: model weight licenses (independent of code license)

Each engine's *weights* are downloaded at runtime and have their own licenses:

| Engine / model | Code license | Weight license | Commercial use? |
|---|---|---|---|
| **XTTS-v2** (default, `xttsv2_2.0.x`) | MPL-2.0 (coqui-tts lib) | **Coqui Public Model License — NON-COMMERCIAL** | ❌ No, without a separate Coqui license. The repo even downloads `LICENSE.txt` with the model. |
| **F5-TTS / E2-TTS** (`f5tts_v1a`, `e2tts_v1a`) | MIT | **CC-BY-NC-4.0** (Emilia dataset) | ❌ No. (Training your own F5 weights on licensed data IS fine — code is MIT.) |
| **Parler-TTS** (`parler-tts-mini-v1`, `-large-v1`) | Apache-2.0 | **Apache-2.0** | ✅ Yes — fully open release. |
| **VITS** (`tts_models--en--vctk--vits`, etc.) | MPL-2.0 | **Apache-2.0** (per coqui `.models.json`; verify each model you enable — CV variants vary) | ✅ Mostly yes; verify per-model. |
| **Piper** | MIT (engine + bundled binary) | **Per-voice** (rhasspy/piper-voices: mostly MIT/CC-BY, a few restricted) | ✅ Generally yes — check the specific voices you ship. |
| **RVC** (voice conversion) | MIT | Pretraineds: HuBERT/ContentVec/RMVPE/FCPE — permissive research licenses, but provenance is murky | ⚠️ Probably fine; low-quality audit trail. Voice-converting a real person raises separate publicity issues. |
| **Whisper** (transcription) | MIT | MIT | ✅ Yes. |

**Bottom line on weights:** for a commercial deployment, set the default engine to **Piper** (CPU-friendly, cleanest) or **Parler/VITS**, and **do not ship or default-enable XTTS-v2 or F5-TTS weights** unless you obtain a commercial license (Coqui commercial licensing for XTTS; F5 requires self-training on commercially-licensed data — the authors have confirmed self-trained weights on your own data are fine).

### 5.3 Bundled third-party binaries committed to the repo

`git ls-files` shows these binaries tracked in git — redistributing them has obligations:

| File | License | Obligation |
|---|---|---|
| `system/win_ffmpeg/ffmpeg.exe` | Almost certainly a **GPL** build (typical Windows static builds include GPL components like libx264) | If GPL: must provide license text + offer/corresponding source when you redistribute. **Verify provenance; consider replacing with a download-at-install step or an LGPL build.** |
| `system/espeak-ng/*.msi`, `system/tts_engines/piper/engine/espeak-ng.dll` | **GPL-3.0** (espeak-ng) | Same GPL redistribution obligations; running it as a subprocess is fine, but shipping the binaries requires notices/source offer. |
| `system/tts_engines/piper/engine/piper.exe`, `piper_phonemize.dll`, `onnxruntime*.dll` | MIT (Piper, ONNX Runtime) | Keep copyright notices. |

**Action:** add a `THIRD_PARTY_LICENSES` / `NOTICE` file listing every bundled binary + downloaded model with its license and source URL. This is standard practice and cheap insurance.

### 5.4 The celebrity voice files — remove them

`voices/` (git-tracked, inherited from upstream) contains voice-clone samples named **Arnold, Clint Eastwood, David Attenborough, Morgan Freeman, James Earl Jones, Sophie Anderson** — recognizable public figures.

- Shipping these in a commercial product is a **right-of-publicity / voice-clone-law risk** (EU AI Act deepfake provisions; US state laws e.g. CA AB-1836, TN ELVIS Act) regardless of code license.
- **Action:** delete them (and `git rm` + ideally purge history, or at minimum remove going forward), replace with consented/synthetic voices. Your product's voice-cloning feature itself needs a **consent workflow** for any real-person voice.

### 5.5 License action checklist

1. **Fix `pyproject.toml`**: MIT → `AGPL-3.0-only` (license field + classifier).
2. **Keep the repo/fork public or ship source** — satisfies AGPL for customer-self-hosted deployments with zero extra work.
3. **Do not remove copyright/license notices**; add a `NOTICE`/`THIRD_PARTY_LICENSES` file.
4. **Remove celebrity voice samples** from `voices/` (and from any image/package you ship).
5. **Choose a commercially-clean default engine**: Piper (per-voice check) or Parler/VITS. Gate XTTS/F5 behind a "non-commercial / bring-your-own-license" flag or remove them from the distribution you ship.
6. **Verify `ffmpeg.exe` build license**; if GPL, keep notices + source offer, or swap to an LGPL build / runtime download.
7. **If you ever offer hosted TTS**: either run stock AllTalk unmodified (point users to source) or get ready to publish modifications under AGPL.
8. **Voice cloning:** ship with a consent/attestation step and keep records; don't market "clone any celebrity voice."

---

## 6. Recommended Remediation (prioritized)

**Before any customer ships with it:**
1. Remove celebrity voices; fix `pyproject.toml` license metadata.
2. Set default engine to Piper or Parler; disable/document XTTS & F5 as non-commercial.
3. Never expose the API port directly; document the reverse-proxy requirement.

**Before production hardening:**
4. Add optional API-key auth to `/v1/audio/speech` (or enforce it at the proxy).
5. Fix CI to run `tests/` (not just `test/`), correct the coverage flag, add `pip-audit` + Dependabot.
6. Upgrade Gradio ≥5.x (or backport advisories); pin + audit all requirements.
7. Enable output cleanup; add a retention setting.

**Ongoing:**
8. Track upstream selectively; keep fork public (it's also your AGPL compliance mechanism).
9. Add `NOTICE`/third-party license inventory; re-audit whenever adding an engine/model.

---

## 7. Appendix — Key Files

| Purpose | File |
|---|---|
| License (AGPL-3.0) | `LICENSE` |
| License metadata bug | `pyproject.toml` (MIT → should be AGPL-3.0) |
| API server | `tts_server.py` (`/v1/audio/speech` at line ~1252; CORS at ~261) |
| Config defaults | `config/app/confignew.json` |
| Engine model manifests (download URLs) | `system/tts_engines/*/available_models.json` |
| Dependency pins | `system/requirements/requirements_standalone.txt` (+ `_f5tts`, `_parler`) |
| Prior security/quality review | `CODE_REVIEW_ISSUES.md` |
| MPT-oriented licensing analysis | `MONETIZATION_README.md` (uncommitted; §4–5 still accurate) |
| Docker | `Dockerfile`, `Dockerfile.prod`, `docker-compose.dev.yml`, `DOCKER_QUICKSTART.md` |
| CI | `.github/workflows/python-ci.yml`, `publish-docker-v2.yml` |
| Celebrity voices to remove | `voices/` (Arnold, Clint_Eastwood, David_Attenborough, Morgan_Freeman, James_Earl_Jones, Sophie_Anderson) |
| Bundled binaries to audit | `system/win_ffmpeg/ffmpeg.exe`, `system/espeak-ng/*.msi`, `system/tts_engines/piper/engine/*` |
