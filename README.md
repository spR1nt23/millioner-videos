# millioner-videos

YouTube Shorts for the **Millioner_lifestyle** channel.

- `WORKFLOW.md` – full production method (setup, topic rules, past topics, script/visual rules, render, checks, titles, schedule, Studio upload).
- `tools/` – renderer (`mk.py`), setup (`setup.sh`, `requirements.txt`), scene specs (`specs/`).
- `videos/YYYY-MM-DD/` – rendered videos (+ `meta.json`), served via raw.githubusercontent.com for upload.

Quick start (clean Linux):
```bash
python3 -m venv .venv && . .venv/bin/activate
bash tools/setup.sh
python3 tools/mk.py tools/specs/spec_fee.json -o out
```
