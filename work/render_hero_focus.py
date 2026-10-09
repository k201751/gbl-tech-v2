import argparse
import math
import subprocess
from functools import lru_cache
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SOURCES = [
    ASSETS / "work-chef-silvia.png",
    ASSETS / "work-jennifer-wells.png",
    ASSETS / "work-louise-de-silva.png",
]

FPS = 18
DURATION = 10
INK = (33, 27, 45)
IVORY = (247, 243, 255)
LAVENDER = (201, 184, 255)
CORAL = (242, 95, 69)
WHITE = (255, 253, 250)


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def smooth(value):
    value = clamp(value)
    return value * value * (3 - 2 * value)


def ease_out(value):
    value = clamp(value)
    return 1 - (1 - value) ** 3


def mix(a, b, amount):
    return a + (b - a) * amount


def cover(image, size):
    tw, th = size
    ratio = max(tw / image.width, th / image.height)
    resized = image.resize((round(image.width * ratio), round(image.height * ratio)), Image.Resampling.LANCZOS)
    left = (resized.width - tw) // 2
    top = (resized.height - th) // 2
    return resized.crop((left, top, left + tw, top + th))


def contain(image, size, background=WHITE):
    tw, th = size
    ratio = min(tw / image.width, th / image.height)
    resized = image.resize((round(image.width * ratio), round(image.height * ratio)), Image.Resampling.LANCZOS)
    result = Image.new("RGB", size, background)
    result.paste(resized, ((tw - resized.width) // 2, (th - resized.height) // 2))
    return result


def rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return mask


@lru_cache(maxsize=4)
def background(width, height, portrait):
    y, x = np.ogrid[:height, :width]
    cx = width * (0.80 if not portrait else 0.58)
    cy = height * (0.44 if not portrait else 0.72)
    dist = np.sqrt(((x - cx) / width) ** 2 + ((y - cy) / height) ** 2)
    glow = np.clip(1 - dist / 0.72, 0, 1) ** 2
    base = np.empty((height, width, 3), dtype=np.float32)
    base[:] = IVORY
    lavender = np.array(LAVENDER, dtype=np.float32)
    base = base * (1 - glow[..., None] * 0.25) + lavender * glow[..., None] * 0.25
    return Image.fromarray(np.uint8(np.clip(base, 0, 255)), "RGB")


def add_grid(canvas, portrait):
    draw = ImageDraw.Draw(canvas, "RGBA")
    gap = 58 if not portrait else 52
    left_safe = int(canvas.width * (0.47 if not portrait else 0.04))
    for x in range(left_safe, canvas.width + gap, gap):
        draw.line((x, 0, x, canvas.height), fill=(*INK, 13), width=1)
    top = int(canvas.height * (0.08 if not portrait else 0.42))
    for y in range(top, canvas.height + gap, gap):
        draw.line((left_safe, y, canvas.width, y), fill=(*INK, 13), width=1)


def make_card(image, size, blur=0.0, desaturate=0.0):
    w, h = size
    inner = contain(image, (w - 26, h - 58), WHITE)
    if desaturate:
        gray = ImageEnhance.Color(inner).enhance(0.0)
        inner = Image.blend(inner, gray, desaturate)
    if blur > 0.1:
        inner = inner.filter(ImageFilter.GaussianBlur(blur))
    card = Image.new("RGBA", size, (*WHITE, 255))
    card.paste(inner, (13, 13))
    draw = ImageDraw.Draw(card, "RGBA")
    draw.line((18, h - 31, w - 18, h - 31), fill=(*INK, 35), width=1)
    draw.ellipse((18, h - 20, 24, h - 14), fill=(*CORAL, 220))
    draw.rounded_rectangle((w - 78, h - 22, w - 18, h - 12), radius=5, fill=(*INK, 35))
    mask = rounded_mask(size, 7)
    card.putalpha(mask)
    return card


def paste_card(canvas, card, xy, angle=0.0, opacity=255):
    card = card.copy()
    if opacity < 255:
        alpha = card.getchannel("A").point(lambda value: value * opacity // 255)
        card.putalpha(alpha)
    x, y = map(int, xy)
    shadow = Image.new("RGBA", card.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=9, fill=(*INK, 20 * opacity // 255))
    canvas.alpha_composite(shadow, (x + 13, y + 16))
    canvas.alpha_composite(card, (x, y))


def bezier(p0, p1, p2, amount):
    inv = 1 - amount
    return (
        inv * inv * p0[0] + 2 * inv * amount * p1[0] + amount * amount * p2[0],
        inv * inv * p0[1] + 2 * inv * amount * p1[1] + amount * amount * p2[1],
    )


def add_focus_path(canvas, t, portrait):
    draw = ImageDraw.Draw(canvas, "RGBA")
    if portrait:
        p0 = (55, canvas.height * 0.52)
        p1 = (canvas.width * 0.87, canvas.height * 0.57)
        p2 = (canvas.width * 0.64, canvas.height * 0.84)
    else:
        p0 = (canvas.width * 0.48, canvas.height * 0.22)
        p1 = (canvas.width * 0.92, canvas.height * 0.08)
        p2 = (canvas.width * 0.78, canvas.height * 0.70)
    amount = smooth((t - 0.7) / 8.5)
    points = [bezier(p0, p1, p2, i / 60) for i in range(round(amount * 60) + 1)]
    if len(points) > 1:
        draw.line(points, fill=(*CORAL, 85), width=2)
    x, y = bezier(p0, p1, p2, amount)
    pulse = 1 + .08 * math.sin(t * 4)
    radius = int((18 if not portrait else 15) * pulse)
    draw.ellipse((x - radius * 2.3, y - radius * 2.3, x + radius * 2.3, y + radius * 2.3), outline=(*CORAL, 75), width=2)
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*CORAL, 245))
    draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=WHITE)


def render_frame(t, width, height, portrait, cards, frame_index):
    base = background(width, height, portrait).copy()
    add_grid(base, portrait)
    canvas = base.convert("RGBA")

    if portrait:
        card_size = (520, 360)
        finals = [(105, 650, -5), (145, 745, 4), (92, 840, -1)]
        starts = [(680, 560), (-590, 750), (680, 930)]
    else:
        card_size = (500, 342)
        finals = [(740, 145, -6), (785, 230, 5), (705, 320, -1)]
        starts = [(1320, 20), (1320, 230), (1320, 590)]

    for index, variants in enumerate(cards):
        enter_start = .85 + index * .55
        enter = ease_out((t - enter_start) / 1.25)
        align = smooth((t - 4.1 - index * .18) / 1.4)
        reveal = smooth((t - 6.3 - index * .3) / 1.0)
        final_x, final_y, final_angle = finals[index]
        scattered_y = final_y + (-85 + index * 75)
        x = mix(starts[index][0], final_x + (index - 1) * 28, enter)
        y = mix(starts[index][1], scattered_y, enter)
        y = mix(y, final_y, align)
        angle = mix((11, -9, 8)[index], final_angle, align)
        card = variants[1] if reveal < .55 else variants[0]
        opacity = int(255 * clamp((t - enter_start) / .45))
        paste_card(canvas, card, (x, y), angle, opacity)

    # A lavender plane briefly passes over the cards, then reveals them in order.
    wipe = smooth((t - 3.1) / .8) * (1 - smooth((t - 4.8) / .9))
    if wipe > 0:
        draw = ImageDraw.Draw(canvas, "RGBA")
        if portrait:
            top = int(mix(height * .95, height * .46, wipe))
            draw.rectangle((0, top, width, height), fill=(*LAVENDER, int(105 * wipe)))
        else:
            left = int(mix(width, width * .48, wipe))
            draw.rectangle((left, 0, width, height), fill=(*LAVENDER, int(90 * wipe)))

    add_focus_path(canvas, t, portrait)

    # Resolve into a simple final frame that remains useful when playback ends.
    resolve = smooth((t - 9.0) / 1.7)
    if resolve > 0:
        draw = ImageDraw.Draw(canvas, "RGBA")
        cx = width * (.81 if not portrait else .70)
        cy = height * (.70 if not portrait else .81)
        for offset, alpha in ((0, 150), (28, 75), (58, 38)):
            r = (54 + offset) * (1 + .05 * math.sin(t * 2))
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(*CORAL, int(alpha * resolve)), width=3 if offset == 0 else 2)
        draw.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=(*CORAL, int(255 * resolve)))

    return canvas.convert("RGB")


def render(orientation, preview=False):
    portrait = orientation == "portrait"
    width, height = ((720, 1280) if portrait else (1280, 720))
    images = [Image.open(path).convert("RGB") for path in SOURCES]
    card_size = (520, 360) if portrait else (500, 342)
    cards = [(make_card(image, card_size, 0, 0), make_card(image, card_size, 5.5, .82)) for image in images]
    suffix = "-mobile" if portrait else ""
    out = ASSETS / f"hero-focus{suffix}.mp4"
    poster = ASSETS / f"hero-focus-poster{suffix}.jpg"

    if preview:
        times = [1.2, 2.8, 4.5, 6.5, 8.2, 10.8]
        thumbs = []
        for index, time in enumerate(times):
            frame = render_frame(time, width, height, portrait, cards, round(time * FPS))
            thumb_width = 320 if not portrait else 180
            thumb_height = round(thumb_width * height / width)
            thumbs.append(frame.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS))
        sheet = Image.new("RGB", (thumbs[0].width * 3, thumbs[0].height * 2), IVORY)
        for index, thumb in enumerate(thumbs):
            sheet.paste(thumb, ((index % 3) * thumb.width, (index // 3) * thumb.height))
        path = ROOT / "work" / f"hero-focus-preview{suffix}.jpg"
        sheet.save(path, quality=92)
        print(path)
        return

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg, "-y", "-f", "rawvideo", "-vcodec", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{width}x{height}", "-r", str(FPS), "-i", "-", "-an",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "25", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", str(out)
    ]
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    total = DURATION * FPS
    for index in range(total):
        frame = render_frame(index / FPS, width, height, portrait, cards, index)
        process.stdin.write(np.asarray(frame, dtype=np.uint8).tobytes())
        if index % FPS == 0:
            print(f"{orientation}: {index // FPS:02d}/{DURATION}s", flush=True)
    process.stdin.close()
    if process.wait() != 0:
        raise SystemExit("ffmpeg failed")
    render_frame(DURATION - 1 / FPS, width, height, portrait, cards, total - 1).save(poster, quality=92)
    print(out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("orientation", choices=("landscape", "portrait"))
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()
    render(args.orientation, args.preview)
