# Breakfix Log — VPS Git Divergence

**Date:** 2026-09-27  
**System:** zangji (Hostinger VPS 72.62.97.23)  
**Severity:** Medium — RAG stale, SSH briefly unavailable  

---

## What Broke

1. **SSH temporarily unavailable** — VPS was reachable by ping but SSH timed out for ~15 min
2. **Git divergence** — VPS `/opt/zangbot` was 5 commits behind GitHub AND had a local uncommitted change (`scripts/breakfix-logger.sh` staged but not pushed)
3. **RAG stale** — still at 92 chunks, missing 4 new fleet reference guides (zangpachi, zangagotchi, synology, flipper, lora)

---

## Root Cause

### SSH outage
Likely transient — SSH service recovered on its own. No config changes made. Probable cause: high memory spike from RAG re-index or Docker operation caused brief SSH daemon stall.

### Git divergence
VPS had its own local git history that diverged from GitHub master:
- VPS commit: `abe985b chore: initial VPS git tracking - router v0.2.0 + RAG indexed`
- This commit existed only on VPS, never pushed to GitHub
- `breakfix-logger.sh` was staged locally on VPS but never committed or pushed
- Mac (source of truth) pushed 5 new commits that VPS couldn't fast-forward merge

---

## Fix Applied

```bash
# 1. Save VPS-only file before reset
cp scripts/breakfix-logger.sh /tmp/breakfix-logger.sh.bak

# 2. Fetch and hard reset to match GitHub
git fetch origin
git reset --hard origin/master

# 3. Restore saved file (now untracked, safe)
cp /tmp/breakfix-logger.sh.bak scripts/breakfix-logger.sh

# 4. Re-index RAG with new guides
/opt/zangbot/venv/bin/python3 rag/vector-db-init.py

# 5. Restart router to load new index
systemctl restart zangbot-router
```

---

## Result

| Check | Before | After |
|---|---|---|
| Git sync | 5 commits behind, diverged | ✅ In sync with GitHub master |
| RAG chunks | 92 | ✅ 116 |
| RAG categories | 7 | ✅ 12 (added: zangpachi, zangagotchi, synology, flipper, lora) |
| Router status | Stale RAG | ✅ Running, 116 chunks loaded |
| SSH | Flaky | ✅ Stable |

---

## Prevention

**Rule:** VPS is a DEPLOYMENT TARGET, not a development machine.  
- Never make git commits directly on VPS  
- All changes go: Mac → GitHub → VPS pull  
- VPS pull command: `git pull --ff-only origin master`  
- If VPS has local changes, stash or discard — Mac is source of truth  

**Add to deployment checklist:**
```bash
# VPS update procedure (run from Mac after push)
ssh root@72.62.97.23 "cd /opt/zangbot && git pull --ff-only origin master && systemctl restart zangbot-router"
```
