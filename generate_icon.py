"""
Generate the Koda icon as a multi-resolution .ico for Windows.

Modern-minimal direction (Tesla / Linear / Vercel language):
  - Single deep-ink rounded square
  - One bold white K, geometric, no glow
  - No gradients, no waveforms, no borders
  - Reads cleanly at 16x16 (tray) through 512x512 (splash/store)

Run once to regenerate koda.ico when the mark changes.
"""

from PIL import Image, ImageDraw, ImageFont
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "koda.ico")
PREVIEW_PATH = os.path.join(SCRIPT_DIR, "koda_preview.png")

# Palette — deliberately tiny.
INK       = "#0a0a18"   # deep ink background (almost black w/ cool cast)
MARK      = "#ffffff"   # the K
ACCENT    = "#4a9eff"   # accent stroke under the K (subtle brand mark)
# State-overlay colors (used for runtime tray variants; not baked into .ico)
PULSE_RED = "#ef4444"   # recording
PULSE_AMB = "#f59e0b"   # processing


def _font(size):
    """Heaviest installed geometric sans we can reach. Bahnschrift SemiBold
    renders a wide, Tesla-flavored K; Segoe UI Black is the best fallback."""
    candidates = [
        ("C:/Windows/Fonts/bahnschrift.ttf", size),
        ("C:/Windows/Fonts/seguibl.ttf",     size),    # Segoe UI Black
        ("C:/Windows/Fonts/segoeuib.ttf",    size),    # Segoe UI Bold
        ("C:/Windows/Fonts/arialbd.ttf",     size),
    ]
    for path, sz in candidates:
        try:
            return ImageFont.truetype(path, sz)
        except Exception:
            continue
    return ImageFont.load_default()


def _draw_mark(draw, size, k_color=MARK, scale=1.0, shift_up=0.05):
    """Draw the K centered in a size×size canvas, with optional upward shift
    to leave room for an accent stroke beneath it."""
    font_size = int(0.68 * size * scale)
    font = _font(font_size)
    bbox = draw.textbbox((0, 0), "K", font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (size - tw) // 2 - bbox[0]
    ty = (size - th) // 2 - bbox[1] - int(shift_up * size)
    draw.text((tx, ty), "K", fill=k_color, font=font)


def generate_icon_image(size, status=None):
    """Render a single square icon at the requested pixel size.

    Supersamples 4× then downsamples for crisp edges. status=None produces
    the base mark; status='recording'|'processing' adds a status dot.
    """
    SS = 4  # supersample factor
    W = size * SS
    radius = int(0.22 * W)   # iOS-style radius (Apple/Linear language)

    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, W - 1, W - 1], radius=radius, fill=INK)

    _draw_mark(draw, W, k_color=MARK)

    # Accent stroke — a short, crisp horizontal line beneath the K. Subtle
    # brand mark that reads at 32px+ and disappears cleanly at 16px so the
    # tray icon stays pure K.
    if size >= 32:
        line_w = int(0.20 * W)
        line_h = max(2, int(0.025 * W))
        cx = W // 2
        ly = int(0.80 * W)
        draw.rounded_rectangle(
            [cx - line_w // 2, ly, cx + line_w // 2, ly + line_h],
            radius=line_h // 2,
            fill=ACCENT,
        )

    if status in ("recording", "processing"):
        dot_color = PULSE_RED if status == "recording" else PULSE_AMB
        r = int(0.11 * W)
        cx = W - int(0.22 * W)
        cy = W - int(0.22 * W)
        # Ring halo for depth (subtle, modern — not a glow blur).
        draw.ellipse([cx - r - SS, cy - r - SS, cx + r + SS, cy + r + SS],
                     fill=INK)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=dot_color)

    return img.resize((size, size), Image.LANCZOS)


# Back-compat: voice.py imports generate_status_icon for the tray state dot.
def generate_status_icon(size, dot_color=None):
    """Compatibility shim. Interprets legacy color hints as our new states."""
    if dot_color is None:
        return generate_icon_image(size)
    # Red-ish → recording; amber/yellow/green → processing; else base mark.
    hx = (dot_color or "").lstrip("#").lower()
    if hx.startswith(("ef", "f0", "ff0", "e6", "cc")) or "red" in (dot_color or "").lower():
        return generate_icon_image(size, status="recording")
    return generate_icon_image(size, status="processing")


def generate_ico():
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = [generate_icon_image(sz) for sz in sizes]
    largest = images[-1]
    others = images[:-1]
    largest.save(OUTPUT_PATH, format="ICO", append_images=others)
    print(f"Generated {OUTPUT_PATH}")
    print(f"  Resolutions: {', '.join(f'{sz}x{sz}' for sz in sizes)}")
    print(f"  Size: {os.path.getsize(OUTPUT_PATH) / 1024:.1f} KB")

    # Save a 512px preview PNG for visual review (not bundled with the exe).
    preview = generate_icon_image(512)
    preview.save(PREVIEW_PATH, format="PNG")
    print(f"Preview saved: {PREVIEW_PATH}")
    return OUTPUT_PATH


if __name__ == "__main__":
    generate_ico()
