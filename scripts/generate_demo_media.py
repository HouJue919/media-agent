from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT_DIR = Path(__file__).resolve().parents[1]
DEMO_DIR = ROOT_DIR / "demo_media"
SIZE = (1024, 768)


def main() -> None:
    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    _save("normal_sharp_demo.jpg", _normal_sharp())
    _save("blurry_demo.jpg", _normal_sharp().filter(ImageFilter.GaussianBlur(radius=8)))
    _save("overexposed_demo.jpg", _overexposed())
    _save("underexposed_demo.jpg", _underexposed())
    duplicate = _duplicate_scene()
    _save("duplicate_pair_a_demo.jpg", duplicate)
    _save("duplicate_pair_b_demo.jpg", duplicate.copy())
    _save("fuji_mountain_demo.jpg", _fuji_mountain())
    _save("sunset_sky_demo.jpg", _sunset_sky())
    _save("tokyo_street_demo.jpg", _tokyo_street())
    _save("plane_airport_demo.jpg", _plane_airport())
    _save("unknown_demo.jpg", _unknown())
    print(f"Demo media written to: {DEMO_DIR}")


def _save(filename: str, image: Image.Image) -> None:
    output_path = DEMO_DIR / filename
    image.convert("RGB").save(output_path, "JPEG", quality=92, optimize=True)


def _canvas(top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    image = Image.new("RGB", SIZE, top)
    draw = ImageDraw.Draw(image)
    for y in range(SIZE[1]):
        ratio = y / max(SIZE[1] - 1, 1)
        color = tuple(int(top[i] * (1 - ratio) + bottom[i] * ratio) for i in range(3))
        draw.line([(0, y), (SIZE[0], y)], fill=color)
    return image


def _label(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int]) -> None:
    font = ImageFont.load_default()
    x, y = xy
    draw.rectangle((x - 12, y - 8, x + 330, y + 34), fill=(255, 255, 255))
    draw.text((x, y), text, fill=(32, 40, 50), font=font)


def _normal_sharp() -> Image.Image:
    image = _canvas((95, 160, 210), (40, 95, 75))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 510, 1024, 768), fill=(55, 120, 78))
    for x in range(-120, 1024, 70):
        draw.line((x, 768, x + 420, 500), fill=(235, 240, 230), width=3)
    for x in range(80, 960, 160):
        draw.rectangle((x, 360, x + 80, 520), fill=(210, 180, 120), outline=(80, 70, 55), width=4)
        draw.rectangle((x + 18, 390, x + 42, 430), fill=(50, 80, 115))
    _label(draw, "normal sharp demo", (36, 36))
    return image


def _overexposed() -> Image.Image:
    image = Image.new("RGB", SIZE, (248, 248, 242))
    draw = ImageDraw.Draw(image)
    draw.ellipse((700, 40, 940, 280), fill=(255, 255, 255))
    draw.rectangle((0, 570, 1024, 768), fill=(236, 232, 218))
    for x in range(40, 1024, 90):
        draw.line((x, 768, x + 240, 520), fill=(255, 255, 255), width=5)
    _label(draw, "overexposed demo", (36, 36))
    return image


def _underexposed() -> Image.Image:
    image = _canvas((12, 20, 34), (8, 12, 18))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 570, 1024, 768), fill=(10, 18, 14))
    for x in range(80, 1024, 170):
        draw.rectangle((x, 420, x + 70, 560), fill=(25, 28, 34), outline=(45, 48, 54), width=2)
    draw.ellipse((760, 90, 840, 170), fill=(58, 62, 78))
    _label(draw, "underexposed demo", (36, 36))
    return image


def _duplicate_scene() -> Image.Image:
    image = _canvas((88, 150, 196), (55, 110, 95))
    draw = ImageDraw.Draw(image)
    draw.polygon([(0, 610), (240, 340), (470, 610)], fill=(62, 92, 74), outline=(235, 245, 240))
    draw.polygon([(320, 610), (620, 280), (940, 610)], fill=(54, 85, 72), outline=(235, 245, 240))
    draw.rectangle((0, 610, 1024, 768), fill=(42, 100, 70))
    draw.line((0, 680, 1024, 650), fill=(230, 235, 220), width=6)
    _label(draw, "duplicate pair demo", (36, 36))
    return image


def _fuji_mountain() -> Image.Image:
    image = _canvas((118, 178, 218), (230, 235, 225))
    draw = ImageDraw.Draw(image)
    draw.polygon([(120, 650), (512, 170), (904, 650)], fill=(70, 96, 118))
    draw.polygon([(390, 320), (512, 170), (635, 320), (570, 300), (512, 250), (455, 300)], fill=(248, 250, 246))
    draw.rectangle((0, 650, 1024, 768), fill=(72, 132, 82))
    _label(draw, "fuji mountain demo", (36, 36))
    return image


def _sunset_sky() -> Image.Image:
    image = _canvas((250, 110, 80), (72, 45, 116))
    draw = ImageDraw.Draw(image)
    draw.ellipse((410, 250, 610, 450), fill=(255, 205, 98))
    draw.rectangle((0, 440, 1024, 768), fill=(40, 45, 72))
    for y in range(500, 760, 45):
        draw.line((0, y, 1024, y + 12), fill=(238, 120, 88), width=4)
    _label(draw, "sunset sky demo", (36, 36))
    return image


def _tokyo_street() -> Image.Image:
    image = _canvas((75, 93, 128), (30, 34, 45))
    draw = ImageDraw.Draw(image)
    for index, x in enumerate(range(40, 980, 120)):
        height = 300 + (index % 4) * 55
        draw.rectangle((x, 520 - height, x + 86, 650), fill=(42, 52, 70), outline=(105, 120, 140))
        for wy in range(240, 620, 52):
            draw.rectangle((x + 16, wy, x + 32, wy + 18), fill=(248, 205, 95))
            draw.rectangle((x + 52, wy, x + 68, wy + 18), fill=(118, 168, 210))
    draw.polygon([(300, 768), (470, 540), (554, 540), (724, 768)], fill=(52, 54, 60))
    _label(draw, "tokyo street demo", (36, 36))
    return image


def _plane_airport() -> Image.Image:
    image = _canvas((130, 184, 220), (210, 220, 220))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 535, 1024, 768), fill=(112, 118, 125))
    draw.line((0, 650, 1024, 650), fill=(240, 240, 220), width=6)
    draw.ellipse((280, 315, 730, 395), fill=(245, 248, 250), outline=(64, 72, 84), width=4)
    draw.polygon([(470, 330), (300, 220), (540, 335)], fill=(230, 235, 240), outline=(64, 72, 84))
    draw.polygon([(530, 350), (760, 260), (605, 380)], fill=(230, 235, 240), outline=(64, 72, 84))
    draw.rectangle((680, 342, 820, 368), fill=(245, 248, 250), outline=(64, 72, 84))
    _label(draw, "plane airport demo", (36, 36))
    return image


def _unknown() -> Image.Image:
    image = Image.new("RGB", SIZE, (150, 150, 150))
    draw = ImageDraw.Draw(image)
    for y in range(0, SIZE[1], 32):
        for x in range(0, SIZE[0], 32):
            value = 110 + ((x * 7 + y * 3) % 90)
            draw.rectangle((x, y, x + 31, y + 31), fill=(value, value, value))
    _label(draw, "unknown demo", (36, 36))
    return image


if __name__ == "__main__":
    main()
