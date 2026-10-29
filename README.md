# İti Qovan Qrupu — complaint text generator

Static single-page site. No build step, no dependencies.

```
index.html                     root redirect -> /iti-qovan/
iti-qovan/index.html           page (UI in Azerbaijani, complaint templates in English inside <script>)
iti-qovan/audio/meqsed.mp3     TTS of the purpose text (generate with tools/tts.py)
tools/purpose_az.txt  purpose text, source for TTS — keep in sync with #p-goal in index.html
tools/tts.py          Azure Speech REST → MP3 (stdlib only)
```

## 1. Generate audio

```bash
export AZURE_SPEECH_KEY=<key>
export AZURE_SPEECH_REGION=<region>        # e.g. westeurope
python3 tools/tts.py                       # female: az-AZ-BanuNeural (default)
python3 tools/tts.py --voice az-AZ-BabekNeural   # male
```

## 2. Publish on GitHub Pages

```bash
git init -b main
git add .
git commit -m "Initial release"
gh repo create iti-qovan --public --source=. --push
gh api -X POST repos/{owner}/iti-qovan/pages -f "source[branch]=main" -f "source[path]=/"
```

Without `gh`: create a public repo `iti-qovan` on github.com → upload files →
Settings → Pages → Source: *Deploy from a branch*, Branch: `main` / `/ (root)` → Save.

Live: https://mekhti.github.io/iti-qovan/ (root redirects there)

## Editing

- Purpose text: `#p-goal` in `iti-qovan/index.html` + `tools/purpose_az.txt`, then re-run `tts.py`.
- Complaint types: `<option>` in `#type` (`iti-qovan/index.html`) + matching key in `TYPES` (script).
- Template phrases: `INTROS`, `TYPES[*].desc`, `POLICY_LINES`, `CLOSINGS`.
- X forms: `FORM_BASE` + `FORM_SECTION[type]` + `/me` or `/somebody-else`.
- Complaint text is limited to `MAX_TEXT` (280, X form limit); links are not part of the text, they go to the form's URL fields.
- Bypass browser cache after updates: hard refresh, or rename `iti-qovan/audio/meqsed.mp3` → `meqsed-v2.mp3` and update `src`.
