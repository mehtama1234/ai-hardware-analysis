#!/usr/bin/env python3
"""Capture GPUMODE YouTube metadata and captions.

This follows the transcript shape used by sibling course repos: raw VTT files,
clean text, cue JSON, metadata JSON, and a single transcript index.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CHANNEL_URL = "https://www.youtube.com/@GPUMODE/videos"
COURSE_SLUG = "gpumode"
RAW = ROOT / "raw-material" / "youtube"
PLAYLIST_MANIFEST = RAW / "gpumode-channel.json"
BASE = RAW / "transcripts" / COURSE_SLUG
RAW_VTT = BASE / "raw-vtt"
CLEAN = BASE / "clean"
CUES = BASE / "cues"
META = RAW / "metadata" / COURSE_SLUG
INDEX = RAW / "transcript-index.json"
SUMMARY = RAW / "summary.json"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=check)


def load_json_from_output(output: str) -> dict[str, Any]:
    for line in reversed(output.splitlines()):
        candidate = line.strip()
        if candidate.startswith("{") and candidate.endswith("}"):
            return json.loads(candidate)
    raise ValueError("yt-dlp did not return a JSON object")


def slugify(value: str) -> str:
    value = value.replace("|", " ")
    value = re.sub(r"[^\w .:()&+#/-]+", "", value, flags=re.UNICODE)
    value = re.sub(r"\s+", " ", value).strip()
    return value[:130] or "untitled"


def parse_seconds(value: str) -> float:
    parts = value.split(":")
    if len(parts) == 2:
        minutes, rest = parts
        return int(minutes) * 60 + float(rest)
    hours, minutes, rest = parts
    return int(hours) * 3600 + int(minutes) * 60 + float(rest)


def clean_caption_line(line: str) -> str:
    line = re.sub(r"<[^>]+>", "", line)
    replacements = {
        "&amp;": "&",
        "&lt;": "<",
        "&gt;": ">",
        "&quot;": '"',
        "&#39;": "'",
    }
    for old, new in replacements.items():
        line = line.replace(old, new)
    return re.sub(r"\s+", " ", line).strip()


def parse_vtt(path: Path) -> tuple[str, list[dict[str, Any]]]:
    cues: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    text_lines: list[str] = []
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line == "WEBVTT" or line.startswith(("Kind:", "Language:", "NOTE")):
            continue
        if "-->" in line:
            start, end = [part.strip().split(" ")[0] for part in line.split("-->", 1)]
            current = {
                "start": start,
                "end": end,
                "start_seconds": parse_seconds(start),
                "end_seconds": parse_seconds(end),
                "text": [],
            }
            cues.append(current)
            continue
        if re.match(r"^\d+$", line):
            continue
        cleaned = clean_caption_line(line)
        if not cleaned:
            continue
        if current is not None and (not current["text"] or current["text"][-1] != cleaned):
            current["text"].append(cleaned)
        text_lines.append(cleaned)

    compact_cues: list[dict[str, Any]] = []
    for cue in cues:
        joined = " ".join(cue["text"]).strip()
        if joined:
            compact_cues.append({**cue, "text": joined})

    deduped: list[str] = []
    for line in text_lines:
        if not deduped or deduped[-1] != line:
            deduped.append(line)
    return "\n".join(deduped).strip() + "\n", compact_cues


def ensure_dirs() -> None:
    for path in [RAW, RAW_VTT, CLEAN, CUES, META]:
        path.mkdir(parents=True, exist_ok=True)


def capture_channel() -> dict[str, Any]:
    result = run(["yt-dlp", "--flat-playlist", "--dump-single-json", CHANNEL_URL])
    manifest = load_json_from_output(result.stdout)
    manifest.pop("epoch", None)
    PLAYLIST_MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def videos_from_manifest() -> list[dict[str, Any]]:
    if not PLAYLIST_MANIFEST.exists():
        return []
    manifest = json.loads(PLAYLIST_MANIFEST.read_text(encoding="utf-8"))
    videos: list[dict[str, Any]] = []
    for index, entry in enumerate(manifest.get("entries", []), 1):
        video_id = entry.get("id")
        if not video_id:
            continue
        videos.append(
            {
                "index": entry.get("playlist_index") or index,
                "id": video_id,
                "title": entry.get("title") or f"GPUMODE lesson {index}",
                "url": entry.get("url") or f"https://www.youtube.com/watch?v={video_id}",
                "duration": entry.get("duration"),
                "view_count": entry.get("view_count"),
            }
        )
    return videos


def choose_vtt(video_id: str) -> Path | None:
    candidates = sorted(RAW_VTT.glob(f"*{video_id}*.vtt"))
    if not candidates:
        return None
    ranked: list[tuple[int, Path]] = []
    for path in candidates:
        name = path.name
        if ".en." in name:
            rank = 0
        elif ".en-orig." in name or ".en-US." in name:
            rank = 1
        else:
            rank = 5
        ranked.append((rank, path))
    return sorted(ranked, key=lambda item: (item[0], item[1].name))[0][1]


def download_transcripts() -> None:
    output = str(RAW_VTT / "%(playlist_index|001)03d-%(id)s-%(title).130B.%(ext)s")
    cmd = [
        "yt-dlp",
        "--ignore-errors",
        "--skip-download",
        "--write-info-json",
        "--write-subs",
        "--write-auto-subs",
        "--sub-langs",
        "en,en-US,en-orig,en.*",
        "--sub-format",
        "vtt",
        "-o",
        output,
        CHANNEL_URL,
    ]
    print(run(cmd, check=False).stdout)
    for info in RAW_VTT.glob("*.info.json"):
        target = META / info.name
        if target.exists():
            target.unlink()
        info.replace(target)


def rebuild_index() -> None:
    records: list[dict[str, Any]] = []
    for video in videos_from_manifest():
        video_id = video["id"]
        vtt = choose_vtt(video_id)
        transcript_status = "missing"
        clean_path = None
        cue_path = None
        word_count = 0
        cue_count = 0
        if vtt is not None:
            text, cues = parse_vtt(vtt)
            clean_path = CLEAN / f"{video['index']:03d}-{video_id}-{slugify(video['title'])}.txt"
            cue_path = CUES / f"{video['index']:03d}-{video_id}.json"
            clean_path.write_text(text, encoding="utf-8")
            cue_path.write_text(json.dumps(cues, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            word_count = len(re.findall(r"\b\w+\b", text))
            cue_count = len(cues)
            transcript_status = "available" if word_count >= 50 else "unusable"
        meta_files = sorted(META.glob(f"*{video_id}*.info.json"))
        records.append(
            {
                "course_slug": COURSE_SLUG,
                "source_url": CHANNEL_URL,
                "index": video["index"],
                "id": video_id,
                "title": video["title"],
                "url": video["url"],
                "duration": video.get("duration"),
                "view_count": video.get("view_count"),
                "transcript_status": transcript_status,
                "source_tier": "youtube-caption" if transcript_status == "available" else "metadata-only",
                "raw_vtt": str(vtt.relative_to(ROOT)) if vtt else None,
                "clean_txt": str(clean_path.relative_to(ROOT)) if clean_path else None,
                "cues_json": str(cue_path.relative_to(ROOT)) if cue_path else None,
                "metadata_json": str(meta_files[0].relative_to(ROOT)) if meta_files else None,
                "word_count": word_count,
                "cue_count": cue_count,
            }
        )

    summary = {
        "course_slug": COURSE_SLUG,
        "course_title": "GPUMODE",
        "source_url": CHANNEL_URL,
        "generated_at": now(),
        "video_count": len(records),
        "transcript_count": sum(1 for row in records if row["transcript_status"] == "available"),
        "word_count": sum(row["word_count"] for row in records),
        "videos": records,
    }
    INDEX.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"wrote {INDEX.relative_to(ROOT)} with {summary['transcript_count']}/"
        f"{summary['video_count']} transcripts and {summary['word_count']} words"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata-only", action="store_true", help="Capture video list and build metadata-only index.")
    parser.add_argument("--summary-only", action="store_true", help="Rebuild index from files already on disk.")
    args = parser.parse_args()
    ensure_dirs()
    if not args.summary_only:
        capture_channel()
        if not args.metadata_only:
            download_transcripts()
    rebuild_index()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
