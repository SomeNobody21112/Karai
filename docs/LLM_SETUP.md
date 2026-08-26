# AI briefings and multilingual support — setup

Both features are **optional**. Without a key the product runs exactly as before: briefings
fall back to a deterministic template built from the same numbers, and the interface stays
in English. Adding a key upgrades the prose; it never changes the analysis.

## What you need

One thing: an **Anthropic API key** from <https://console.anthropic.com>.

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-..."
```

Set it in the shell that runs `mplads api`, then restart the API. Confirm with:

```bash
curl -s http://127.0.0.1:8000/api/languages
```

`"llm_available": true` means it is wired up.

## What it powers

| Feature | Endpoint | Without a key |
|---|---|---|
| National situation brief | `GET /api/insight/portfolio?lang=` | Deterministic template |
| Per-case briefing | `GET /api/insight/case/{ref}?lang=` | Deterministic template |
| Interface translation | `GET /api/strings?lang=` | Stays English |

12 languages: English, Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati, Kannada,
Malayalam, Punjabi, Odia, Assamese.

## Cost control

- **Interface strings are translated once per language and cached** to
  `data/artifacts/i18n/<lang>.json`. Delete a file to re-translate it.
- Briefings run at `effort: "low"` with adaptive thinking, and are short by construction.
- Model: `claude-opus-5`.

## The guardrails, and why they are not just a prompt

The model is handed **only figures the pipeline already computed** — never raw data it
could compute its own numbers from. `_case_facts()` is the whole surface it sees.

The system prompt forbids inventing figures and forbids asserting wrongdoing. But a prompt
is a request, so `_scrub()` enforces it afterwards: any output containing a word that
asserts wrongdoing is **discarded entirely** and the deterministic template is used
instead. A prompt is a request; a filter is a guarantee.

The UI always labels which one you are reading — `generated · claude-opus-5` or
`deterministic template`. That label is never hidden.
