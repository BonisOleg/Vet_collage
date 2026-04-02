"""
Update all .jpg / .png image references to .webp in CSS and HTML template files.

Run AFTER export_figma_images.py has successfully downloaded all WebP files.

    python tools/update_image_refs.py [--dry-run]

With --dry-run it prints what would change without writing anything.
"""

import re
import sys
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

DRY_RUN = "--dry-run" in sys.argv

# ─── Files to update ──────────────────────────────────────────────────────────

CSS_FILES = [
    BASE_DIR / "static" / "css" / "pages" / "home1.css",
    BASE_DIR / "static" / "css" / "pages" / "home2.css",
    BASE_DIR / "static" / "css" / "pages" / "home3.css",
    BASE_DIR / "static" / "css" / "components.css",
    BASE_DIR / "static" / "css" / "pages" / "contact.css",
]

HTML_FILES = list((BASE_DIR / "templates").rglob("*.html"))

# ─── Replacement logic ────────────────────────────────────────────────────────

# Matches image filenames ending in .jpg / .jpeg / .png inside url() or src attributes.
# Captures the stem so we can swap just the extension.
IMG_PATTERN = re.compile(
    r"((?:/static/images/|{% static 'images/)[^\s'\"]+?)"  # path prefix + name
    r"\.(jpg|jpeg|png)"                                      # old extension
    r"(?=['\"\s\)])",                                        # followed by quote/space/paren
    re.IGNORECASE,
)


def should_convert(path_str: str) -> bool:
    """Skip SVG files and dynamic template variables like {{ ... }}."""
    return "{{" not in path_str and ".svg" not in path_str.lower()


def process_file(filepath: Path, *, images_dir: Path) -> int:
    """Replace old extensions with .webp only where the .webp file actually exists.
    Returns the number of replacements made."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as exc:
        print(f"  ⚠️  Cannot read {filepath}: {exc}")
        return 0

    replacements = 0

    def replacer(m: re.Match) -> str:
        nonlocal replacements
        prefix = m.group(1)      # e.g. /static/images/hero-photo-1
        old_ext = m.group(2)     # e.g. jpg

        if not should_convert(prefix):
            return m.group(0)

        # Derive the filesystem path to the .webp counterpart
        rel_path = prefix.split("/images/", 1)[-1]  # hero-photo-1
        # Strip Django static tag fragments if present
        rel_path = rel_path.replace("{% static 'images/", "").rstrip("'")
        webp_path = images_dir / (rel_path + ".webp")

        if webp_path.exists():
            replacements += 1
            return prefix + ".webp"
        else:
            # .webp not yet on disk — keep original, warn
            print(f"    ⚠️  WebP not found, keeping original: {rel_path}.{old_ext}")
            return m.group(0)

    new_content = IMG_PATTERN.sub(replacer, content)

    if new_content != content:
        if DRY_RUN:
            print(f"  [dry-run] {filepath.relative_to(BASE_DIR)}: {replacements} replacement(s)")
        else:
            filepath.write_text(new_content, encoding="utf-8")
            print(f"  ✅  {filepath.relative_to(BASE_DIR)}: {replacements} replacement(s)")

    return replacements


# ─── Fix blog/list.html inline style (rules violation) ───────────────────────

def fix_blog_hero_inline_style(filepath: Path, images_dir: Path) -> None:
    """
    blog/list.html has an inline style= on the hero section.
    Move background-image to a CSS variable approach by replacing it with
    a data attribute instead.

    The inline style:
        style="background-image: url('{% static 'images/blog-card-photo.jpg' %}')"
    becomes:
        data-bg="{% static 'images/blog-card-photo.webp' %}"

    A tiny JS snippet in blog.js handles setting the CSS variable.
    """
    if not filepath.exists():
        return

    content = filepath.read_text(encoding="utf-8")

    inline_style_pattern = re.compile(
        r"""style="background-image:\s*url\('({% static '[^']+' %})'\)"\s*""",
        re.IGNORECASE,
    )

    def _fix(m: re.Match) -> str:
        static_tag = m.group(1)
        # Convert .jpg/.png to .webp in the tag
        static_tag_webp = re.sub(r"\.(jpg|jpeg|png)'", ".webp'", static_tag, flags=re.IGNORECASE)
        return f'data-bg="{static_tag_webp}" '

    new_content = inline_style_pattern.sub(_fix, content)

    if new_content != content:
        if DRY_RUN:
            print(f"  [dry-run] Fixed inline style in {filepath.relative_to(BASE_DIR)}")
        else:
            filepath.write_text(new_content, encoding="utf-8")
            print(f"  ✅  Fixed inline style → data-bg in {filepath.relative_to(BASE_DIR)}")


# ─── Ensure blog JS handles data-bg ──────────────────────────────────────────

BLOG_BG_JS = """\
/* Set hero background from data-bg attribute (avoids inline style= rule) */
document.querySelectorAll('[data-bg]').forEach(function (el) {
  el.style.backgroundImage = "url('" + el.dataset.bg + "')";
});
"""


def ensure_blog_bg_js(base_dir: Path) -> None:
    blog_js = base_dir / "static" / "js" / "pages" / "blog.js"
    if not blog_js.exists():
        return
    content = blog_js.read_text(encoding="utf-8")
    if "data-bg" in content:
        return  # already patched
    if DRY_RUN:
        print(f"  [dry-run] Would append data-bg handler to {blog_js.relative_to(base_dir)}")
        return
    blog_js.write_text(content.rstrip() + "\n\n" + BLOG_BG_JS, encoding="utf-8")
    print(f"  ✅  Appended data-bg handler to {blog_js.relative_to(base_dir)}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    images_dir = BASE_DIR / "static" / "images"
    total = 0

    print(f"\n{'─'*50}")
    print("CSS files")
    print(f"{'─'*50}")
    for f in CSS_FILES:
        if f.exists():
            total += process_file(f, images_dir=images_dir)
        else:
            print(f"  ⚠️  Not found: {f.relative_to(BASE_DIR)}")

    print(f"\n{'─'*50}")
    print("HTML templates")
    print(f"{'─'*50}")
    for f in sorted(HTML_FILES):
        total += process_file(f, images_dir=images_dir)

    # Fix blog inline style
    blog_list = BASE_DIR / "templates" / "pages" / "blog" / "list.html"
    print(f"\n{'─'*50}")
    print("Inline style fix (blog/list.html)")
    print(f"{'─'*50}")
    fix_blog_hero_inline_style(blog_list, images_dir)
    ensure_blog_bg_js(BASE_DIR)

    print(f"\n{'='*50}")
    print(f"Total replacements: {total}")
    if DRY_RUN:
        print("(DRY RUN — no files were modified)")
    print()


if __name__ == "__main__":
    main()
