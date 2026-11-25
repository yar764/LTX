# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "torch",
#     "diffusers @ git+https://github.com/huggingface/diffusers",
#     "transformers",
#     "accelerate",
#     "safetensors",
#     "sentencepiece",
#     "huggingface_hub",
#     "imageio-ffmpeg",
#     "av",
#     "pillow",
#     "numpy",
# ]
# ///
#
#  استودیو داستان سینمایی با MiniMax H3 — برای molab (marimo)
#  1) GPU (RTX Pro 6000) را از دکمه‌ی مشخصات بالای صفحه روشن کنید   2) Run all
#
#  ساختار: مرحله‌ی ۱ مدل متن همه‌ی صحنه‌ها را می‌خواند و پاک می‌شود ← مرحله‌ی ۲ مدل ویدیو همه‌ی صحنه‌ها را
#  پشت سر هم می‌سازد ← مرحله‌ی ۳ چسباندن. هر قدم روی دیسک ذخیره می‌شود و بعد از قطعی از همان‌جا ادامه می‌دهد.

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="full", app_title="H3 Story Studio")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import os
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
    import gc, json, time, random, shutil, subprocess, hashlib, traceback, threading, zipfile, re
    from pathlib import Path
    from PIL import Image
    return (
        Image, Path, gc, hashlib, json, mo, os, random, re, shutil, subprocess, threading, time, traceback,
        zipfile,
    )


@app.cell(hide_code=True)
def _():
    REPO = "MiniMaxAI/MiniMax-H3"
    FPS = 24
    STYLES = {
        "🎬 فیلم سینمایی واقعی": (
            "Photorealistic live-action Hollywood film, shot on ARRI Alexa 65 with anamorphic lenses, real actors "
            "in real practical costumes, realistic skin texture, physically accurate lighting, natural film color "
            "grading, subtle film grain"),
        "🎥 لایو اکشن طبیعی": (
            "Natural live-action footage, real people, handheld modern cinema camera, natural light, true-to-life colors"),
        "🕯 تاریک / ترسناک": (
            "Dark live-action thriller, low-key lighting, deep shadows, desaturated cold tones, drifting fog"),
        "🐉 فانتزی حماسی": (
            "Epic live-action fantasy film, grand scale, volumetric god rays, rich colors, sweeping cinematography"),
        "🧸 انیمیشن سه‌بعدی": (
            "High-quality 3D animated feature film, stylized characters, soft global illumination"),
        "🌸 انیمه": ("Japanese anime, cel-shaded characters, detailed painted backgrounds, dynamic anime camera"),
    }
    # اندازه‌ها مضرب ۳۲ (شرط H3)
    CANVAS = {
        "کیفیت کامل H3 (۷۶۸p)": {"16:9 افقی": (768, 1344), "9:16 عمودی": (1344, 768)},
        "سریع‌تر (۵۴۴p — حدود ۲ برابر سریع‌تر)": {"16:9 افقی": (544, 960), "9:16 عمودی": (960, 544)},
    }
    SECONDS = {"۵ ثانیه": 5, "۸ ثانیه": 8, "۱۰ ثانیه": 10, "۱۲ ثانیه": 12, "۱۵ ثانیه": 15}
    DEFAULT_SFX = ("cinematic orchestral score, realistic sound effects matching every action, footsteps, impacts, "
                   "ambience")
    return CANVAS, DEFAULT_SFX, FPS, REPO, SECONDS, STYLES


@app.cell(hide_code=True)
def _(Path, json, os, threading):
    # ───────────── پروژه روی دیسک ─────────────
    OUT = Path("h3_story_output").resolve()
    for _d in ("characters", "embeds", "scenes", "final", "backups"):
        (OUT / _d).mkdir(parents=True, exist_ok=True)
    PROJECT_FILE = OUT / "project.json"
    LOCK = threading.RLock()

    def _empty():
        return {"chars": {}, "scenes": [], "final": None, "drafts": {}, "backup": None}

    def load_project():
        _p = _empty()
        try:
            _p.update(json.loads(PROJECT_FILE.read_text(encoding="utf-8")))
        except Exception:
            pass
        _p["chars"] = {k: v for k, v in _p["chars"].items() if (OUT / v["image"]).exists()}
        for _s in _p["scenes"]:
            if _s.get("embeds") and not (OUT / _s["embeds"]).exists():
                _s["embeds"] = None
            if _s.get("video") and not (OUT / _s["video"]).exists():
                _s["video"] = None
        for _k in ("final", "backup"):
            if _p.get(_k) and not (OUT / _p[_k]).exists():
                _p[_k] = None
        return _p

    PROJECT = load_project()

    def save_project():
        with LOCK:
            _tmp = PROJECT_FILE.with_suffix(".tmp")
            _tmp.write_text(json.dumps(PROJECT, ensure_ascii=False, indent=1), encoding="utf-8")
            _tmp.replace(PROJECT_FILE)

    def rel(p):
        return str(Path(p).resolve().relative_to(OUT))

    def absp(r):
        return OUT / r

    def read_env_token():
        for _f in (Path(".env"), Path.home() / ".env"):
            try:
                for _line in _f.read_text(encoding="utf-8").splitlines():
                    _k, _, _v = _line.partition("=")
                    if _k.strip() in ("HF_TOKEN", "HUGGING_FACE_HUB_TOKEN") and _v.strip():
                        return _v.strip().strip('"').strip("'")
            except Exception:
                pass
        return os.environ.get("HF_TOKEN", "")
    return LOCK, OUT, PROJECT, absp, read_env_token, rel, save_project


@app.cell(hide_code=True)
def _(mo):
    get_rev, set_rev = mo.state(0)

    def bump():
        set_rev(lambda v: v + 1)
    return bump, get_rev


@app.cell(hide_code=True)
def _(threading, time, traceback):
    # ───────────── کار در پس‌زمینه ─────────────
    JOB = {"running": False, "title": "", "detail": "", "step": 0, "total": 0,
           "start": 0.0, "version": 0, "error": None, "message": ""}

    def start_job(title, fn):
        if JOB["running"]:
            return False
        JOB.update(running=True, title=title, detail="آماده‌سازی…", step=0, total=0,
                   start=time.time(), error=None, message="")

        def _run():
            try:
                JOB["message"] = fn() or "✅ انجام شد."
            except Exception as _e:
                _t = str(_e).lower()
                if "out of memory" in _t:
                    JOB["error"] = "حافظه‌ی کارت گرافیک کافی نبود. «سریع‌تر (۵۴۴p)» یا صحنه‌های کوتاه‌تر را امتحان کنید."
                elif "no space left" in _t:
                    JOB["error"] = "فضای دیسک molab پر شد (مدل H3 حدود ۱۳۵ گیگ است)."
                elif any(x in _t for x in ("401", "403", "gated", "unauthorized")):
                    JOB["error"] = ("دسترسی به مدل ندارید: در صفحه‌ی MiniMaxAI/MiniMax-H3 در Hugging Face شرایط را قبول "
                                    "کنید و توکن را در تب «💾 پروژه و تنظیمات» بگذارید.")
                else:
                    JOB["error"] = f"{type(_e).__name__}: {_e}"
                JOB["trace"] = traceback.format_exc()[-3000:]
                JOB["message"] = ""
            finally:
                JOB["running"] = False
                JOB["version"] += 1

        threading.Thread(target=_run, daemon=True).start()
        return True
    return JOB, start_job


@app.cell(hide_code=True)
def _(FPS, Image, OUT, REPO, gc, os, re, shutil, subprocess, torch_mod):
    torch = torch_mod

    def use_token(token):
        """توکن برای همه‌ی دانلودها (حتی آن‌هایی که پارامتر توکن ندارند)"""
        if token:
            os.environ["HF_TOKEN"] = token
            try:
                from huggingface_hub import login
                login(token=token, add_to_git_credential=False)
            except Exception:
                pass

    def valid_frames(seconds):
        """H3 فقط تعداد فریم 17n+5 بین ۵ تا ۱۵ ثانیه را می‌پذیرد"""
        _f = int(seconds * FPS)
        _n = -(-(_f - 5) // 17)
        return max(124, min(345, 17 * _n + 5))

    def ffmpeg_exe():
        _f = shutil.which("ffmpeg")
        if _f:
            return _f
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()

    def load_rgb(path):
        """عکس شفاف (بدون پس‌زمینه) روی زمینه‌ی سفید"""
        _im = Image.open(path)
        if _im.mode in ("RGBA", "LA", "P"):
            _im = _im.convert("RGBA")
            _bg = Image.new("RGB", _im.size, (255, 255, 255))
            _bg.paste(_im, mask=_im.split()[-1])
            return _bg
        return _im.convert("RGB")

    def wipe(module):
        """وزن‌ها مستقیم از کارت گرافیک پاک می‌شوند (به رم ۳۲ گیگی منتقل نمی‌شوند)"""
        if module is None:
            return
        try:
            for _t in list(module.parameters()) + list(module.buffers()):
                _t.data = torch.empty(0, dtype=_t.dtype)
        except Exception:
            pass

    def clear():
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def split_pipelines():
        """خط تولید H3 دو تکه می‌شود: «خواننده‌ی متن» و «سازنده‌ی ویدیو» تا هیچ‌وقت هم‌زمان روی GPU نباشند"""
        from diffusers.modular_pipelines import SequentialPipelineBlocks
        from diffusers.modular_pipelines.minimax_h3 import MiniMaxH3Blocks
        _blocks = MiniMaxH3Blocks().get_workflow("ref2va")
        _subs = dict(_blocks.sub_blocks)
        _cond = SequentialPipelineBlocks.from_blocks_dict(
            {"before_encode": _subs.pop("before_encode"), "text_encoder": _subs.pop("text_encoder")})
        _rest = SequentialPipelineBlocks.from_blocks_dict(_subs)
        return _cond, _rest

    class H3Engine:
        def __init__(self):
            self.cond = None
            self.rest = None
            self.job = None

        def _say(self, d):
            if self.job is not None:
                self.job["detail"] = d

        def _check(self, pipe, names):
            """load_components خطا را فقط هشدار می‌دهد؛ اینجا اگر بخشی بار نشده باشد صریح متوقف می‌شویم"""
            _missing = [n for n in names if getattr(pipe, n, None) is None]
            if _missing:
                raise RuntimeError(
                    "این بخش‌های مدل بار نشدند: " + ", ".join(_missing) + ". معمولاً یعنی توکن Hugging Face نیست، "
                    "شرایط مدل MiniMaxAI/MiniMax-H3 قبول نشده، یا فضای دیسک/حافظه کم است.")

        def free(self):
            for _p in (self.cond, self.rest):
                if _p is None:
                    continue
                for _name in ("text_encoder", "transformer_ref", "vae", "audio_vae"):
                    wipe(getattr(_p, _name, None))
            self.cond = self.rest = None
            clear()

        def load_reader(self, token):
            """مرحله‌ی ۱: مدل متن (Qwen3-VL، ۶۲ گیگ) مستقیم روی GPU"""
            if self.cond is not None:
                return
            self.free()
            _cb, _ = split_pipelines()
            self._say("دانلود/بارگذاری مدل متن H3 (بار اول ممکن است طول بکشد)…")
            self.cond = _cb.init_pipeline(REPO)
            self.cond.load_components(dtype=torch.bfloat16, device_map={"text_encoder": "cuda"},
                                      token=token or None)
            self._check(self.cond, ("text_encoder", "tokenizer", "processor"))

        def load_maker(self, token):
            """مرحله‌ی ۲: مدل ویدیو (۶۲ گیگ) + VAEها مستقیم روی GPU"""
            if self.rest is not None:
                return
            self.free()
            _, _rb = split_pipelines()
            self._say("دانلود/بارگذاری مدل ویدیوی H3 (بار اول ممکن است طول بکشد)…")
            self.rest = _rb.init_pipeline(REPO)
            self.rest.load_components(
                dtype=torch.bfloat16,
                device_map={"transformer_ref": "cuda", "vae": "cuda", "audio_vae": "cuda"},
                token=token or None)
            self._check(self.rest, ("transformer_ref", "vae", "audio_vae"))

        def read(self, prompt, ref_paths, seconds, hw):
            from diffusers.modular_pipelines.minimax_h3 import MiniMaxH3ImageReference
            _refs = [MiniMaxH3ImageReference(image=load_rgb(p)) for p in ref_paths]
            _h, _w = hw
            with torch.no_grad():
                _state = self.cond(prompt=prompt, references=_refs, num_frames=valid_frames(seconds),
                                   height=_h, width=_w)
            _vals = {}
            for _k, _v in _state.values.items():
                _vals[_k] = _v.detach().to("cpu") if isinstance(_v, torch.Tensor) else _v
            return _vals

        def make(self, values, seconds, hw, seed):
            from diffusers.modular_pipelines import PipelineState
            _st = PipelineState()
            for _k, _v in values.items():
                _st.set(_k, _v)
            _h, _w = hw
            with torch.no_grad():
                return self.rest(state=_st, num_frames=valid_frames(seconds), height=_h, width=_w,
                                 generator=torch.Generator().manual_seed(int(seed)),
                                 output=["videos", "audio", "sampling_rate"])

    def save_scene(results, out_path):
        from diffusers.utils.export_utils import encode_video
        encode_video(results["videos"][0], fps=FPS, output_path=str(out_path),
                     audio=results["audio"][0], audio_sample_rate=results["sampling_rate"])
        return out_path

    def concat(paths, out_path):
        _ff = ffmpeg_exe()
        _probe = subprocess.run([_ff, "-i", str(paths[0])], capture_output=True).stderr.decode(errors="ignore")
        _m = re.search(r"Video:.*?(\d{3,4})x(\d{3,4})", _probe)
        _W, _H = (int(_m.group(1)), int(_m.group(2))) if _m else (1344, 768)
        _cmd = [_ff, "-y", "-loglevel", "error"]
        for _p in paths:
            _cmd += ["-i", str(_p)]
        _f = []
        for _i in range(len(paths)):
            _f.append(f"[{_i}:v]scale={_W}:{_H}:force_original_aspect_ratio=increase,crop={_W}:{_H},setsar=1,"
                      f"fps={FPS}[v{_i}]")
            _f.append(f"[{_i}:a]aresample=48000,aformat=channel_layouts=stereo[a{_i}]")
        _f.append("".join(f"[v{_i}][a{_i}]" for _i in range(len(paths))) + f"concat=n={len(paths)}:v=1:a=1[v][a]")
        _cmd += ["-filter_complex", ";".join(_f), "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "17",
                 "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                 "-movflags", "+faststart", str(out_path)]
        _r = subprocess.run(_cmd, capture_output=True)
        if _r.returncode != 0:
            raise RuntimeError(_r.stderr.decode(errors="ignore")[-1500:])
        return out_path

    def disk_free_gb():
        try:
            return shutil.disk_usage(OUT).free / 1e9
        except Exception:
            return -1

    engine = H3Engine()
    return clear, concat, disk_free_gb, engine, save_scene, use_token


@app.cell(hide_code=True)
def _():
    import torch as torch_mod
    return (torch_mod,)


@app.cell(hide_code=True)
def _(mo, re):
    _F = "font-family:Vazirmatn,Tahoma,sans-serif;"
    STY = {
        "yar-root": "direction:rtl;" + _F,
        "yar-card": "border:1px solid #e4e0f5;border-radius:14px;padding:14px 16px;background:#fcfbff;" + _F,
        "yar-sec": "font-weight:700;color:#3b2a8c;font-size:16px;margin:2px 0 6px;",
        "yar-muted": "color:#77738c;font-size:13px;line-height:1.8;",
        "yar-badge": "display:inline-block;background:#ede8ff;color:#3b2a8c;border-radius:8px;padding:1px 9px;font-size:12px;margin:0 4px;",
        "yar-ltr": "direction:ltr;text-align:left;",
        "yar-head": "background:linear-gradient(120deg,#1d1440,#4a2fb5 60%,#7b5cf0);color:#fff;border-radius:16px;padding:18px 24px;margin-bottom:6px;",
        "yar-pill": "display:inline-block;background:rgba(255,255,255,.16);border-radius:999px;padding:3px 12px;margin:8px 0 0 6px;font-size:13px;",
    }

    def sty(html):
        def _rep(m):
            _cls = m.group(1).split()
            if _cls and all(c in STY for c in _cls):
                return 'style="' + "".join(STY[c] for c in _cls) + '"'
            return m.group(0)
        return re.sub(r'class="([^"]*)"', _rep, html)

    def H(html):
        return mo.Html(sty(html))

    mo.Html('<link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">')
    return (H,)


@app.cell(hide_code=True)
def _(H, disk_free_gb, read_env_token, torch_mod):
    _tok = "✅ توکن Hugging Face پیدا شد" if read_env_token() else "🔑 توکن Hugging Face را در تب «💾 پروژه و تنظیمات» بگذارید"
    if torch_mod.cuda.is_available():
        _p = torch_mod.cuda.get_device_properties(0)
        _gpu = f"✅ {_p.name} — {_p.total_memory / 1e9:.0f} GB"
    else:
        _gpu = "❌ GPU روشن نیست (دکمه‌ی مشخصات بالای صفحه ← RTX Pro 6000)"
    _disk = disk_free_gb()
    _dk = f"💽 فضای خالی دیسک: {_disk:.0f} GB" + (" ⚠️ کم است (مدل ~۱۳۵ گیگ)" if 0 <= _disk < 150 else "")
    H(f"""<div class="yar-root"><div class="yar-head">
      <h1 style="margin:0;font-size:26px;color:#fff">🎬 استودیو داستان سینمایی — MiniMax H3</h1>
      <div style="opacity:.9;margin-top:4px">عکس شخصیت‌ها + صحنه‌های داستان ← فیلم با صدا، صحنه‌به‌صحنه</div>
      <span class="yar-pill">{_gpu}</span><span class="yar-pill">{_dk}</span><span class="yar-pill">{_tok}</span>
    </div></div>""")
    return


@app.cell(hide_code=True)
def _(CANVAS, PROJECT, SECONDS, STYLES, mo, read_env_token):
    _d = PROJECT["drafts"]

    def _pick(key, options, default):
        _v = _d.get(key)
        return _v if _v in options else default

    style_dd = mo.ui.dropdown(options=list(STYLES), value=_pick("style", STYLES, list(STYLES)[0]), label="سبک")
    canvas_dd = mo.ui.dropdown(options=list(CANVAS), value=_pick("canvas", CANVAS, list(CANVAS)[0]), label="کیفیت")
    aspect_dd = mo.ui.dropdown(options=["16:9 افقی", "9:16 عمودی"], value=_pick("aspect", ["16:9 افقی", "9:16 عمودی"],
                               "16:9 افقی"), label="نسبت تصویر")
    sec_dd = mo.ui.dropdown(options=list(SECONDS), value=_pick("seconds", SECONDS, "۱۰ ثانیه"), label="طول هر صحنه")
    seed_in = mo.ui.number(value=-1, start=-1, stop=2**31 - 1, step=1, label="Seed (‎-1 = تصادفی)")
    hf_token = mo.ui.text(value=read_env_token(), kind="password", label="توکن Hugging Face", full_width=True)
    story_desc = mo.ui.text_area(
        label="فضای داستان (انگلیسی) — مکان، زمان، حال‌وهوا؛ در همه‌ی صحنه‌ها تکرار می‌شود",
        value=_d.get("story", ""), rows=3, full_width=True,
        placeholder="A frozen Norse mountain plateau at dusk, ancient stone ruins, heavy falling snow.")
    scenes_in = mo.ui.text_area(
        label="صحنه‌ها (انگلیسی) — هر خط یک صحنه", value=_d.get("scenes", ""), rows=12, full_width=True,
        placeholder="Scene 1 on line 1...\nScene 2 on line 2...")
    sfx_in = mo.ui.text(label="صدا و موسیقی (خالی = موسیقی سینمایی + صداهای واقعی)", value=_d.get("sfx", ""),
                        full_width=True)
    ticker = mo.ui.refresh(options=["2s", "5s"], default_interval="2s", label="به‌روزرسانی خودکار")
    go_btn = mo.ui.run_button(label="🎬 ساخت / ادامه‌ی فیلم", kind="success")
    merge_btn = mo.ui.run_button(label="🎞 ساخت دوباره‌ی فیلم نهایی")
    reset_btn = mo.ui.run_button(label="🔄 فیلم جدید (پاک کردن صحنه‌ها)", kind="danger")
    return (
        aspect_dd, canvas_dd, go_btn, hf_token, merge_btn, reset_btn, scenes_in, sec_dd, seed_in, sfx_in,
        story_desc, style_dd, ticker,
    )


@app.cell(hide_code=True)
def _(LOCK, PROJECT, aspect_dd, canvas_dd, save_project, scenes_in, sec_dd, sfx_in, story_desc, style_dd):
    with LOCK:
        PROJECT["drafts"].update(style=style_dd.value, canvas=canvas_dd.value, aspect=aspect_dd.value,
                                 seconds=sec_dd.value, story=story_desc.value, scenes=scenes_in.value,
                                 sfx=sfx_in.value)
    save_project()
    return


@app.cell(hide_code=True)
def _(mo):
    char_name = mo.ui.text(label="نام (انگلیسی)", placeholder="Kratos")
    char_upload = mo.ui.file(filetypes=[".png", ".jpg", ".jpeg", ".webp"], kind="area", label="عکس کاراکتر")
    char_look = mo.ui.text_area(label="ظاهر (انگلیسی)", rows=3, full_width=True,
                                placeholder="a huge bald warrior with ash-white skin and a red tattoo, ...")
    char_role = mo.ui.text_area(label="سلاح، توانایی و نقش در داستان (انگلیسی — اختیاری)", rows=3, full_width=True,
                                placeholder="Fights with a frost axe that he throws and recalls; slow, heavy strikes.")
    char_add = mo.ui.run_button(label="💾 ذخیره‌ی کاراکتر", kind="success")
    backup_btn = mo.ui.run_button(label="📦 ساخت فایل پشتیبان")
    restore_file = mo.ui.file(filetypes=[".zip"], kind="area", label="فایل پشتیبان (zip)", max_size=1_500_000_000)
    restore_btn = mo.ui.run_button(label="♻️ بازگردانی", kind="warn")
    return backup_btn, char_add, char_look, char_name, char_role, char_upload, restore_btn, restore_file


@app.cell(hide_code=True)
def _(PROJECT, get_rev, mo):
    get_rev()
    _names = list(PROJECT["chars"])
    cast_ms = mo.ui.multiselect(options=_names, value=[n for n in PROJECT["drafts"].get("cast", []) if n in _names][:4],
                                max_selections=4, label="شخصیت‌های این فیلم (۱ تا ۴)")
    char_del_dd = mo.ui.dropdown(options=_names or ["—"], label="کاراکتر")
    char_del_btn = mo.ui.run_button(label="🗑 حذف کاراکتر")
    _sc = PROJECT["scenes"]
    redo_dd = mo.ui.dropdown(options=[f"صحنه {i + 1}" for i in range(len(_sc))] or ["—"], label="صحنه")
    redo_btn = mo.ui.run_button(label="🔁 ساخت دوباره‌ی این صحنه", kind="warn")
    return cast_ms, char_del_btn, char_del_dd, redo_btn, redo_dd


@app.cell(hide_code=True)
def _(LOCK, PROJECT, cast_ms, save_project):
    with LOCK:
        PROJECT["drafts"]["cast"] = list(cast_ms.value)
    save_project()
    return


@app.cell(hide_code=True)
def _(H, JOB, aspect_dd, bump, canvas_dd, mo, sec_dd, seed_in, style_dd, ticker, time):
    ticker
    _seen = getattr(bump, "_seen", 0)
    if JOB["version"] != _seen:
        bump._seen = JOB["version"]
        bump()
    if JOB["running"]:
        _el = int(time.time() - JOB["start"])
        _pct = int(100 * JOB["step"] / JOB["total"]) if JOB["total"] else 3
        _steps = f" — {JOB['step']} از {JOB['total']}" if JOB["total"] else ""
        _status = H(f"""<div class="yar-root"><div class="yar-card">
          <div class="yar-sec">⏳ {JOB['title']}</div>
          <div>{JOB['detail']}{_steps} — زمان: {_el // 60:02d}:{_el % 60:02d}</div>
          <div style="height:10px;background:#ece8fb;border-radius:99px;overflow:hidden;margin:8px 0"><div style="height:100%;width:{_pct}%;background:linear-gradient(90deg,#6c4fd8,#a48bff)"></div></div>
          <div class="yar-muted">کار در پس‌زمینه ادامه دارد. هر صحنه‌ی تمام‌شده روی دیسک ذخیره می‌شود.</div>
        </div></div>""")
    elif JOB.get("error"):
        _status = mo.callout(mo.vstack([
            mo.md(f"**❌ خطا در «{JOB['title']}»:** {JOB['error']}"),
            mo.accordion({"جزئیات فنی": mo.md(f"```\n{JOB.get('trace', '')}\n```")}),
        ]), kind="danger")
    elif JOB.get("message"):
        _status = mo.callout(mo.md(JOB["message"]), kind="success")
    else:
        _status = mo.md("")
    mo.vstack([
        H('<div class="yar-root">' + mo.hstack([style_dd, canvas_dd, aspect_dd, sec_dd, seed_in, ticker],
                                                justify="start", gap=1.2, wrap=True).text + "</div>"),
        _status,
    ])
    return


@app.cell(hide_code=True)
def _(
    JOB, LOCK, OUT, PROJECT, char_add, char_look, char_name, char_role, char_upload, mo, re, rel, save_project,
    time,
):
    mo.stop(not char_add.value)
    _name = re.sub(r"\s+", " ", char_name.value.strip())
    if not _name:
        JOB.update(error=None, title="", message="⚠️ نام کاراکتر را بنویسید.")
    elif not char_upload.value:
        JOB.update(error=None, title="", message="⚠️ یک عکس برای کاراکتر انتخاب کنید.")
    else:
        _dst = OUT / "characters" / f"{int(time.time())}_{re.sub(r'[^A-Za-z0-9]+', '_', _name)}.png"
        _dst.write_bytes(char_upload.contents(0))
        with LOCK:
            PROJECT["chars"][_name] = {"image": rel(_dst), "look": char_look.value.strip(),
                                       "role": char_role.value.strip()}
        save_project()
        JOB.update(error=None, title="", message=f"✅ کاراکتر «{_name}» ذخیره شد.")
    JOB["version"] += 1
    return


@app.cell(hide_code=True)
def _(JOB, LOCK, PROJECT, char_del_btn, char_del_dd, mo, save_project):
    mo.stop(not char_del_btn.value)
    with LOCK:
        _ok = PROJECT["chars"].pop(char_del_dd.value, None)
    save_project()
    JOB.update(error=None, title="", message="🗑 حذف شد." if _ok else "چیزی برای حذف نبود.")
    JOB["version"] += 1
    return


@app.cell(hide_code=True)
def _(DEFAULT_SFX, STYLES, hashlib):
    def build_prompt(scene, idx, total, cast, chars, story, style_key, sfx):
        """پرامپت هر صحنه؛ کاراکترها با شماره‌ی عکسشان (<Picture n>) معرفی می‌شوند"""
        _p = [STYLES[style_key] + "."]
        _who = []
        for _i, _n in enumerate(cast, start=1):
            _c = chars[_n]
            _t = f"{_n} is the person shown in <Picture {_i}>"
            if _c.get("look"):
                _t += f" ({_c['look'].rstrip('.')})"
            _who.append(_t + ".")
        _p.append("Characters: " + " ".join(_who))
        for _n in cast:
            if chars[_n].get("role"):
                _p.append(f"{_n}: {chars[_n]['role'].rstrip('.')}.")
        _p.append("Every character keeps exactly the same face, body, hair, costume and weapons as in their picture, "
                  "and uses only the weapons shown in their own picture.")
        if story.strip():
            _p.append("Setting: " + story.strip().rstrip(".") + ".")
        _p.append(f"Scene {idx} of {total}: " + scene.strip().rstrip(".") + ".")
        _p.append("Audio: " + (sfx.strip() or DEFAULT_SFX).rstrip(".") + ".")
        return " ".join(_p)

    def key_of(prompt, refs):
        return hashlib.sha1((prompt + "|" + "|".join(refs)).encode("utf-8")).hexdigest()[:16]
    return build_prompt, key_of


@app.cell(hide_code=True)
def _(
    CANVAS, JOB, LOCK, OUT, PROJECT, SECONDS, absp, aspect_dd, build_prompt, canvas_dd, cast_ms, clear, concat,
    engine, go_btn, hf_token, key_of, mo, random, rel, save_project, save_scene, scenes_in, sec_dd, seed_in,
    sfx_in, start_job, story_desc, style_dd, time, torch_mod, use_token,
):
    mo.stop(not go_btn.value)
    _lines = [l.strip() for l in scenes_in.value.splitlines() if l.strip()][:12]
    _cast = [n for n in cast_ms.value if n in PROJECT["chars"]]
    if not _cast:
        JOB.update(error=None, title="", message="⚠️ در تب «🎬 فیلم» حداقل یک شخصیت انتخاب کنید.")
        JOB["version"] += 1
    elif not _lines:
        JOB.update(error=None, title="", message="⚠️ صحنه‌ها را بنویسید (هر خط یک صحنه).")
        JOB["version"] += 1
    else:
        def _launch(lines, cast, cfg):
            _chars = PROJECT["chars"]
            _refs = [str(absp(_chars[n]["image"])) for n in cast]
            _n = len(lines)
            # فهرست صحنه‌ها با متن فعلی هماهنگ می‌شود؛ صحنه‌ای که متنش عوض شده دوباره ساخته می‌شود
            with LOCK:
                _old = {s.get("key"): s for s in PROJECT["scenes"]}
                _new = []
                for _i, _l in enumerate(lines, start=1):
                    _prompt = build_prompt(_l, _i, _n, cast, _chars, cfg["story"], cfg["style"], cfg["sfx"])
                    _k = key_of(_prompt + f"|{cfg['seconds']}|{cfg['hw']}", _refs)
                    _s = _old.get(_k) or {"key": _k, "text": _l, "prompt": _prompt, "embeds": None, "video": None}
                    _new.append(_s)
                PROJECT["scenes"] = _new
                PROJECT["final"] = None
            save_project()

            def _work():
                engine.job = JOB
                use_token(cfg["token"])
                _t0 = time.time()
                _scenes = PROJECT["scenes"]
                _need_read = [s for s in _scenes if not s.get("video") and not s.get("embeds")]
                # ── مرحله‌ی ۱: خواندن همه‌ی صحنه‌ها با مدل متن
                if _need_read:
                    JOB["title"] = "مرحله‌ی ۱ از ۳ — خواندن صحنه‌ها"
                    engine.load_reader(cfg["token"])
                    JOB["total"] = len(_need_read)
                    for _j, _s in enumerate(_need_read):
                        JOB["step"] = _j
                        JOB["detail"] = f"خواندن صحنه‌ی {_scenes.index(_s) + 1}"
                        _vals = engine.read(_s["prompt"], _refs, cfg["seconds"], cfg["hw"])
                        _p = OUT / "embeds" / f"{_s['key']}.pt"
                        torch_mod.save(_vals, _p)
                        with LOCK:
                            _s["embeds"] = rel(_p)
                        save_project()
                        JOB["version"] += 1
                    JOB["step"] = len(_need_read)
                # ── مرحله‌ی ۲: ساخت ویدیوی همه‌ی صحنه‌ها
                _need_make = [s for s in _scenes if not s.get("video")]
                if _need_make:
                    JOB["title"] = "مرحله‌ی ۲ از ۳ — ساخت صحنه‌ها"
                    engine.load_maker(cfg["token"])
                    JOB["total"] = len(_need_make)
                    for _j, _s in enumerate(_need_make):
                        JOB["step"] = _j
                        _idx = _scenes.index(_s) + 1
                        JOB["detail"] = f"ساخت صحنه‌ی {_idx} ({cfg['seconds']} ثانیه)"
                        _vals = torch_mod.load(absp(_s["embeds"]), weights_only=False)
                        _seed = cfg["seed"] if cfg["seed"] >= 0 else random.randint(0, 2**31 - 1)
                        try:
                            _res = engine.make(_vals, cfg["seconds"], cfg["hw"], _seed)
                        except Exception as _e:
                            if "out of memory" not in str(_e).lower() or cfg["hw"] == cfg["hw_fast"]:
                                raise
                            clear()
                            JOB["detail"] = f"صحنه‌ی {_idx}: حافظه کم بود؛ ساخت با ۵۴۴p"
                            _res = engine.make(_vals, cfg["seconds"], cfg["hw_fast"], _seed)
                        _vp = OUT / "scenes" / f"scene_{_idx:02d}_{int(time.time())}.mp4"
                        save_scene(_res, _vp)
                        del _res
                        clear()
                        with LOCK:
                            _s["video"] = rel(_vp)
                            _s["seed"] = _seed
                        save_project()
                        JOB["version"] += 1
                    JOB["step"] = len(_need_make)
                # ── مرحله‌ی ۳: چسباندن
                JOB["title"] = "مرحله‌ی ۳ از ۳ — فیلم نهایی"
                JOB["detail"] = "چسباندن صحنه‌ها…"
                _out = concat([absp(s["video"]) for s in _scenes], OUT / "final" / f"film_{int(time.time())}.mp4")
                with LOCK:
                    PROJECT["final"] = rel(_out)
                save_project()
                return f"✅ فیلم آماده شد: {len(_scenes)} صحنه، حدود {int((time.time() - _t0) / 60)} دقیقه."

            if not start_job("ساخت فیلم", _work):
                JOB["message"] = "⏳ یک کار دیگر در حال انجام است."
                JOB["version"] += 1

        _hw = CANVAS[canvas_dd.value][aspect_dd.value]
        _hw_fast = CANVAS[list(CANVAS)[1]][aspect_dd.value]
        _launch(_lines, _cast, {
            "story": story_desc.value, "style": style_dd.value, "sfx": sfx_in.value,
            "seconds": SECONDS[sec_dd.value], "hw": _hw, "hw_fast": _hw_fast,
            "seed": int(seed_in.value if seed_in.value is not None else -1), "token": hf_token.value.strip(),
        })
    return


@app.cell(hide_code=True)
def _(JOB, LOCK, PROJECT, mo, redo_btn, redo_dd, save_project):
    mo.stop(not redo_btn.value)
    if JOB["running"]:
        JOB["message"] = "⏳ صبر کنید تا کار فعلی تمام شود."
    else:
        try:
            _i = int(redo_dd.value.split()[-1]) - 1
            with LOCK:
                PROJECT["scenes"][_i]["video"] = None
                PROJECT["final"] = None
            save_project()
            JOB.update(error=None, title="",
                       message=f"🔁 صحنه‌ی {_i + 1} پاک شد. «🎬 ساخت / ادامه‌ی فیلم» آن را با seed تازه می‌سازد.")
        except Exception:
            JOB.update(error=None, title="", message="صحنه‌ای انتخاب نشده.")
    JOB["version"] += 1
    return


@app.cell(hide_code=True)
def _(JOB, LOCK, PROJECT, mo, reset_btn, save_project):
    mo.stop(not reset_btn.value)
    if JOB["running"]:
        JOB["message"] = "⏳ صبر کنید تا کار فعلی تمام شود."
    else:
        with LOCK:
            PROJECT["scenes"] = []
            PROJECT["final"] = None
        save_project()
        JOB.update(error=None, title="", message="🔄 آماده‌ی فیلم جدید. (فیلم‌های قبلی در پوشه‌ی final می‌مانند.)")
    JOB["version"] += 1
    return


@app.cell(hide_code=True)
def _(JOB, LOCK, OUT, PROJECT, absp, concat, merge_btn, mo, rel, save_project, start_job, time):
    mo.stop(not merge_btn.value)
    _done = [s for s in PROJECT["scenes"] if s.get("video")]
    if not _done:
        JOB.update(error=None, title="", message="⚠️ هنوز صحنه‌ای ساخته نشده.")
        JOB["version"] += 1
    else:
        def _launch(done):
            def _work():
                JOB["detail"] = "چسباندن صحنه‌ها…"
                _out = concat([absp(s["video"]) for s in done], OUT / "final" / f"film_{int(time.time())}.mp4")
                with LOCK:
                    PROJECT["final"] = rel(_out)
                save_project()
                return f"✅ فیلم نهایی از {len(done)} صحنه ساخته شد."

            if not start_job("فیلم نهایی", _work):
                JOB["message"] = "⏳ یک کار دیگر در حال انجام است."
                JOB["version"] += 1
        _launch(_done)
    return


@app.cell(hide_code=True)
def _(JOB, LOCK, OUT, PROJECT, backup_btn, mo, rel, save_project, start_job, time, zipfile):
    mo.stop(not backup_btn.value)

    def _work():
        JOB["detail"] = "ساخت فایل پشتیبان (بدون فایل‌های embeds)…"
        _zp = OUT / "backups" / f"h3_story_backup_{int(time.strftime('%Y%m%d%H%M%S'))}.zip"
        with zipfile.ZipFile(_zp, "w", zipfile.ZIP_STORED) as _z:
            _z.writestr("project.json", (OUT / "project.json").read_text(encoding="utf-8"))
            for _sub in ("characters", "scenes", "final"):
                for _f in (OUT / _sub).glob("*"):
                    _z.write(_f, f"{_sub}/{_f.name}")
        with LOCK:
            PROJECT["backup"] = rel(_zp)
        save_project()
        return "✅ فایل پشتیبان آماده است؛ در تب «💾 پروژه و تنظیمات» دانلودش کنید."

    if not start_job("پشتیبان", _work):
        JOB["message"] = "⏳ یک کار دیگر در حال انجام است."
        JOB["version"] += 1
    return


@app.cell(hide_code=True)
def _(JOB, LOCK, OUT, PROJECT, json, mo, restore_btn, restore_file, save_project, zipfile):
    mo.stop(not restore_btn.value)
    import io as _io
    if not restore_file.value:
        JOB.update(error=None, title="", message="⚠️ اول فایل zip پشتیبان را انتخاب کنید.")
    else:
        with zipfile.ZipFile(_io.BytesIO(restore_file.contents(0))) as _z:
            for _m in _z.namelist():
                if _m != "project.json" and not _m.endswith("/"):
                    (OUT / _m).parent.mkdir(parents=True, exist_ok=True)
                    (OUT / _m).write_bytes(_z.read(_m))
            _data = json.loads(_z.read("project.json").decode("utf-8"))
        for _s in _data.get("scenes", []):
            _s["embeds"] = None
        with LOCK:
            for _k in ("chars", "scenes", "final", "drafts"):
                if _k in _data:
                    PROJECT[_k] = _data[_k]
        save_project()
        JOB.update(error=None, title="", message="♻️ پروژه برگردانده شد. برای دیدن متن‌ها یک‌بار Run all بزنید.")
    JOB["version"] += 1
    return


@app.cell(hide_code=True)
def _(H, PROJECT, absp, get_rev, mo):
    get_rev()
    _chars = PROJECT["chars"]
    chars_view = mo.hstack([
        mo.vstack([
            mo.image(src=str(absp(_c["image"])), width=170, rounded=True),
            H(f'<div class="yar-root"><b>{_n}</b></div>'),
        ], gap=0.3) for _n, _c in _chars.items()
    ], wrap=True, justify="start", gap=1) if _chars else H('<div class="yar-root yar-muted">هنوز شخصیتی نیست.</div>')

    def _video(path, label):
        _p = absp(path)
        return mo.vstack([
            mo.video(src=str(_p), controls=True, width="100%"),
            mo.download(data=lambda _p=_p: _p.read_bytes(), filename=_p.name, mimetype="video/mp4", label=label),
        ], gap=0.3)

    _items = []
    for _i, _s in enumerate(PROJECT["scenes"], start=1):
        _state = "✅" if _s.get("video") else ("📖 خوانده شد" if _s.get("embeds") else "⏳ در صف")
        _body = [H(f'<div class="yar-root"><b>صحنه {_i}</b> <span class="yar-badge">{_state}</span>'
                   f'<div class="yar-muted yar-ltr">{_s["text"]}</div></div>')]
        if _s.get("video"):
            _body.append(_video(_s["video"], "⬇️ دانلود صحنه"))
        _items.append(mo.vstack(_body, gap=0.3))
    scenes_view = mo.vstack(_items, gap=1.1) if _items else H(
        '<div class="yar-root yar-muted">هنوز صحنه‌ای ساخته نشده.</div>')
    final_view = (mo.vstack([H('<div class="yar-root yar-sec">🏁 فیلم نهایی</div>'),
                             _video(PROJECT["final"], "⬇️ دانلود فیلم نهایی")])
                  if PROJECT.get("final") else mo.md(""))
    if PROJECT.get("backup"):
        _bp = absp(PROJECT["backup"])
        backup_view = mo.download(data=lambda: _bp.read_bytes(), filename=_bp.name, mimetype="application/zip",
                                  label=f"⬇️ دانلود {_bp.name}")
    else:
        backup_view = mo.md("")
    return backup_view, chars_view, final_view, scenes_view


@app.cell(hide_code=True)
def _(
    H, backup_btn, backup_view, cast_ms, char_add, char_del_btn, char_del_dd, char_look, char_name, char_role,
    char_upload, chars_view, final_view, go_btn, hf_token, merge_btn, mo, redo_btn, redo_dd, reset_btn,
    restore_btn, restore_file, scenes_in, scenes_view, sfx_in, story_desc,
):
    def _R(x):
        return H('<div class="yar-root">' + (x.text if hasattr(x, "text") else str(x)) + "</div>")

    def _sec(title, note=""):
        return H(f'<div class="yar-root"><div class="yar-sec">{title}</div>'
                 + (f'<div class="yar-muted">{note}</div>' if note else "") + "</div>")

    def _card(*items):
        return H('<div class="yar-root"><div class="yar-card">' + mo.vstack(list(items), gap=0.7).text + "</div></div>")

    _tab_film = mo.hstack([
        mo.vstack([_card(_sec("🎞 صحنه‌ها"), scenes_view), final_view], gap=1),
        mo.vstack([
            _card(_sec("👥 شخصیت‌ها", "ترتیب انتخاب = شماره‌ی عکس (<Picture 1>، <Picture 2>…)"), _R(cast_ms)),
            _card(_sec("📖 داستان"), _R(story_desc), _R(scenes_in), _R(sfx_in),
                  H('<div class="yar-root yar-muted">مرحله‌ی ۱: مدل متن همه‌ی صحنه‌ها را می‌خواند. مرحله‌ی ۲: مدل ویدیو '
                    'همه را پشت سر هم می‌سازد. مرحله‌ی ۳: چسباندن. اگر وسط کار قطع شد، دوباره دکمه‌ی ساخت را '
                    'بزنید؛ از همان‌جا ادامه می‌دهد.</div>'),
                  _R(mo.hstack([go_btn, merge_btn, reset_btn], justify="start", gap=1, wrap=True))),
            _card(_sec("🔁 ساخت دوباره‌ی یک صحنه"), _R(mo.hstack([redo_dd, redo_btn], justify="start", gap=1))),
        ], gap=1),
    ], widths=[1.15, 1], gap=1.5, align="start")

    _tab_char = mo.hstack([
        mo.vstack([_card(_sec("👥 همه‌ی شخصیت‌ها"), chars_view),
                   _card(_R(mo.hstack([char_del_dd, char_del_btn], justify="start", gap=1)))], gap=1),
        _card(_sec("➕ شخصیت جدید", "بهترین عکس: تمام‌قد، از جلو، با لباس و سلاح خودش"),
              _R(char_name), _R(char_upload), _R(char_look), _R(char_role), _R(char_add)),
    ], widths=[1.3, 1], gap=1.5, align="start")

    _tab_proj = mo.hstack([
        _card(_sec("💾 پشتیبان", "molab فایل‌ها را بعد از خاموش شدن نگه نمی‌دارد."),
              _R(backup_btn), backup_view, _R(restore_file), _R(restore_btn)),
        _card(_sec("🔑 توکن Hugging Face"), _R(hf_token),
              H('<div class="yar-root yar-muted">در صفحه‌ی MiniMaxAI/MiniMax-H3 در Hugging Face شرایط مدل را قبول '
                'کنید. می‌توانید در پنل <b>Files</b> فایلی به اسم <code>.env</code> بسازید و بنویسید: '
                '<code class="yar-ltr">HF_TOKEN=hf_...</code></div>')),
    ], widths=[1, 1], gap=1.5, align="start")

    mo.ui.tabs({"🎬 فیلم": _tab_film, "👤 شخصیت‌ها": _tab_char, "💾 پروژه و تنظیمات": _tab_proj})
    return


if __name__ == "__main__":
    app.run()
