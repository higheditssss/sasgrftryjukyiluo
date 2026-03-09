#!/usr/bin/env python3
# fetch_kick.py — ia datele de pe Kick și salvează în public/data.json
# Folosește KickApi (fără token, fără autorizare)

import json
import os
from datetime import datetime, timezone

CHANNEL = "razvwi"
OUTPUT  = "public/data.json"

def fmt_duration(seconds):
    if not seconds:
        return "—"
    try:
        s = int(float(str(seconds)))
        h = s // 3600
        m = (s % 3600) // 60
        sec = s % 60
        if h > 0:
            return f"{h}:{m:02d}:{sec:02d}"
        return f"{m}:{sec:02d}"
    except:
        return "—"

def fmt_thumb(t):
    if not t:
        return None
    if isinstance(t, str):
        return t
    if isinstance(t, dict):
        return t.get("src") or t.get("url") or t.get("original")
    return None

def main():
    print(f"📡 Se preiau datele pentru {CHANNEL}...")

    try:
        from kickapi import KickAPI
    except ImportError:
        print("❌ KickApi nu e instalat. Rulează: pip install KickApi")
        exit(1)

    kick = KickAPI()

    # ── Channel ───────────────────────────────────────────
    channel_out = {"followers": 0, "isLive": False, "viewers": 0}
    try:
        ch = kick.channel(CHANNEL)
        channel_out = {
            "followers": getattr(ch, "followers_count", 0) or 0,
            "isLive":    getattr(ch, "is_live", False) or False,
            "viewers":   getattr(ch, "viewer_count", 0) or 0,
        }
        print(f"  ✅ Canal: {channel_out['followers']} followeri, {'🔴 LIVE' if channel_out['isLive'] else 'offline'}")
    except Exception as e:
        print(f"  ⚠ Canal error: {e}")

    # ── VOD-uri ───────────────────────────────────────────
    videos_out = []
    try:
        ch = kick.channel(CHANNEL)
        raw_videos = getattr(ch, "videos", []) or []
        for v in raw_videos:
            videos_out.append({
                "id":       str(getattr(v, "id", "") or getattr(v, "uuid", "")),
                "type":     "vod",
                "title":    getattr(v, "session_title", None) or getattr(v, "title", None) or "Stream",
                "date":     str(getattr(v, "created_at", "") or ""),
                "duration": fmt_duration(getattr(v, "duration", None)),
                "views":    getattr(v, "views", 0) or 0,
                "category": getattr(getattr(v, "category", None), "name", None) or "Just Chatting",
                "thumb":    fmt_thumb(getattr(v, "thumbnail", None)) or "https://placehold.co/480x270/0a0a0a/53fc18?text=VOD",
                "url":      f"https://kick.com/video/{getattr(v, 'uuid', None) or getattr(v, 'id', '')}",
            })
        print(f"  ✅ VOD-uri: {len(videos_out)}")
    except Exception as e:
        print(f"  ⚠ Videos error: {e}")

    # ── Clipuri ───────────────────────────────────────────
    clips_out = []
    try:
        ch = kick.channel(CHANNEL)
        raw_clips = getattr(ch, "clips", []) or []
        for c in raw_clips:
            clip_id = getattr(c, "clip_id", None) or getattr(c, "id", "")
            clips_out.append({
                "id":       str(clip_id),
                "type":     "clip",
                "title":    getattr(c, "title", None) or "Clip",
                "date":     str(getattr(c, "created_at", "") or ""),
                "duration": fmt_duration(getattr(c, "duration", None)),
                "views":    getattr(c, "views", 0) or getattr(c, "view_count", 0) or 0,
                "category": getattr(getattr(c, "category", None), "name", None) or "Just Chatting",
                "thumb":    getattr(c, "thumbnail_url", None) or getattr(c, "thumbnail", None) or "https://placehold.co/480x270/0a0a0a/53fc18?text=Clip",
                "url":      f"https://kick.com/{CHANNEL}?clip={clip_id}",
            })
        print(f"  ✅ Clipuri: {len(clips_out)}")
    except Exception as e:
        print(f"  ⚠ Clips error: {e}")

    # ── Salvează ──────────────────────────────────────────
    output = {
        "channel": channel_out,
        "videos":  videos_out,
        "clips":   clips_out,
        "fetched": datetime.now(timezone.utc).isoformat(),
    }

    os.makedirs("public", exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Salvat în {OUTPUT}")
    print(f"   {len(videos_out)} VOD-uri, {len(clips_out)} clipuri\n")

if __name__ == "__main__":
    main()
