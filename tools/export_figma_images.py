"""
Figma → WebP export script.

Usage:
    FIGMA_TOKEN=<your_personal_access_token> python tools/export_figma_images.py

How to get a Figma Personal Access Token:
    Figma → Account Settings (click avatar) → Security → Personal access tokens → Generate new token
"""

import os
import sys
import time
import shutil
import requests
from pathlib import Path
from io import BytesIO

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow не встановлено. Виконайте: pip install Pillow")

# ─── Config ────────────────────────────────────────────────────────────────────

FIGMA_TOKEN = os.environ.get("FIGMA_TOKEN", "")
FILE_KEY    = "CNsW1Wif7PQCZDaAIGmfci"

IMAGES_DIR  = Path(__file__).parent.parent / "static" / "images"
TMP_DIR     = Path(__file__).parent.parent / "static" / "images" / "_tmp_figma"

SCALE       = 2      # export at 2x for retina
WEBP_QUALITY = 85    # 0-100 (lossy); photos look good at 82-88

# ─── Node ID → target filename mapping ────────────────────────────────────────
# Each tuple: (figma_node_id, target_path_relative_to_IMAGES_DIR, use_lossless)
# use_lossless=True  → for icons/logos with transparency (PNGs with alpha)
# use_lossless=False → for photos (smaller files)

IMAGE_MAP = [
    # ── Hero section (головна сторінка) ──────────────────────────────────────
    ("242:2337", "hero-photo-1.webp",          False),
    ("242:2340", "hero-photo-2.webp",          False),
    ("248:7592", "hero-bg-texture-1.webp",     False),
    ("248:7594", "hero-bg-texture-2.webp",     False),  # vector with grain texture fill
    ("248:7598", "mission-bg.webp",            False),
    ("248:7613", "mission-stamp.webp",         True),   # stamp has transparency

    # ── Expertise section ─────────────────────────────────────────────────────
    ("248:7600", "expertise-texture.webp",     False),
    ("242:2551", "expertise-photo-1.webp",     False),
    ("242:2552", "expertise-photo-2.webp",     False),
    ("242:2553", "expertise-photo-3.webp",     False),

    # ── Popular courses carousel (home page) ──────────────────────────────────
    ("250:7615", "course-photo-1.webp",        False),
    ("250:7625", "course-photo-2.webp",        False),

    # ── Membership section ────────────────────────────────────────────────────
    ("242:2491", "membership-photo.webp",      False),
    ("242:2493", "membership-photo-2.webp",    False),

    # ── Services / Consultation ───────────────────────────────────────────────
    ("242:2603", "services-row1-photo.webp",   False),
    ("242:2627", "services-row2-photo.webp",   False),
    ("242:2652", "consultation-left-photo.webp", False),

    # ── Education section ─────────────────────────────────────────────────────
    ("252:7683", "edu-bg-photo.webp",          False),
    ("242:2675", "edu-portrait.webp",          False),

    # ── Blog section previews (home page) ────────────────────────────────────
    ("242:2745", "blog-preview-1.webp",        False),
    ("242:2746", "blog-preview-2.webp",        False),
    ("242:2747", "blog-preview-3.webp",        False),
    ("242:2721", "blog-card-photo.webp",       False),  # large featured photo

    # ── Blog page — article card placeholder photos ────────────────────────────
    ("350:1150", "blog-owners-nutrition.webp", False),  # 2nd article card fill

    # ── About page — hero textures (same style as home hero) ─────────────────
    ("248:7592", "about-bg-texture-1.webp",   False),   # reuse same texture node
    ("248:7594", "about-bg-texture-2.webp",   False),   # reuse same grain node

    # ── About page — ellipses ─────────────────────────────────────────────────
    ("242:2386", "about-ellipse-top.webp",     True),   # has transparency
    ("242:2387", "about-ellipse-bottom.webp",  True),

    # ── About page — timeline ─────────────────────────────────────────────────
    ("511:156",  "about-timeline-line.webp",   True),   # vertical timeline line+dots
    ("242:2412", "about-timeline-photo-1.webp", False),
    ("242:2413", "about-timeline-photo-2.webp", False),
    ("242:2414", "about-timeline-photo-3.webp", False),
    ("242:2415", "about-timeline-photo-4.webp", False),

    # ── About page — founders & team ─────────────────────────────────────────
    ("261:9202", "about-founder-1.webp",        False),
    ("261:9218", "about-founder-2.webp",        False),
    ("242:2416", "about-team-bg.webp",          False),
    ("242:2882", "about-team-1.webp",           False),
    ("242:2888", "about-team-2.webp",           False),
    ("242:2894", "about-team-3.webp",           False),

    # ── Courses page ──────────────────────────────────────────────────────────
    ("335:1666", "courses-hero-bg.webp",        False),  # MISSING — hero background
    ("313:658",  "courses-photo-1.webp",        False),
    ("313:675",  "courses-photo-2.webp",        False),
    ("313:692",  "courses-photo-3.webp",        False),

    # ── Webinars page ─────────────────────────────────────────────────────────
    ("336:1958", "webinars-hero-bg.webp",       False),  # MISSING — hero background
    ("242:7220", "webinar-photo-1.webp",        False),
    ("254:8410", "webinar-photo-2.webp",        False),
    ("254:8421", "webinar-photo-3.webp",        False),

    # ── Footer decorations ────────────────────────────────────────────────────
    # These nodes may be vector solid fills (not image fills).
    # The script will skip them gracefully if Figma returns null for their URL.
    ("254:7766", "footer/bg_1.webp",            True),
    ("254:7765", "footer/bg_2.webp",            True),
]

# ─── Helpers ──────────────────────────────────────────────────────────────────

HEADERS = {"X-Figma-Token": FIGMA_TOKEN}


def export_nodes_to_urls(node_ids: list[str]) -> dict[str, str]:
    """Calls Figma API to get signed export URLs for the given node IDs."""
    # Pass ids as a raw comma-separated string; requests will URL-encode if needed.
    # Figma REST API accepts both '242:2337' and '242-2337' formats in query string.
    resp = requests.get(
        f"https://api.figma.com/v1/images/{FILE_KEY}",
        headers=HEADERS,
        params={"ids": ",".join(node_ids), "format": "png", "scale": str(SCALE)},
        timeout=60,
    )
    if not resp.ok:
        print(f"    HTTP {resp.status_code}: {resp.text[:300]}")
        resp.raise_for_status()
    data = resp.json()
    if data.get("err"):
        raise RuntimeError(f"Figma export error: {data['err']}")
    return data.get("images", {})


def download_png(url: str, dest: Path) -> None:
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    dest.write_bytes(resp.content)


def png_to_webp(src: Path, dest: Path, lossless: bool = False) -> None:
    with Image.open(src) as img:
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA" if img.mode == "RGBA" else "RGB")
        dest.parent.mkdir(parents=True, exist_ok=True)
        if lossless:
            img.save(dest, "WEBP", lossless=True)
        else:
            img.save(dest, "WEBP", quality=WEBP_QUALITY, method=6)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    if not FIGMA_TOKEN:
        sys.exit(
            "\n❌  FIGMA_TOKEN not set.\n"
            "Run:  FIGMA_TOKEN=<your_token> python tools/export_figma_images.py\n"
            "Get a token at: Figma → Account Settings → Security → Personal access tokens\n"
        )

    TMP_DIR.mkdir(parents=True, exist_ok=True)

    # Build target_map: node_id → list of (rel_path, lossless) tuples
    # A single node can produce multiple output files (e.g. about-bg-texture reuses hero nodes).
    target_map: dict[str, list[tuple[str, bool]]] = {}
    for node_id, rel_path, lossless in IMAGE_MAP:
        target_map.setdefault(node_id, []).append((rel_path, lossless))

    # Unique node IDs for the API request
    node_ids = list(target_map.keys())

    print(f"\n📦 Exporting {len(node_ids)} nodes from Figma…\n")

    # Figma allows up to 100 IDs per request; batch in chunks of 50 to be safe.
    BATCH = 50
    url_map: dict[str, str] = {}
    for i in range(0, len(node_ids), BATCH):
        batch = node_ids[i : i + BATCH]
        print(f"  → Requesting batch {i // BATCH + 1} ({len(batch)} nodes)…")
        urls = export_nodes_to_urls(batch)
        url_map.update(urls)
        time.sleep(0.5)  # be polite to the API

    print(f"\n  Got {len(url_map)} export URLs.\n")

    success, skipped, failed = 0, 0, 0

    for node_id, targets in target_map.items():
        # Figma returns node IDs with dashes or colons depending on the API version
        figma_key = node_id
        if figma_key not in url_map:
            figma_key = node_id.replace(":", "-")
        if figma_key not in url_map:
            figma_key = node_id.replace("-", ":")

        img_url = url_map.get(figma_key)
        if not img_url:
            for rel_path, _ in targets:
                print(f"  ⚠️  No URL for {node_id} ({rel_path}) — skipping")
                skipped += 1
            continue

        tmp_png = TMP_DIR / f"{node_id.replace(':', '_')}.png"
        try:
            download_png(img_url, tmp_png)
        except Exception as exc:
            for rel_path, _ in targets:
                print(f"  ❌  {node_id} → {rel_path}: download failed: {exc}")
                failed += 1
            continue

        for rel_path, lossless in targets:
            dest_webp = IMAGES_DIR / rel_path
            try:
                print(f"  ⬇️  {node_id} → {rel_path} …", end=" ", flush=True)
                png_to_webp(tmp_png, dest_webp, lossless=lossless)
                size_kb = dest_webp.stat().st_size // 1024
                print(f"✅  ({size_kb} KB)")
                success += 1
            except Exception as exc:
                print(f"❌  {exc}")
                failed += 1

    # Cleanup temp files
    shutil.rmtree(TMP_DIR, ignore_errors=True)

    print(f"\n{'─'*50}")
    print(f"✅ Success: {success}  ⚠️ Skipped: {skipped}  ❌ Failed: {failed}")
    print(f"Images saved to: {IMAGES_DIR}\n")


if __name__ == "__main__":
    main()
