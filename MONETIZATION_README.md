# AllTalk TTS v2 (moltra fork) — Component Analysis for MoneyPrinterTurbo

> **Purpose of this document:** AllTalk TTS is **not a separate product**. It
> is the **local TTS subsystem** of the MoneyPrinterTurbo (MPT) video
> automation stack. This document analyzes AllTalk as a *component* of MPT —
> what it contributes to the product, the licensing implications for the
> combined offering, and the risks/considerations that flow into MPT's
> monetization story. Intended to be pasted into another LLM alongside the
> MPT monetization README.

---

## 1. Role Inside the MPT Stack

AllTalk is the **voice-generation backend** that MPT calls over HTTP to turn
the AI-written script into narrated audio. In the MPT pipeline (`app/services/task.py`):

```
Script  →  TTS voiceover (THIS COMPONENT)  →  Subtitles (from TTS timing)
        →  Stock footage + BGM + FFmpeg compositing  →  Final MP4
```

MPT's `app/services/voice.py` detects an AllTalk endpoint by host/port
(any host containing `"alltalk"`, or port `7851`) and routes TTS requests
to it via the **OpenAI-compatible `/v1/audio/speech` API**. MPT treats
AllTalk as just another OpenAI-TTS-compatible provider — the only
difference is that it's self-hosted and costs $0 per character.

### 1.1 Why it exists in the stack
The default MPT TTS path is **OpenAI TTS** (paid, per-character). AllTalk
replaces that with a **self-hosted, GPU-local, voice-cloning-capable**
engine. This is what gives MPT its **$0-marginal-cost-per-video economics**
— the single most important number for any volume-based MPT business model.

### 1.2 Deployment shape
In the Docker stack, AllTalk runs as its own container (`alltalk-dev`,
port 7851) alongside the MPT API, MPT WebUI, Redis, and Ollama. MPT and
AllTalk are **separate OS processes communicating over a network HTTP API**
— they do not share memory, import each other's code, or link statically.
This boundary matters a great deal for licensing (§4).

---

## 2. What AllTalk Contributes to the MPT Product

| Capability | Value to MPT |
|---|---|
| **Local XTTS synthesis** | Eliminates OpenAI TTS per-character billing → $0/video |
| **Voice cloning (RVC + XTTS fine-tune)** | MPT can produce videos with a *consistent custom narrator voice* — a quality differentiator vs. generic OpenAI voices |
| **Multi-engine support (XTTS/VITS/Piper/Parler/F5)** | MPT can trade quality vs. speed vs. VRAM per deployment; Piper runs on CPU for low-end hosts |
| **OpenAI-compatible API** | MPT's voice.py already speaks this protocol — zero integration glue |
| **DeepSpeed + Low-VRAM modes** | MPT can run on a single consumer GPU alongside Ollama (the fork's auto-unload-Ollama-before-TTS logic in MPT exists precisely because they share one GPU) |
| **Bulk TTS generator** | Useful for MPT batch-generation workflows |
| **Narrator function (multi-voice)** | Enables character-dialogue videos, not just single-narrator |
| **Fine-tuning pipeline** | Path to a *proprietary MPT house voice* — a defensible asset (see §5) |

### 2.1 MPT-side integration specifics (this fork)
MPT's `voice.py` has dedicated AllTalk handling:
- Auto-detection of AllTalk endpoints (host/port sniff).
- No API key sent for AllTalk (self-hosted, no auth).
- **Text chunking for XTTS** — AllTalk/XTTS is prone to repeating phrases on
  long text, so MPT chunks text >200 chars into multiple requests and
  concatenates the audio. This is a real production fix, not a toy integration.
- Subtitles are derived from the TTS timing data returned by AllTalk.
- MPT's task pipeline **force-unloads Ollama from GPU before TTS** to free
  VRAM for AllTalk — they share one GPU.

This is a tight, battle-tested integration. The two are designed to run
together.

---

## 3. The moltra Fork's Refactors (why this AllTalk, not upstream)

The upstream `erew123/alltalk_tts` is a capable but loosely-structured
hobbyist project. This fork (`moltra/alltalk_tts`, ~1,055 commits) has been
hardened specifically to be a **reliable MPT backend**:

- **SRP refactors** of the XTTS engine (`__init__`, `generate_tts`,
  `handle_tts_method_change`, `setup`, `scan_models_folder`,
  `handle_deepspeed_change`) with dedicated test suites — fewer
  crashes during long MPT batch runs.
- **Custom exception hierarchy** + error-handler decorator — MPT gets
  predictable errors instead of bare tracebacks.
- **Hybrid on-demand model download (Option D)** — keeps the AllTalk
  container small and first-run fast; important because MPT users
  already download Ollama models and don't want a second multi-GB
  upfront pull.
- **Docker hardening** — separate dev/prod Dockerfiles, external storage
  paths for models/voices/outputs so the AllTalk container is stateless
  and shares a model cache with the host. This is what lets MPT's
  docker-compose stack work cleanly.
- **Pydantic v2 + Gradio 6.0 compatibility** fixes — keeps the stack on
  modern Python deps that align with MPT's own requirements.
- **Security fixes** — Gradio SSRF, Piper tuple-unpacking, XTTS voices.
  `CODE_REVIEW_ISSUES.md` documents 23 upstream issues (3 critical, 7
  high) including `allow_origins=["*"]` + credentials CORS and
  `shell=True` in diagnostics. **Several remain unfixed upstream** —
  this fork is safer to expose on a network.
- **Documentation** — DEEPWIKI, CODEMAP, API docs, TTS generation flow
  diagrams, voice-path flow, Docker quickstart. Makes operating the
  combined stack tractable.

**Net:** this fork is what makes the MPT+AllTalk combination deployable as
a unit rather than a pile of scripts.

---

## 4. Licensing Implications for the Combined MPT Product (the critical section)

This is the most important part of the analysis for MPT monetization.

### 4.1 The two licenses in play
- **MPT code:** MIT (permissive — do anything, keep your changes closed).
- **AllTalk code:** AGPL-3.0 (copyleft + network-use disclosure trigger).

### 4.2 The boundary is clean (good news)
MPT and AllTalk are **separate processes communicating over HTTP**. MPT
does not import AllTalk's Python code, link against it, or ship it inside
the MPT codebase. MPT just calls `POST http://alltalk-dev:7851/v1/audio/speech`.

Under the most common reading of the GPL/AGPL, **separate processes
communicating over a network API are not a single derivative work** —
this is the same principle that lets a proprietary web app call a
PostgreSQL server (GPL) or a Linux kernel (GPL) without becoming GPL.

So: **MPT-the-MIT-codebase does not become AGPL just because it calls
AllTalk over HTTP.** The two stay license-independent.

### 4.3 The AGPL still bites AllTalk itself (the catch)
AGPL §13's network-use disclosure trigger applies to **AllTalk itself**
when you host it. Concretely:

| MPT deployment model | AGPL consequence for AllTalk |
|---|---|
| **Self-hosted by you, internal use only** | No disclosure obligation. You are the user. |
| **Self-hosted by your customer** (you ship the docker-compose stack, they run it) | The *customer* is the AllTalk user; they receive the source anyway (it's in the container). No burden on you beyond shipping source you already have. **This is the cleanest commercial model.** |
| **Hosted MPT SaaS where AllTalk runs as a hidden backend** | **AGPL §13 triggers on AllTalk.** You must offer the AllTalk source (including any modifications you made to AllTalk) to every MPT SaaS user. Since the moltra fork is already public, the marginal burden is low *if you don't modify AllTalk*. **The moment you customize AllTalk (e.g. add a proprietary voice pipeline inside AllTalk itself), you must disclose those modifications to your SaaS users.** |
| **You modify AllTalk and ship it inside a closed MPT product** | Same — modifications to AllTalk must be offered to users under AGPL. |

### 4.4 Practical guidance for MPT monetization
1. **Keep AllTalk unmodified** in any hosted/SaaS MPT offering. Use it as
   a stock upstream-style component. Then AGPL §13 is satisfied by
   pointing users at the public repo — no real burden.
2. **If you need custom TTS behavior, put the customization in MPT
   (MIT), not in AllTalk (AGPL).** MPT's `voice.py` already does this —
   the chunking, the Ollama-unload orchestration, the subtitle extraction
   all live on the MIT side. Keep that pattern.
3. **If you build a proprietary voice pipeline, keep it as a separate
   service AllTalk calls out to**, or as fine-tuned *voice weights*
   (data, not code — see §5). Don't bake it into AllTalk's codebase.
4. **For on-prem/self-hosted MPT licenses, AGPL is a non-issue** — the
   customer gets source with the container anyway.

### 4.5 The XTTS weight license (second, independent risk)
Separate from the code license: **Coqui XTTS-v2 model weights are
non-commercial.** This affects MPT directly, because XTTS is the default
high-quality AllTalk engine and the one MPT's chunking logic is tuned for.

- **Commercial MPT deployment using XTTS-v2 weights likely requires a
  separate license from Coqui** (or its successor entity).
- **Workarounds:** switch AllTalk's default engine to a
  permissively-licensed one (Piper / VITS / Parler / F5 — each has its
  own weight license to verify), or obtain the Coqui commercial license,
  or train your own XTTS weights on licensed data.
- **This must be resolved before any commercial MPT deployment that uses
  AllTalk+XTTS.** It is not optional.

### 4.6 Voice-cloning legality (third risk)
AllTalk's RVC + XTTS fine-tuning can clone a real person's voice from a
few seconds of audio. **Cloning a real person's voice without consent is
illegal in many jurisdictions** (right of publicity, EU AI Act deepfake
provisions, US state voice-clone laws).

For MPT this means:
- Any "custom narrator voice" feature must include a **consent workflow**
  (the voice donor must affirmatively consent and you must retain proof).
- Don't market MPT with "clone any celebrity voice" messaging.
- A **library of consented, licensed, or synthetic voices** is the safe
  path — and is itself a monetizable asset (§5).

---

## 5. The One Genuinely Monetizable Asset AllTalk Contributes to MPT

**Proprietary fine-tuned voice weights.**

Voice weights are **data/model files**, not code. They are **not covered
by AllTalk's AGPL** (which covers the code) and **not covered by MPT's
MIT** (which covers the code). Their license is whatever you set —
proprietary by default if you train them yourself on licensed data.

This means: even in a hosted MPT SaaS where AGPL forces you to disclose
AllTalk code modifications, **your proprietary house voices remain
yours.** Customers pay for access to *the voice*, delivered through the
(open) AllTalk engine, called by the (open) MPT pipeline.

This is the cleanest defensible moat the AllTalk component contributes to
the MPT product:

- Train (or commission) a set of high-quality narrator voices on
  consented/licensed data.
- Offer them as the "premium voices" in an MPT SaaS tier.
- Free tier = generic open voices; paid tier = your proprietary voices.
- The voices are the product; the code is the delivery vehicle.

---

## 6. Risks AllTalk Introduces Into the MPT Product

| Risk | Severity | Mitigation |
|---|---|---|
| **AGPL §13 on hosted AllTalk** | Medium | Keep AllTalk unmodified in SaaS; put customization in MPT (MIT). On-prem model is unaffected. |
| **XTTS-v2 non-commercial weights** | **High** | Obtain Coqui commercial license, or switch default engine to a permissive one, or train own weights. **Must resolve before commercial launch.** |
| **Voice-cloning legality** | High | Consent workflow; synthetic/licensed voice library only; no celebrity-clone marketing. |
| **GPU co-location with Ollama** | Medium | Already mitigated in MPT (force-unload Ollama before TTS). Caps throughput on single-GPU hosts. |
| **Quality ceiling vs. ElevenLabs/OpenAI** | Medium | AllTalk is competitive on cost+control+cloning, not on absolute quality. Position MPT accordingly. |
| **Single-maintainer fork** | Low–Med | Bus factor; the fork is public so it can be forked again, but upstream-merge maintenance is on you. |
| **Upstream security holes** (CORS wildcard+creds, shell=True in diagnostics) | Medium | Several fixed in this fork; verify all are closed before public exposure. Don't expose AllTalk's port directly to the internet — put it behind MPT's API or a reverse proxy. |
| **Brand ("AllTalk")** | Low | Not customer-facing in an MPT product; MPT is the brand. |

---

## 7. Bottom Line (AllTalk as an MPT component)

AllTalk is **not a product to sell separately** — it is the **cost-engine
and voice-cloning layer** that makes MPT's $0-per-video economics work and
gives MPT a quality differentiator (custom narrator voices) over
generic-OpenAI-voice MPT deployments.

**For MPT monetization, AllTalk contributes three things:**

1. **The $0/video cost structure** — the foundation of any volume-based
   MPT business model. Without AllTalk (or equivalent local TTS), MPT
   pays OpenAI per character and the unit economics break at scale.

2. **A proprietary-voice moat** — fine-tuned voice weights are
   data, not code, so they escape both AGPL and MIT and can be sold as
   access through the open pipeline. This is the single most defensible
   asset the MPT+AllTalk combination can build.

3. **A licensing constraint to design around** — AGPL on AllTalk and
   non-commercial weights on XTTS-v2 must be handled. The clean path:
   - Keep AllTalk unmodified in any hosted offering.
   - Put all custom logic in MPT (MIT).
   - Resolve the XTTS weight license before launch (license, swap engine,
     or train own weights).
   - Sell **on-prem MPT licenses** (AGPL is a non-issue there) or
     **hosted MPT with proprietary voices as the paid tier**.

**The AllTalk component does not change the MPT monetization conclusion
from the MPT README** — it *enables* it. The $0/video economics and the
custom-voice moat are what make an MPT SaaS or on-prem license
defensible against someone just running vanilla upstream MPT with
OpenAI TTS. The licensing constraints are real but manageable with the
architecture discipline described in §4.4.

---

*Component analysis for MPT monetization. AllTalk code: AGPL-3.0
(see `LICENSE` in the AllTalk repo). MPT code: MIT. XTTS-v2 weights:
non-commercial (Coqui) — verify before commercial use.
AllTalk upstream: https://github.com/erew123/alltalk_tts
AllTalk fork:    https://github.com/moltra/alltalk_tts*
