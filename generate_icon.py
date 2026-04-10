"""
Generate professional Koda icon as a multi-resolution .ico file.

Design: Dark navy rounded square with a bold white "K" and a subtle
audio waveform accent. Clean, modern, reads well at 16x16 through 256x256.

Run once to generate koda.ico — used by PyInstaller, Inno Setup, and tray.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import math

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "koda.ico")

# Brand colors
BG_DARK = "#0f1023"       # Deep navy background
BG_GRADIENT = "#1a1a3e"   # Slightly lighter navy for gradient feel
ACCENT = "#4a9eff"        # Bright blue accent (waveform, glow)
ACCENT_DIM = "#2d6bc4"    # Dimmer blue for subtle elements
TEXT_WHITE = "#f0f0f8"    # Slightly warm white for the K
DOT_GREEN = "#2ecc71"     # Status dot green (used at runtime, not baked in)


def _get_font(size):
    """Get Bahnschrift Bold or best available sans-serif font."""
    candidates = [
        "bahnschrift.ttf",
        "C:/Windows/Fonts/bahnschrift.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def generate_icon_image(size):
    """Generate a single icon image at the given pixel size."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    s = size / 256  # Scale factor (256 is our design resolution)

    # --- Background: rounded rectangle with subtle gradient effect ---
    corner_radius = int(48 * s)
    # Base dark fill
    draw.rounded_rectangle(
        [0, 0, size - 1, size - 1],
        radius=corner_radius,
        fill=BG_DARK,
    )

    # Subtle lighter region in upper portion for depth
    if size >= 48:
        gradient_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        gradient_draw = ImageDraw.Draw(gradient_img)
        gradient_draw.rounded_rectangle(
            [0, 0, size - 1, size - 1],
            radius=corner_radius,
            fill=BG_GRADIENT,
        )
        # Fade: only blend top portion
        for y in range(size):
            alpha = max(0, int(40 * (1 - y / size)))
            for x in range(size):
                r, g, b, a = gradient_img.getpixel((x, y))
                if a > 0:
                    gradient_img.putpixel((x, y), (r, g, b, alpha))
        img = Image.alpha_composite(img, gradient_img)
        draw = ImageDraw.Draw(img)

    # --- Subtle border glow ---
    if size >= 64:
        draw.rounded_rectangle(
            [0, 0, size - 1, size - 1],
            radius=corner_radius,
            outline=ACCENT_DIM,
            width=max(1, int(1.5 * s)),
        )

    # --- Audio waveform accent (bottom area, behind the K) ---
    if size >= 48:
        wave_y_center = int(200 * s)
        wave_amplitude = int(12 * s)
        wave_width = int(180 * s)
        wave_x_start = int(38 * s)
        num_bars = 7
        bar_width = max(1, int(4 * s))
        bar_spacing = wave_width / (num_bars + 1)

        # Heights for each bar (symmetric audio waveform pattern)
        bar_heights = [0.3, 0.6, 0.9, 1.0, 0.9, 0.6, 0.3]
        for i, h in enumerate(bar_heights):
            bx = int(wave_x_start + bar_spacing * (i + 1))
            bh = int(wave_amplitude * h)
            alpha_val = int(60 + 40 * h)  # More opaque for taller bars
            bar_color = (*_hex_to_rgb(ACCENT), alpha_val)

            bar_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            bar_draw = ImageDraw.Draw(bar_img)
            bar_draw.rounded_rectangle(
                [bx - bar_width // 2, wave_y_center - bh,
                 bx + bar_width // 2, wave_y_center + bh],
                radius=max(1, bar_width // 2),
                fill=bar_color,
            )
            img = Image.alpha_composite(img, bar_img)
            draw = ImageDraw.Draw(img)

    # --- The "K" letterform ---
    font_size = int(160 * s)
    font = _get_font(font_size)

    bbox = draw.textbbox((0, 0), "K", font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = (size - tw) // 2 - bbox[0]
    ty = (size - th) // 2 - bbox[1] - int(16 * s)  # Shift up slightly to balance with waveform

    # Subtle glow behind the K
    if size >= 64:
        glow_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_img)
        glow_draw.text((tx, ty), "K", fill=(*_hex_to_rgb(ACCENT), 50), font=font)
        glow_img = glow_img.filter(ImageFilter.GaussianBlur(radius=int(8 * s)))
        img = Image.alpha_composite(img, glow_img)
        draw = ImageDraw.Draw(img)

    # The K itself
    draw.text((tx, ty), "K", fill=TEXT_WHITE, font=font)

    return img


def generate_status_icon(size, dot_color=None):
    """Generate icon with optional status dot (for runtime tray use)."""
    img = generate_icon_image(size)

    if dot_color:
        draw = ImageDraw.Draw(img)
        s = size / 256
        dot_radius = int(28 * s)
        cx = size - int(38 * s)
        cy = size - int(38 * s)

        # Dark outline for contrast
        draw.ellipse(
            [cx - dot_radius - int(4 * s), cy - dot_radius - int(4 * s),
             cx + dot_radius + int(4 * s), cy + dot_radius + int(4 * s)],
            fill=BG_DARK,
        )
        # The dot
        draw.ellipse(
            [cx - dot_radius, cy - dot_radius,
             cx + dot_radius, cy + dot_radius],
            fill=dot_color,
        )

    return img


def _hex_to_rgb(hex_color):
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def generate_ico():
    """Generate multi-resolution .ico file for Windows."""
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = []

    for sz in sizes:
        img = generate_icon_image(sz)
        # Convert RGBA to RGB with proper alpha compositing on dark background
        # ICO supports RGBA, so keep it
        images.append(img)

    # Save as .ico — PIL needs all images passed via append_images,
    # and the first image determines the "main" entry.
    # Use the largest image as the base for best quality.
    largest = images[-1]  # 256x256
    others = images[:-1]  # 16 through 128
    largest.save(
        OUTPUT_PATH,
        format="ICO",
        append_images=others,
    )

    print(f"Generated {OUTPUT_PATH}")
    print(f"  Resolutions: {', '.join(f'{sz}x{sz}' for sz in sizes)}")
    print(f"  Size: {os.path.getsize(OUTPUT_PATH) / 1024:.1f} KB")
    return OUTPUT_PATH


if __name__ == "__main__":
    generate_ico()
