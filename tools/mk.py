#!/usr/bin/env python3
"""Millioner_lifestyle Shorts renderer.

Usage:
    python3 tools/mk.py tools/specs/spec_x.json [-o OUT_DIR]

Writes OUT_DIR/vidNEW7_<name>.mp4 (default OUT_DIR: ./out) and check stills to
OUT_DIR/stills_<name>/. Exit code 2 = a layout check failed (text did not fit) or
duration is outside 19-23 s; look at the stills and shorten text before uploading.

Spec format (see tools/specs/TEMPLATE.json):
{"name": "x", "scenes": [ {type, say, ...}, ... ]}
 hook:  {"type":"hook","title":"...","sub":"...","say":"..."}
 stat:  {"type":"stat","big":"$172,000","label":"...","count":172000,"prefix":"$","suffix":"","say":"..."}
        (count is optional; when set the number counts up from 0)
 bars:  {"type":"bars","title":"...","bars":[["label",value,"shown"],...],"hl":0,"say":"..."}
        (hl = index of the yellow highlighted bar; default = last bar)
 cta:   {"type":"cta","title":"...","sub":"...","say":"..."}

Assets (installed by tools/setup.sh):
  tools/models/kokoro-v1.0.onnx, tools/models/voices-v1.0.bin
  tools/fonts/Poppins-Bold.ttf, tools/fonts/Poppins-Medium.ttf
Override with env MK_MODELS_DIR / MK_FONTS_DIR.
"""
import argparse
import json
import math
import os
import random
import subprocess
import sys
import tempfile
import zlib

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
PAD = 0.7                      # silence after each scene's voice (s)
VOICE, LANG, SPEED = "am_michael", "en-us", 1.0
MIN_DUR, MAX_DUR = 19.0, 23.0  # target length of a Short (s)
HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.environ.get("MK_MODELS_DIR", os.path.join(HERE, "models"))
FONTS = os.environ.get("MK_FONTS_DIR", os.path.join(HERE, "fonts"))
FB = os.path.join(FONTS, "Poppins-Bold.ttf")
FM = os.path.join(FONTS, "Poppins-Medium.ttf")
YEL = (255, 210, 40)
BLUE = (90, 160, 255)
_fc = {}
WARN = []


def font(path, size):
    k = (path, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]


_kok = None


def tts(text):
    global _kok
    if _kok is None:
        from kokoro_onnx import Kokoro
        _kok = Kokoro(os.path.join(MODELS, "kokoro-v1.0.onnx"), os.path.join(MODELS, "voices-v1.0.bin"))
    s, sr = _kok.create(text, voice=VOICE, speed=SPEED, lang=LANG)
    return np.asarray(s, dtype=np.float32), sr


def wrap(draw, text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit(draw, text, path, size, maxw, maxlines, minsize=40, what=""):
    """Shrink font until text fits in maxlines and every line fits maxw."""
    while size > minsize:
        f = font(path, size)
        lines = wrap(draw, text, f, maxw)
        if len(lines) <= maxlines and all(draw.textlength(l, font=f) <= maxw for l in lines):
            return f, lines
        size -= 4
    f = font(path, minsize)
    lines = wrap(draw, text, f, maxw)
    if len(lines) > maxlines or any(draw.textlength(l, font=f) > maxw for l in lines):
        msg = f"TEXT DOES NOT FIT ({what}): {text!r}"
        if msg not in WARN:
            WARN.append(msg)
    return f, lines


def center_lines(draw, lines, fnt, y, fill, spacing=1.15, shadow=True):
    lh = int(fnt.size * spacing)
    for i, l in enumerate(lines):
        w = draw.textlength(l, font=fnt)
        x = (W - w) / 2
        if shadow:
            draw.text((x + 4, y + i * lh + 5), l, font=fnt, fill=(0, 0, 0, 160))
        draw.text((x, y + i * lh), l, font=fnt, fill=fill)
    return y + len(lines) * lh


def make_bg(seed):
    """Big blurred colour blobs; the frame is a slowly drifting crop of it."""
    rnd = random.Random(seed)
    big = Image.new("RGB", (W + 400, H + 400), (12, 14, 26))
    d = ImageDraw.Draw(big)
    pal = [(40, 90, 200), (120, 40, 170), (20, 140, 120), (200, 120, 30), (180, 40, 80)]
    for _ in range(9):
        c = rnd.choice(pal)
        r = rnd.randint(250, 520)
        x, y = rnd.randint(0, W + 400), rnd.randint(0, H + 400)
        d.ellipse([x - r, y - r, x + r, y + r], fill=c)
    big = big.filter(ImageFilter.GaussianBlur(160))
    return Image.blend(big, Image.new("RGB", big.size, (0, 0, 0)), 0.45)


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def word_times(text, start, dur):
    """Kokoro gives no word timestamps: spread the scene audio over words by length."""
    words = text.split()
    wts = [len(w.strip(".,!?;:")) + 2 for w in words]
    tot = sum(wts)
    out, t = [], start
    for w, wt in zip(words, wts):
        d = dur * wt / tot
        out.append((w, t, t + d))
        t += d
    return out


def draw_scene(d, sc, lt):
    """lt = local time inside scene (s)."""
    a = ease(lt / 0.35)
    typ = sc["type"]
    if typ in ("hook", "cta"):
        f, lines = fit(d, sc["title"], FB, 118 if typ == "hook" else 100, W - 140, 4, what=f"{typ} title")
        y = center_lines(d, lines, f, 520 - (1 - a) * 60, YEL if typ == "hook" else (255, 255, 255))
        if sc.get("sub"):
            f2, l2 = fit(d, sc["sub"], FM, 60, W - 180, 3, what=f"{typ} sub")
            center_lines(d, l2, f2, y + 40, (230, 230, 240))
    elif typ == "stat":
        if sc.get("count") is not None:
            v = sc["count"] * ease(lt / 1.2)
            big = f"{sc.get('prefix', '')}{v:,.0f}{sc.get('suffix', '')}"
        else:
            big = sc["big"]
        f, _ = fit(d, sc["big"], FB, 200, W - 120, 1, what="stat big")
        w = d.textlength(big, font=f)
        y = 520 - (1 - a) * 60
        d.text(((W - w) / 2 + 5, y + 6), big, font=f, fill=(0, 0, 0, 160))
        d.text(((W - w) / 2, y), big, font=f, fill=YEL)
        f2, l2 = fit(d, sc["label"], FM, 66, W - 160, 3, what="stat label")
        center_lines(d, l2, f2, y + f.size + 60, (240, 240, 245))
    elif typ == "bars":
        f, lines = fit(d, sc["title"], FB, 80, W - 140, 2, what="bars title")
        y = center_lines(d, lines, f, 300, (255, 255, 255)) + 50
        bars = sc["bars"]
        n = len(bars)
        mx = max(b[1] for b in bars)
        area_h = 640
        bw = min(220, (W - 160) // n - 50)
        gap = (W - 160 - n * bw) / max(1, n - 1) if n > 1 else 0
        base = y + area_h + 40
        for i, (lab, val, shown) in enumerate(bars):
            g = ease((lt - 0.25 * i) / 0.9)
            h = area_h * val / mx * g
            x = 80 + i * (bw + gap) if n > 1 else (W - bw) / 2
            col = YEL if i == sc.get("hl", n - 1) else BLUE
            d.rounded_rectangle([x, base - h, x + bw, base], radius=18, fill=col)
            fv, _ = fit(d, shown, FB, 56, bw + gap * 0.8, 1, 30, what="bar value")
            tw = d.textlength(shown, font=fv)
            if g > 0.05:
                d.text((x + bw / 2 - tw / 2, base - h - fv.size - 16), shown, font=fv, fill=(255, 255, 255))
            fl2, ll = fit(d, lab, FM, 44, bw + gap * 0.8, 2, 28, what="bar label")
            for j, l in enumerate(ll):
                lw = d.textlength(l, font=fl2)
                lx = min(max(x + bw / 2 - lw / 2, 50), W - 50 - lw)
                d.text((lx, base + 16 + j * int(fl2.size * 1.15)), l, font=fl2, fill=(220, 220, 230))
    else:
        raise ValueError(f"unknown scene type {typ!r}")


def draw_caption(d, words, t):
    """Word-by-word caption: current word yellow, past white, upcoming grey.
    Shows groups of up to 4 words; a group never spans two scenes."""
    idx = None
    for i, (w, s, e, _) in enumerate(words):
        if s <= t < e:
            idx = i
            break
    if idx is None:
        return
    chunk = 4
    first = idx
    while first > 0 and words[first - 1][3] == words[idx][3]:
        first -= 1
    c0 = first + ((idx - first) // chunk) * chunk
    group = [w for w in words[c0:c0 + chunk] if w[3] == words[idx][3]]
    f = font(FB, 78)
    txt = " ".join(g[0] for g in group)
    while d.textlength(txt, font=f) > W - 120 and f.size > 44:
        f = font(FB, f.size - 4)
    x = (W - d.textlength(txt, font=f)) / 2
    y = 1450
    for j, (w, s, e, _) in enumerate(group):
        gi = c0 + j
        col = YEL if gi == idx else ((255, 255, 255) if gi < idx else (150, 150, 160))
        for ox, oy in ((-3, 0), (3, 0), (0, -3), (0, 3), (4, 5)):
            d.text((x + ox, y + oy), w, font=f, fill=(0, 0, 0))
        d.text((x, y), w, font=f, fill=col)
        x += d.textlength(w + " ", font=f)


def contact_sheet(paths, out):
    ims = [Image.open(p).resize((216, 384)) for p in paths]
    sh = Image.new("RGB", (216 * len(ims), 384))
    for i, im in enumerate(ims):
        sh.paste(im, (216 * i, 0))
    sh.save(out)


def render(specpath, outdir):
    for p in (FB, FM, os.path.join(MODELS, "kokoro-v1.0.onnx"), os.path.join(MODELS, "voices-v1.0.bin")):
        if not os.path.exists(p):
            sys.exit(f"missing asset {p} - run tools/setup.sh first")
    spec = json.load(open(specpath, encoding="utf-8"))
    name = spec["name"]
    scenes = spec["scenes"]
    os.makedirs(outdir, exist_ok=True)
    stdir = os.path.join(outdir, f"stills_{name}")
    os.makedirs(stdir, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix=f"mk_{name}_")

    # 1) voice: one TTS clip per scene; scene length = voice + PAD
    t, sr, parts = 0.0, 24000, []
    for i, sc in enumerate(scenes):
        s, sr = tts(sc["say"])
        ad = len(s) / sr
        sc["_start"], sc["_dur"] = t, ad + PAD
        sc["_words"] = [(w, a, b, i) for w, a, b in word_times(sc["say"], t + 0.05, ad - 0.1)]
        parts.append((t, s))
        t += ad + PAD
    total = t
    audio = np.zeros(int(total * sr) + sr, dtype=np.float32)
    for st, s in parts:
        i0 = int(st * sr)
        audio[i0:i0 + len(s)] += s
    audio = audio[:int(total * sr)]
    wav = os.path.join(tmp, "audio.wav")
    sf.write(wav, audio, sr)
    print(f"{name}: {total:.2f}s")
    if not (MIN_DUR <= total <= MAX_DUR):
        WARN.append(f"DURATION {total:.1f}s outside {MIN_DUR}-{MAX_DUR}s - shorten/lengthen 'say' texts")

    # 2) frames: drawn with PIL, piped as raw RGB into ffmpeg
    bg = make_bg(zlib.crc32(name.encode()) & 0xffff)
    allwords = [w for sc in scenes for w in sc["_words"]]
    out = os.path.join(outdir, f"vidNEW7_{name}.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out],
                          stdin=subprocess.PIPE)
    nf = int(total * FPS)
    # one check still per scene, at 80% of the scene (animations finished)
    stills = {int((sc["_start"] + sc["_dur"] * 0.8) * FPS): f"{i}_{sc['type']}" for i, sc in enumerate(scenes)}
    saved = []
    for fi in range(nf):
        tt = fi / FPS
        ox = 200 + 180 * math.sin(tt * 0.25)
        oy = 200 + 180 * math.cos(tt * 0.18)
        frame = bg.crop((int(ox), int(oy), int(ox) + W, int(oy) + H)).convert("RGBA")
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        sc = next(s for s in reversed(scenes) if s["_start"] <= tt)
        draw_scene(d, sc, tt - sc["_start"])
        draw_caption(d, allwords, tt)
        d.rectangle([0, 0, W * tt / total, 14], fill=YEL)  # progress bar
        frame = Image.alpha_composite(frame, layer).convert("RGB")
        if fi in stills:
            p = os.path.join(stdir, f"still_{stills[fi]}.png")
            frame.save(p)
            saved.append(p)
        ff.stdin.write(frame.tobytes())
    ff.stdin.close()
    if ff.wait() != 0:
        sys.exit("ffmpeg failed")
    sheet = os.path.join(outdir, f"sheet_{name}.png")
    contact_sheet(saved, sheet)
    print("wrote", out)
    print("check sheet", sheet)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("-o", "--outdir", default="out")
    a = ap.parse_args()
    render(a.spec, a.outdir)
    if WARN:
        print("\nCHECKS FAILED:")
        for w in WARN:
            print("  -", w)
        sys.exit(2)
    print("checks OK")


if __name__ == "__main__":
    main()
