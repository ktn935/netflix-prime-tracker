# -*- coding: utf-8 -*-
"""
複数作品のサムネイル画像とタイトルを1枚にまとめた「コラージュ画像」を生成する。
Xの画像添付は1ツイートにつき最大4枚までだが、この画像1枚の中に
全作品のサムネイルを敷き詰めることで、件数の多い日でも全作品を
視覚的に見せられるようにする。
"""
import io
import os

import requests
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = os.path.join(os.path.dirname(__file__), "assets", "fonts", "NotoSansJP-Regular.ttf")

CELL_W = 200
THUMB_H = 160
TITLE_H = 50
COLS = 4
MAX_ITEMS = 12

COLORS = {
    "netflix": {"bg": (20, 20, 20), "text": (255, 255, 255)},
    "prime": {"bg": (5, 30, 60), "text": (255, 255, 255)},
}


def _download_image(url):
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    return Image.open(io.BytesIO(resp.content)).convert("RGB")


def _fit_thumbnail(img, w, h):
    """指定サイズにアスペクト比を保ったまま中央クロップでリサイズする"""
    src_w, src_h = img.size
    scale = max(w / src_w, h / src_h)
    new_w, new_h = max(1, int(src_w * scale)), max(1, int(src_h * scale))
    img = img.resize((new_w, new_h))
    left = (new_w - w) // 2
    top = (new_h - h) // 2
    return img.crop((left, top, left + w, top + h))


def _truncate_text(draw, text, font, max_width):
    if draw.textlength(text, font=font) <= max_width:
        return text
    while text and draw.textlength(text + "…", font=font) > max_width:
        text = text[:-1]
    return text + "…"


def make_collage(items, service):
    """
    items: [{"title": str, "thumbnail": str, ...}, ...]
    service: "netflix" または "prime"(背景色の切り替えに使用)
    戻り値: PNG画像のbytes。有効なサムネイルが1枚もなければNone。
    """
    valid_items = [it for it in items if it.get("thumbnail")][:MAX_ITEMS]
    if not valid_items:
        return None

    colors = COLORS[service]
    cols = min(COLS, len(valid_items))
    rows = (len(valid_items) + cols - 1) // cols

    canvas_w = cols * CELL_W
    canvas_h = rows * (THUMB_H + TITLE_H)
    canvas = Image.new("RGB", (canvas_w, canvas_h), colors["bg"])
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(FONT_PATH, 18)

    for i, it in enumerate(valid_items):
        col = i % cols
        row = i // cols
        x = col * CELL_W
        y = row * (THUMB_H + TITLE_H)

        try:
            thumb = _fit_thumbnail(_download_image(it["thumbnail"]), CELL_W, THUMB_H)
            canvas.paste(thumb, (x, y))
        except Exception:
            pass  # 画像が取得できなければ背景色の枠だけ残す

        title = _truncate_text(draw, it["title"], font, CELL_W - 16)
        draw.text((x + 8, y + THUMB_H + 12), title, font=font, fill=colors["text"])

    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
    return buf.getvalue()
