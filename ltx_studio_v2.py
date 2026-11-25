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
#  استودیو ویدیو LTX 2.5 — برای molab (marimo)
#  1) GPU را از دکمه‌ی مشخصات بالای صفحه روشن کنید   2) Run all

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="full", app_title="LTX 2.5 Studio")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import os
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
    import gc, json, time, random, shutil, subprocess, wave, inspect, traceback, threading, zipfile, re
    from pathlib import Path
    import numpy as np
    from PIL import Image
    return (
        Image, Path, gc, inspect, json, mo, np, os, random, re, shutil,
        subprocess, threading, time, traceback, wave, zipfile,
    )


@app.cell(hide_code=True)
def _():
    # ───────────── ۱۰ سبک ─────────────
    STYLES = {
        "🎬 فیلم سینمایی": "Cinematic feature film, shot on 35mm anamorphic lens, dramatic motivated lighting, shallow depth of field, rich color grading, subtle film grain",
        "📱 ویدیو طبیعی / واقعی": "Natural realistic video, handheld modern camera, natural daylight, true-to-life colors, authentic everyday realism",
        "🎥 لایو اکشن": "Live-action film footage, real actors, practical sets, professional cinema camera, realistic skin and fabric textures, natural motion",
        "🖍 کارتون": "2D cartoon style, bold clean outlines, flat vibrant colors, expressive exaggerated characters, classic TV cartoon animation",
        "🧸 انیمیشن سه‌بعدی": "High-quality 3D animated feature film style, stylized characters, soft global illumination, detailed textures, family animated movie look",
        "🌸 انیمه": "Japanese anime style, cel-shaded characters, detailed hand-painted backgrounds, expressive eyes, dynamic anime cinematography",
        "📽 مستند": "Documentary footage, observational camera, natural available light, authentic details, slightly handheld framing",
        "🕯 ترسناک / تاریک": "Dark horror film style, low-key lighting, deep shadows, desaturated cold tones, eerie atmosphere, drifting fog",
        "🐉 فانتزی حماسی": "Epic fantasy film style, grand scale, volumetric god rays, magical atmosphere, rich saturated colors, sweeping cinematography",
        "🧱 استاپ‌موشن خمیری": "Stop-motion claymation style, handcrafted clay characters, miniature sets, tactile fingerprint textures, charming handmade look",
    }
    SPEECH = {
        "معمولی": "in a natural conversational tone",
        "آرام": "calmly and softly",
        "نجوا / زمزمه": "in a quiet whisper",
        "خشن / تهدیدآمیز": "harshly and aggressively, in a threatening low voice",
        "فریاد": "shouting loudly at the top of their lungs",
        "عصبانی": "angrily, through gritted teeth",
        "غمگین": "sadly, with a trembling voice",
        "گریان": "while crying, voice breaking",
        "شاد": "happily and cheerfully",
        "هیجان‌زده": "excitedly, speaking fast",
        "ترسیده": "fearfully, breathless and shaky",
        "مرموز": "mysteriously, slow and low",
        "طعنه‌آمیز": "sarcastically",
        "فرمان‌دهنده": "with a commanding, authoritative voice",
        "خسته": "wearily, tired and slow",
        "مهربان / عاشقانه": "tenderly, warm and gentle",
    }
    LANGS = {
        "انگلیسی (بهترین نتیجه)": "English",
        "فارسی": "Persian (Farsi)",
        "دری": "Dari Persian with an Afghan accent",
        "فرانسوی": "French",
        "عربی": "Arabic",
        "ترکی": "Turkish",
    }
    CAMERA = {
        "ثابت": "Static locked-off camera.",
        "زوم آرام به داخل": "The camera slowly pushes in.",
        "عقب‌کشیدن دوربین": "The camera slowly pulls back.",
        "پن به چپ": "The camera pans slowly to the left.",
        "پن به راست": "The camera pans slowly to the right.",
        "تعقیب سوژه (تراکینگ)": "The camera tracks alongside the subject.",
        "دوربین روی دست": "Handheld camera with subtle natural shake.",
        "چرخش دور سوژه": "The camera orbits slowly around the subject.",
        "کرین رو به بالا": "The camera cranes up to reveal the scene.",
        "نمای نزدیک صورت": "Close-up shot on the face.",
        "نمای باز": "Wide shot showing the whole environment.",
        "نمای اول‌شخص (POV)": "First-person point-of-view shot.",
        "پهپاد هوایی": "Aerial drone shot gliding over the scene.",
    }
    DURATIONS = {"۵ ثانیه": 121, "۷ ثانیه": 169, "۱۰ ثانیه": 241}  # 24fps, frames % 8 == 1
    FPS = 24
    ASPECTS = ["16:9 افقی", "9:16 عمودی", "1:1 مربع"]
    QUALITIES = ["1080p (1920×1080)", "720p (1280×720)"]
    # ساخت دومرحله‌ای رسمی LTX 2.5: مرحله‌ی ۱ با نصف اندازه، مرحله‌ی ۲ دو برابر
    STAGE1 = {
        "1080p (1920×1080)": {"16:9 افقی": (544, 960), "9:16 عمودی": (960, 544), "1:1 مربع": (544, 544)},
        "720p (1280×720)": {"16:9 افقی": (384, 640), "9:16 عمودی": (640, 384), "1:1 مربع": (384, 384)},
    }
    SINGLE = {"16:9 افقی": (736, 1280), "9:16 عمودی": (1280, 736), "1:1 مربع": (736, 736)}
    FINAL = {
        "1080p (1920×1080)": {"16:9 افقی": (1080, 1920), "9:16 عمودی": (1920, 1080), "1:1 مربع": (1080, 1080)},
        "720p (1280×720)": {"16:9 افقی": (720, 1280), "9:16 عمودی": (1280, 720), "1:1 مربع": (720, 720)},
    }
    IMG_SIZE = {"16:9 افقی": (1024, 1792), "9:16 عمودی": (1792, 1024), "1:1 مربع": (1280, 1280)}
    EDIT_SIZE = {"16:9 افقی": (928, 1664), "9:16 عمودی": (1664, 928), "1:1 مربع": (1328, 1328)}
    IMAGE_MODELS = {
        "Z-Image Turbo (سریع)": ("Tongyi-MAI/Z-Image-Turbo", 9, 0.0),
        "Qwen-Image (کیفیت بالا، کندتر)": ("Qwen/Qwen-Image", 40, 4.0),
    }
    EDIT_ID = "Qwen/Qwen-Image-Edit-2511"
    LTX_ID = "Lightricks/LTX-2.5-Diffusers"
    return (
        ASPECTS, CAMERA, DURATIONS, EDIT_ID, EDIT_SIZE, FINAL, FPS, IMAGE_MODELS,
        IMG_SIZE, LANGS, LTX_ID, QUALITIES, SINGLE, SPEECH, STAGE1, STYLES,
    )


@app.cell(hide_code=True)
def _(Path, json, os, threading):
    # ───────────── پروژه: همه‌چیز روی دیسک ذخیره می‌شود ─────────────
    OUT = Path("ltx_studio_output").resolve()
    for _d in ("images", "characters", "shots", "frames", "final", "backups"):
        (OUT / _d).mkdir(parents=True, exist_ok=True)
    PROJECT_FILE = OUT / "project.json"
    LOCK = threading.RLock()

    def _empty():
        return {"images": [], "chars": {}, "shots": [], "final": None, "drafts": {}, "log": "", "backup": None}

    def load_project():
        _p = _empty()
        try:
            _p.update(json.loads(PROJECT_FILE.read_text(encoding="utf-8")))
        except Exception:
            pass
        _p["images"] = [i for i in _p["images"] if (OUT / i["path"]).exists()]
        _p["chars"] = {k: v for k, v in _p["chars"].items() if (OUT / v["image"]).exists()}
        _p["shots"] = [s for s in _p["shots"] if (OUT / s["video"]).exists()]
        if _p.get("final") and not (OUT / _p["final"]).exists():
            _p["final"] = None
        if _p.get("backup") and not (OUT / _p["backup"]).exists():
            _p["backup"] = None
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
    # ───────────── کار در پس‌زمینه: صفحه هیچ‌وقت قفل نمی‌شود ─────────────
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
                _oom = "out of memory" in str(_e).lower()
                JOB["error"] = (
                    "حافظه‌ی کارت گرافیک کافی نبود. کیفیت 720p یا مدت کوتاه‌تر را امتحان کنید."
                    if _oom else f"{type(_e).__name__}: {_e}"
                )
                JOB["trace"] = traceback.format_exc()[-3000:]
                JOB["message"] = ""
            finally:
                JOB["running"] = False
                JOB["version"] += 1

        threading.Thread(target=_run, daemon=True).start()
        return True
    return JOB, start_job


@app.cell(hide_code=True)
def _(DURATIONS, EDIT_ID, FPS, Image, LTX_ID, STAGE1, SINGLE, gc, inspect, np, os, shutil, subprocess, wave):
    import torch

    def ffmpeg_exe():
        _f = shutil.which("ffmpeg")
        if _f:
            return _f
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()

    def fit_image(img, h, w):
        img = img.convert("RGB")
        _sw, _sh = img.size
        _s = max(w / _sw, h / _sh)
        img = img.resize((max(w, round(_sw * _s)), max(h, round(_sh * _s))), Image.LANCZOS)
        _l, _t = (img.width - w) // 2, (img.height - h) // 2
        return img.crop((_l, _t, _l + w, _t + h))

    def sharpness(frame):
        _g = frame.astype(np.float32).mean(axis=2)
        _lap = (-4 * _g[1:-1, 1:-1] + _g[:-2, 1:-1] + _g[2:, 1:-1] + _g[1:-1, :-2] + _g[1:-1, 2:])
        return float(_lap.var())

    def best_end_frame(frames, window=10):
        """واضح‌ترین فریم در انتهای شات (بدون محوی حرکت) برای ادامه‌ی داستان"""
        _n = len(frames)
        _cands = list(range(max(0, _n - window), _n))
        _scores = [sharpness(frames[i][::2, ::2]) for i in _cands]
        _best = max(_scores)
        # اگر آخرین فریم تقریباً به همان وضوح است، همان را نگه دار
        if _scores[-1] >= 0.9 * _best:
            return _n - 1
        return _cands[int(np.argmax(_scores))]

    def _to_frames(v):
        if isinstance(v, (list, tuple)):
            v = v[0]
            if isinstance(v, (list, tuple)) and v and isinstance(v[0], Image.Image):
                return np.stack([np.asarray(f.convert("RGB")) for f in v])
        if hasattr(v, "detach"):
            v = v.detach().float().cpu().numpy()
        v = np.asarray(v)
        if v.ndim == 5:
            v = v[0]
        if v.ndim == 4 and v.shape[1] in (1, 3) and v.shape[-1] not in (1, 3):
            v = v.transpose(0, 2, 3, 1)
        if v.dtype != np.uint8:
            v = (np.clip(v, 0, 1) * 255).round().astype(np.uint8)
        return np.ascontiguousarray(v)

    def _to_audio(a):
        if a is None:
            return None
        if isinstance(a, (list, tuple)):
            a = a[0]
        if hasattr(a, "detach"):
            a = a.detach().float().cpu().numpy()
        a = np.asarray(a, dtype=np.float32)
        while a.ndim > 2:
            a = a[0]
        if a.ndim == 1:
            a = a[None]
        if a.shape[0] > a.shape[1]:
            a = a.T
        return a

    def write_wav(path, audio, sr, seconds):
        if audio is None:
            audio = np.zeros((1, int(sr * seconds)), dtype=np.float32)
        _pcm = (np.clip(audio, -1, 1).T * 32767).astype(np.int16)
        with wave.open(str(path), "wb") as _w:
            _w.setnchannels(audio.shape[0])
            _w.setsampwidth(2)
            _w.setframerate(int(sr))
            _w.writeframes(_pcm.tobytes())

    def encode_mp4(frames, audio, sr, out_path, final_hw):
        _h, _w = frames.shape[1:3]
        _fh, _fw = final_hw
        _wav = str(out_path) + ".wav"
        write_wav(_wav, audio, sr, len(frames) / FPS)
        _cmd = [
            ffmpeg_exe(), "-y", "-loglevel", "error",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{_w}x{_h}", "-r", str(FPS), "-i", "-",
            "-i", _wav,
            "-vf", f"scale={_fw}:{_fh}:force_original_aspect_ratio=increase:flags=lanczos,crop={_fw}:{_fh},setsar=1",
            "-af", "apad", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out_path),
        ]
        _r = subprocess.run(_cmd, input=frames.tobytes(), capture_output=True)
        try:
            os.remove(_wav)
        except OSError:
            pass
        if _r.returncode != 0:
            raise RuntimeError("ffmpeg: " + _r.stderr.decode(errors="ignore")[-800:])
        return out_path

    def _accepts(fn, kw):
        _p = inspect.signature(fn).parameters
        if any(x.kind == x.VAR_KEYWORD for x in _p.values()):
            return kw
        return {k: v for k, v in kw.items() if k in _p}

    class Engine:
        """هر لحظه فقط یک مدل روی GPU است تا حافظه پر نشود"""

        def __init__(self):
            self.kind = None
            self.model_id = None
            self.pipe = self.t2v = self.up = None
            self.job = None

        def free(self):
            self.pipe = self.t2v = self.up = None
            self.kind = self.model_id = None
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        def clean(self):
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        def _say(self, detail, step=0, total=0):
            if self.job is not None:
                self.job.update(detail=detail, step=step, total=total)

        def _cb(self, label, total):
            def _f(pipe, i, t, kw):
                self._say(label, i + 1, total)
                return kw
            return _f

        def _load(self, cls, mid, token):
            self._say("در حال دانلود/بارگذاری مدل (بار اول ممکن است تا ۲۰ دقیقه طول بکشد)…")
            _kw = dict(torch_dtype=torch.bfloat16, token=token or None)
            try:
                return cls.from_pretrained(mid, device_map="cuda", **_kw)
            except Exception as _e:
                if "gated" in str(_e).lower() or "401" in str(_e) or "403" in str(_e):
                    raise RuntimeError(
                        "دسترسی به مدل ندارید. در Hugging Face مجوز مدل را قبول کنید و توکن را در بالای صفحه بگذارید."
                    ) from _e
                gc.collect()
                return cls.from_pretrained(mid, **_kw).to("cuda")

        def _ensure(self, kind, mid, token):
            if self.kind == kind and self.model_id == mid:
                return
            self.free()
            if kind == "video":
                from diffusers import LTX2ImageToVideoPipeline
                self.pipe = self._load(LTX2ImageToVideoPipeline, mid, token)
                try:
                    self.pipe.vae.enable_tiling()
                except Exception:
                    pass
                try:
                    from diffusers import LTX2Pipeline
                    _ok = inspect.signature(LTX2Pipeline.__init__).parameters
                    self.t2v = LTX2Pipeline(**{k: v for k, v in self.pipe.components.items() if k in _ok})
                except Exception:
                    self.t2v = None
            elif kind == "edit":
                from diffusers import QwenImageEditPlusPipeline
                self.pipe = self._load(QwenImageEditPlusPipeline, mid, token)
            else:
                from diffusers import DiffusionPipeline
                self.pipe = self._load(DiffusionPipeline, mid, token)
            self.kind, self.model_id = kind, mid

        # ─────────── تصویر از متن ───────────
        def image(self, model_id, steps, cfg, prompt, h, w, seed, token):
            self._ensure("image", model_id, token)
            _g = torch.Generator("cuda").manual_seed(seed)
            _kw = dict(prompt=prompt, height=h, width=w, num_inference_steps=steps, generator=_g,
                       callback_on_step_end=self._cb("ساخت تصویر", steps))
            _params = inspect.signature(self.pipe.__call__).parameters
            if "true_cfg_scale" in _params and cfg > 1:
                _kw.update(true_cfg_scale=cfg, negative_prompt=" ")
            else:
                _kw.update(guidance_scale=cfg)
            return self.pipe(**_accepts(self.pipe.__call__, _kw)).images[0]

        # ─────────── ویرایش با عکس مرجع (حفظ چهره) ───────────
        def edit(self, images, prompt, h, w, seed, token, steps=40):
            self._ensure("edit", EDIT_ID, token)
            _g = torch.Generator("cuda").manual_seed(seed)
            _kw = dict(image=[i.convert("RGB") for i in images], prompt=prompt, negative_prompt=" ",
                       true_cfg_scale=4.0, guidance_scale=1.0, num_inference_steps=steps,
                       height=h, width=w, generator=_g,
                       callback_on_step_end=self._cb("حفظ چهره با عکس مرجع", steps))
            return self.pipe(**_accepts(self.pipe.__call__, _kw)).images[0]

        # ─────────── ویدیو LTX 2.5 ───────────
        def video(self, start_img, prompt, nf, quality, aspect, seed, token):
            self._ensure("video", LTX_ID, token)
            _notes = []
            try:
                from diffusers.pipelines.ltx2.utils import (
                    DEFAULT_NEGATIVE_PROMPT, DISTILLED_SIGMA_VALUES, STAGE_2_DISTILLED_SIGMA_VALUES,
                )
                _distilled = True
            except Exception:
                DEFAULT_NEGATIVE_PROMPT = "worst quality, inconsistent motion, blurry, jittery, distorted"
                _distilled = False
            _sr = 48000
            try:
                _sr = int(self.pipe.vocoder.config.output_sampling_rate)
            except Exception:
                pass
            _crf = {}
            try:
                import av  # noqa: F401
            except Exception:
                _crf = {"image_crf": 0}
            _dist_kw = dict(guidance_scale=1.0, audio_guidance_scale=1.0, stg_scale=0.0, audio_stg_scale=0.0,
                            modality_scale=1.0, audio_modality_scale=1.0) if _distilled else {}

            def _run(img, **kw):
                _base = dict(prompt=prompt, negative_prompt=DEFAULT_NEGATIVE_PROMPT, num_frames=nf,
                             frame_rate=float(FPS), return_dict=False, **_dist_kw, **kw)
                if img is not None:
                    return self.pipe(**_accepts(self.pipe.__call__, dict(image=img, **_crf, **_base)))
                if self.t2v is None:
                    raise RuntimeError("حالت «بدون تصویر» کار نکرد؛ یک فریم شروع انتخاب کنید.")
                return self.t2v(**_accepts(self.t2v.__call__, _base))

            if _distilled:
                try:
                    _h, _w = STAGE1[quality][aspect]
                    _img = fit_image(start_img, _h, _w) if start_img is not None else None
                    _g = torch.Generator("cuda").manual_seed(seed)
                    _n1, _n2 = len(DISTILLED_SIGMA_VALUES), len(STAGE_2_DISTILLED_SIGMA_VALUES)
                    _vl, _al = _run(_img, height=_h, width=_w, sigmas=DISTILLED_SIGMA_VALUES, generator=_g,
                                    output_type="latent", callback_on_step_end=self._cb("ویدیو — مرحله‌ی ۱ از ۲", _n1))
                    self._say("بزرگ‌نمایی ×۲…")
                    if self.up is None:
                        from diffusers import LTX2LatentUpsamplePipeline
                        from diffusers.pipelines.ltx2.latent_upsampler import LTX2LatentUpsamplerModel
                        _m = LTX2LatentUpsamplerModel.from_pretrained(
                            LTX_ID, subfolder="latent_upsampler", torch_dtype=torch.bfloat16, token=token or None
                        ).to("cuda")
                        self.up = LTX2LatentUpsamplePipeline(vae=self.pipe.vae, latent_upsampler=_m)
                    _up = self.up(latents=_vl, output_type="latent", return_dict=False)[0]
                    _img2 = fit_image(start_img, _h * 2, _w * 2) if start_img is not None else None
                    _v, _a = _run(_img2, sigmas=STAGE_2_DISTILLED_SIGMA_VALUES, latents=_up, audio_latents=_al,
                                  noise_scale=STAGE_2_DISTILLED_SIGMA_VALUES[0], generator=_g, output_type="np",
                                  callback_on_step_end=self._cb("ویدیو — مرحله‌ی ۲ از ۲", _n2))
                    return _to_frames(_v), _to_audio(_a), _sr, _notes
                except Exception as _e:
                    if "out of memory" in str(_e).lower():
                        raise
                    _notes.append(f"روش دومرحله‌ای انجام نشد ({type(_e).__name__})؛ با روش تک‌مرحله‌ای ساخته شد.")
                    gc.collect()
                    torch.cuda.empty_cache()

            _h, _w = SINGLE[aspect]
            _img = fit_image(start_img, _h, _w) if start_img is not None else None
            _g = torch.Generator("cuda").manual_seed(seed)
            if _distilled:
                _kw = dict(sigmas=DISTILLED_SIGMA_VALUES)
                _tot = len(DISTILLED_SIGMA_VALUES)
            else:
                _kw = dict(num_inference_steps=30)
                _tot = 30
            _v, _a = _run(_img, height=_h, width=_w, generator=_g, output_type="np",
                          callback_on_step_end=self._cb("ساخت ویدیو", _tot), **_kw)
            return _to_frames(_v), _to_audio(_a), _sr, _notes

    engine = Engine()
    return best_end_frame, encode_mp4, engine, ffmpeg_exe, fit_image, torch


@app.cell(hide_code=True)
def _(mo, re):
    # استایل‌ها inline هستند تا داخل تب‌ها هم اعمال شوند
    _F = "font-family:Vazirmatn,Tahoma,sans-serif;"
    STY = {
        "yar-root": "direction:rtl;" + _F,
        "yar-card": "border:1px solid #e4e0f5;border-radius:14px;padding:14px 16px;background:#fcfbff;" + _F,
        "yar-sec": "font-weight:700;color:#3b2a8c;font-size:16px;margin:2px 0 6px;",
        "yar-muted": "color:#77738c;font-size:13px;line-height:1.8;",
        "yar-badge": "display:inline-block;background:#ede8ff;color:#3b2a8c;border-radius:8px;padding:1px 9px;font-size:12px;margin:0 4px;",
        "yar-ltr": "direction:ltr;text-align:left;",
        "yar-head": "background:linear-gradient(120deg,#2b1d5e,#5b3fd1 60%,#8b6cf0);color:#fff;border-radius:16px;padding:18px 24px;margin-bottom:6px;",
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
    return H, sty


@app.cell(hide_code=True)
def _(H, mo, read_env_token, torch):
    _env_token = read_env_token()
    _gpu = (f"✅ {torch.cuda.get_device_name(0)} — {torch.cuda.get_device_properties(0).total_memory / 1e9:.0f} GB"
            if torch.cuda.is_available() else "⚠️ GPU روشن نیست — از دکمه‌ی مشخصات بالای molab، RTX Pro 6000 را انتخاب کنید")
    _tok = "🔑 توکن از فایل .env خوانده شد" if _env_token else "🔑 توکن Hugging Face را در تب «💾 پروژه و راهنما» تنظیم کنید"
    H(f"""<div class="yar-root"><div class="yar-head">
      <h1 style="margin:0;font-size:26px;color:#fff">🎬 استودیو ویدیو LTX 2.5</h1>
      <div style="opacity:.85;font-size:14px;margin-top:4px">تصویرسازی • کاراکتر با چهره‌ی ثابت • شات‌های پیوسته با صدا</div>
      <span class="yar-pill">{_gpu}</span><span class="yar-pill">{_tok}</span>
    </div></div>""")
    return


@app.cell(hide_code=True)
def _(ASPECTS, PROJECT, QUALITIES, STYLES, mo, read_env_token):
    _d = PROJECT["drafts"]

    def _pick(key, options, default):
        _v = _d.get(key)
        return _v if _v in options else default

    style_dd = mo.ui.dropdown(options=list(STYLES), value=_pick("style", STYLES, "🎬 فیلم سینمایی"), label="سبک")
    aspect_dd = mo.ui.dropdown(options=ASPECTS, value=_pick("aspect", ASPECTS, "16:9 افقی"), label="نسبت تصویر")
    quality_dd = mo.ui.dropdown(options=QUALITIES, value=_pick("quality", QUALITIES, "720p (1280×720)"), label="کیفیت")
    seed_in = mo.ui.number(start=-1, stop=2**31 - 1, value=int(_d.get("seed", -1)), label="Seed (‎-1 = تصادفی)")
    hf_token = mo.ui.text(kind="password", value=read_env_token(), label="توکن Hugging Face", full_width=True)
    return aspect_dd, hf_token, quality_dd, seed_in, style_dd


@app.cell(hide_code=True)
def _(mo):
    ticker = mo.ui.refresh(options=["2s", "5s"], default_interval="2s", label="به‌روزرسانی خودکار")
    SEEN = {"v": 0}
    return SEEN, ticker


@app.cell(hide_code=True)
def _(H, JOB, SEEN, aspect_dd, bump, mo, quality_dd, seed_in, style_dd, ticker, time):
    ticker
    if JOB["version"] != SEEN["v"]:
        SEEN["v"] = JOB["version"]
        bump()

    if JOB["running"]:
        _el = int(time.time() - JOB["start"])
        _pct = int(100 * JOB["step"] / JOB["total"]) if JOB["total"] else 3
        _steps = f" — مرحله {JOB['step']} از {JOB['total']}" if JOB["total"] else ""
        _status = H(f"""<div class="yar-root"><div class="yar-card">
          <div class="yar-sec">⏳ {JOB['title']}</div>
          <div>{JOB['detail']}{_steps} — زمان: {_el // 60:02d}:{_el % 60:02d}</div>
          <div style="height:10px;background:#ece8fb;border-radius:99px;overflow:hidden;margin:8px 0"><div style="height:100%;width:{_pct}%;background:linear-gradient(90deg,#6c4fd8,#a48bff)"></div></div>
          <div class="yar-muted">کار در پس‌زمینه ادامه دارد؛ اگر صفحه را رفرش کنید یا ببندید چیزی پاک نمی‌شود.</div>
        </div></div>""")
    elif JOB.get("error"):
        _status = mo.callout(mo.vstack([
            mo.md(f"**❌ خطا در «{JOB['title']}»:** {JOB['error']}"),
            mo.accordion({"جزئیات فنی (برای فرستادن به پشتیبانی)": mo.md(f"```\n{JOB.get('trace', '')}\n```")}),
        ]), kind="danger")
    elif JOB.get("message"):
        _status = mo.callout(mo.md(JOB["message"]), kind="success")
    else:
        _status = mo.md("")
    mo.vstack([
        H('<div class="yar-root">' + mo.hstack([style_dd, aspect_dd, quality_dd, seed_in, ticker],
                                                      justify="start", gap=1.2, wrap=True).text + "</div>"),
        _status,
    ])
    return


@app.cell(hide_code=True)
def _(random, seed_in):
    def pick_seed():
        return random.randint(0, 2**31 - 1) if seed_in.value is None or seed_in.value < 0 else int(seed_in.value)
    return (pick_seed,)


# ═══════════════════════ فرم‌ها (مقدارها خودکار ذخیره می‌شوند) ═══════════════════════
@app.cell(hide_code=True)
def _(CAMERA, DURATIONS, IMAGE_MODELS, LANGS, PROJECT, SPEECH, mo):
    _d = PROJECT["drafts"]

    def _v(key, default=""):
        return _d.get(key, default)

    def _o(key, options, default):
        _x = _d.get(key)
        return _x if _x in options else default

    # تصویرسازی
    img_prompt = mo.ui.text_area(label="پرامپت تصویر (انگلیسی)", value=_v("img_prompt"), rows=6, full_width=True,
                                 placeholder="Wide establishing shot of ...")
    img_model = mo.ui.dropdown(options=list(IMAGE_MODELS), value=_o("img_model", IMAGE_MODELS, "Z-Image Turbo (سریع)"),
                               label="مدل")
    img_count = mo.ui.slider(1, 4, value=int(_v("img_count", 2)), label="تعداد", show_value=True)
    img_name = mo.ui.text(label="نام تصویر", value=_v("img_name"), placeholder="مثلاً: خانه")
    img_use_style = mo.ui.checkbox(value=bool(_v("img_use_style", True)), label="سبک بالای صفحه اضافه شود")
    img_btn = mo.ui.run_button(label="🎨 ساخت تصویر", kind="success")
    img_upload = mo.ui.file(filetypes=[".png", ".jpg", ".jpeg", ".webp"], multiple=True, kind="area",
                            label="آپلود تصویر آماده")
    img_upload_btn = mo.ui.run_button(label="⬆️ افزودن به گالری")

    # صحنه با کاراکترها (حفظ چهره)
    comp_prompt = mo.ui.text_area(label="صحنه را توصیف کنید (انگلیسی): کجا هستند، چه می‌کنند، نور و حال‌وهوا",
                                  value=_v("comp_prompt"), rows=5, full_width=True,
                                  placeholder="Inside a small mud-brick house at night, oil lamp light. Zahra kneels on the left packing a bag, Laila stands on the right watching her.")
    comp_name = mo.ui.text(label="نام تصویر", value=_v("comp_name"), placeholder="مثلاً: خانه با زهرا و لیلا")
    comp_count = mo.ui.slider(1, 3, value=int(_v("comp_count", 2)), label="تعداد", show_value=True)
    comp_btn = mo.ui.run_button(label="🧩 ساخت صحنه با چهره‌ی ثابت", kind="success")

    # کاراکترها
    char_name = mo.ui.text(label="نام (انگلیسی)", placeholder="Zahra")
    char_upload = mo.ui.file(filetypes=[".png", ".jpg", ".jpeg", ".webp"], kind="area", label="عکس کاراکتر")
    char_look = mo.ui.text_area(label="ظاهر (Character DNA — انگلیسی)", rows=4, full_width=True,
                                placeholder="a 35-year-old woman with an oval face, ...")
    char_voice = mo.ui.text_area(label="تُن صدا (انگلیسی)", rows=2, full_width=True,
                                 placeholder="soft, low female voice with an Afghan Dari accent")
    char_style = mo.ui.dropdown(options=list(SPEECH), value="معمولی", label="حالت پیش‌فرض صحبت")
    char_add = mo.ui.run_button(label="💾 ذخیره‌ی کاراکتر", kind="success")

    # استودیو
    story = mo.ui.text_area(label="دنیای داستان (ثابت برای همه‌ی شات‌ها — انگلیسی)", value=_v("story"), rows=3,
                            full_width=True)
    scene = mo.ui.text_area(label="اتفاق این شات (انگلیسی)", value=_v("scene"), rows=4, full_width=True)
    dialogue = mo.ui.text_area(label="دیالوگ (خالی = بدون حرف)", value=_v("dialogue"), rows=2, full_width=True)
    dlg_lang = mo.ui.dropdown(options=list(LANGS), value=_o("dlg_lang", LANGS, "انگلیسی (بهترین نتیجه)"),
                              label="زبان دیالوگ")
    speech_dd = mo.ui.dropdown(options=["پیش‌فرض کاراکتر"] + list(SPEECH),
                               value=_o("speech", ["پیش‌فرض کاراکتر"] + list(SPEECH), "پیش‌فرض کاراکتر"),
                               label="حالت صحبت")
    camera_dd = mo.ui.dropdown(options=list(CAMERA), value=_o("camera", CAMERA, "ثابت"), label="دوربین")
    dur_dd = mo.ui.dropdown(options=list(DURATIONS), value=_o("duration", DURATIONS, "۵ ثانیه"), label="مدت")
    sfx = mo.ui.text(label="صدای محیط / موسیقی (انگلیسی)", value=_v("sfx"), full_width=True)
    manual = mo.ui.text_area(label="پرامپت دستی (اختیاری — جای پرامپت خودکار)", value=_v("manual"), rows=3,
                             full_width=True)
    face_lock = mo.ui.checkbox(value=bool(_v("face_lock", True)),
                               label="🔒 قفل چهره: قبل از ساخت، چهره‌ها در فریم شروع با عکس کاراکترها یکی شوند")
    gen_btn = mo.ui.run_button(label="🎬 ساخت شات بعدی", kind="success")
    undo_btn = mo.ui.run_button(label="↩️ حذف آخرین شات", kind="warn")
    merge_btn = mo.ui.run_button(label="🎞 ساخت فیلم نهایی")

    # پروژه
    backup_btn = mo.ui.run_button(label="📦 ساخت فایل پشتیبان پروژه")
    restore_file = mo.ui.file(filetypes=[".zip"], kind="area", label="فایل پشتیبان (zip)", max_size=1_500_000_000)
    restore_btn = mo.ui.run_button(label="♻️ بازگردانی پروژه", kind="warn")
    return (
        backup_btn, camera_dd, char_add, char_look, char_name, char_style, char_upload, char_voice,
        comp_btn, comp_count, comp_name, comp_prompt, dialogue, dlg_lang, dur_dd, face_lock, gen_btn,
        img_btn, img_count, img_model, img_name, img_prompt, img_upload, img_upload_btn, img_use_style,
        manual, merge_btn, restore_btn, restore_file, scene, sfx, speech_dd, story, undo_btn,
    )


@app.cell(hide_code=True)
def _(PROJECT, get_rev, mo):
    get_rev()
    _d = PROJECT["drafts"]
    _imgs = PROJECT["images"]
    _chars = PROJECT["chars"]
    _names = list(_chars)

    # فریم شروع
    _opts = {}
    if PROJECT["shots"]:
        _opts["▶ ادامه از آخرین فریم شات قبلی"] = "continue"
    for _i, _im in enumerate(_imgs):
        _opts[f"🖼 {_i + 1}. {_im['label']}"] = "img:" + _im["path"]
    for _n, _c in _chars.items():
        _opts[f"👤 {_n} (عکس کاراکتر)"] = "img:" + _c["image"]
    _opts["⛔ بدون تصویر (فقط متن)"] = "none"
    _prev = _d.get("start_label")
    if PROJECT["shots"] and _d.get("last_shot_count", -1) != len(PROJECT["shots"]):
        _prev = "▶ ادامه از آخرین فریم شات قبلی"
    start_dd = mo.ui.dropdown(options=_opts, value=_prev if _prev in _opts else list(_opts)[0], label="فریم شروع")

    _sp = _d.get("speaker")
    speaker_dd = mo.ui.dropdown(options=["— هیچ‌کس —"] + _names,
                                value=_sp if _sp in _names else "— هیچ‌کس —", label="گوینده")
    others_ms = mo.ui.multiselect(options=_names, value=[n for n in _d.get("others", []) if n in _names],
                                  label="کاراکترهای دیگر در صحنه")
    comp_chars = mo.ui.multiselect(options=_names, value=[n for n in _d.get("comp_chars", []) if n in _names][:3],
                                   max_selections=3, label="کاراکترها (حداکثر ۳)")
    _bg_opts = {"— بدون پس‌زمینه (فقط از روی متن) —": ""} | {f"{i + 1}. {im['label']}": im["path"]
                                                            for i, im in enumerate(_imgs)}
    comp_bg = mo.ui.dropdown(options=_bg_opts, value=list(_bg_opts)[0], label="پس‌زمینه از گالری (اختیاری)")
    char_from_gallery = mo.ui.dropdown(
        options={"— آپلود عکس —": ""} | {f"{i + 1}. {im['label']}": im["path"] for i, im in enumerate(_imgs)},
        value="— آپلود عکس —", label="یا عکس از گالری")
    char_del_dd = mo.ui.dropdown(options=_names or ["—"], label="کاراکتر")
    char_del_btn = mo.ui.run_button(label="🗑 حذف کاراکتر")
    img_del_dd = mo.ui.dropdown(options={f"{i + 1}. {im['label']}": i for i, im in enumerate(_imgs)} or {"—": -1},
                                label="تصویر")
    img_del_btn = mo.ui.run_button(label="🗑 حذف از گالری")
    return (
        char_del_btn, char_del_dd, char_from_gallery, comp_bg, comp_chars, img_del_btn, img_del_dd,
        others_ms, speaker_dd, start_dd,
    )


@app.cell(hide_code=True)
def _(
    LOCK, PROJECT, aspect_dd, camera_dd, comp_chars, comp_count, comp_name, comp_prompt, dialogue,
    dlg_lang, dur_dd, face_lock, img_count, img_model, img_name, img_prompt, img_use_style, manual,
    others_ms, quality_dd, save_project, scene, seed_in, sfx, speaker_dd, speech_dd, start_dd, story,
    style_dd,
):
    # ذخیره‌ی خودکار همه‌ی فیلدها (بعد از رفرش برمی‌گردند)
    with LOCK:
        PROJECT["drafts"].update(
            style=style_dd.value, aspect=aspect_dd.value, quality=quality_dd.value, seed=seed_in.value,
            img_prompt=img_prompt.value, img_model=img_model.value, img_count=img_count.value,
            img_name=img_name.value, img_use_style=img_use_style.value,
            comp_prompt=comp_prompt.value, comp_name=comp_name.value, comp_count=comp_count.value,
            comp_chars=list(comp_chars.value),
            story=story.value, scene=scene.value, dialogue=dialogue.value, dlg_lang=dlg_lang.value,
            speech=speech_dd.value, camera=camera_dd.value, duration=dur_dd.value, sfx=sfx.value,
            manual=manual.value, face_lock=face_lock.value, start_label=start_dd.selected_key,
            speaker=speaker_dd.value, others=list(others_ms.value),
            last_shot_count=len(PROJECT["shots"]),
        )
    save_project()
    return


@app.cell(hide_code=True)
def _(
    CAMERA, LANGS, PROJECT, SPEECH, STYLES, camera_dd, dialogue, dlg_lang, manual, others_ms, scene,
    sfx, speaker_dd, speech_dd, start_dd, story, style_dd,
):
    def build_prompt():
        if manual.value.strip():
            return manual.value.strip()
        _chars = PROJECT["chars"]
        _parts = [STYLES[style_dd.value] + "."]
        if story.value.strip():
            _parts.append(story.value.strip().rstrip(".") + ".")
        _present = [n for n in [speaker_dd.value, *others_ms.value] if n in _chars]
        _present = list(dict.fromkeys(_present))
        for _n in _present:
            if _chars[_n]["look"]:
                _parts.append(f"{_n} is {_chars[_n]['look'].rstrip('.')}.")
        if start_dd.value == "continue":
            _parts.append("The shot continues seamlessly from the opening frame: same location, same lighting and color grade.")
        if _present:
            _parts.append(f"{' and '.join(_present)} keep exactly the same face, hairstyle and clothing as in the opening frame throughout the whole shot.")
        if scene.value.strip():
            _parts.append(scene.value.strip().rstrip(".") + ".")
        _sp = speaker_dd.value
        _txt = dialogue.value.strip()
        if _txt:
            if _sp in _chars:
                _c = _chars[_sp]
                _mode = _c["style"] if speech_dd.value == "پیش‌فرض کاراکتر" else speech_dd.value
                _voice = f" in a {_c['voice'].rstrip('.')}" if _c["voice"] else ""
                _parts.append(f"{_sp} faces the listener and speaks {SPEECH[_mode]}{_voice}, in "
                              f"{LANGS[dlg_lang.value]}, with clear natural lip movement, saying: \"{_txt}\"")
            else:
                _mode = "معمولی" if speech_dd.value == "پیش‌فرض کاراکتر" else speech_dd.value
                _parts.append(f"A voice says {SPEECH[_mode]} in {LANGS[dlg_lang.value]}: \"{_txt}\"")
        _parts.append(CAMERA[camera_dd.value])
        if sfx.value.strip():
            _parts.append(f"Audio: {sfx.value.strip()}.")
        return " ".join(_parts)
    return (build_prompt,)


# ═══════════════════════ کارها (همه در پس‌زمینه) ═══════════════════════
@app.cell(hide_code=True)
def _(
    IMAGE_MODELS, IMG_SIZE, JOB, LOCK, OUT, PROJECT, STYLES, aspect_dd, engine, hf_token,
    img_btn, img_count, img_model, img_name, img_prompt, img_use_style, mo, pick_seed, rel,
    save_project, start_job, style_dd, time,
):
    mo.stop(not img_btn.value)
    if not img_prompt.value.strip():
        JOB.update(error=None, message="⚠️ پرامپت تصویر خالی است.", title="")
        JOB["version"] += 1  # نمایش در به‌روزرسانی بعدی (بدون چرخه)
    else:
        _mid, _steps, _cfg = IMAGE_MODELS[img_model.value]
        _prompt = img_prompt.value.strip()
        if img_use_style.value:
            _prompt = STYLES[style_dd.value] + ". " + _prompt
        _h, _w = IMG_SIZE[aspect_dd.value]
        _n, _label, _tok = img_count.value, img_name.value.strip() or "تصویر", hf_token.value.strip()
        _seeds = [pick_seed() for _ in range(_n)]

        def _work():
            engine.job = JOB
            for _i, _seed in enumerate(_seeds):
                JOB["title"] = f"ساخت تصویر {_i + 1} از {_n}"
                _im = engine.image(_mid, _steps, _cfg, _prompt, _h, _w, _seed, _tok)
                _p = OUT / "images" / f"img_{int(time.time() * 1000)}.png"
                _im.save(_p)
                with LOCK:
                    PROJECT["images"].append({"path": rel(_p), "label": _label + (f" {_i + 1}" if _n > 1 else ""),
                                              "prompt": _prompt, "seed": _seed})
                save_project()
                JOB["version"] += 1
            return f"✅ {_n} تصویر ساخته شد و در گالری است."

        if not start_job("ساخت تصویر", _work):
            JOB["message"] = "⏳ یک کار دیگر در حال انجام است؛ صبر کنید تا تمام شود."
            JOB["version"] += 1  # نمایش در به‌روزرسانی بعدی (بدون چرخه)
    return


@app.cell(hide_code=True)
def _(
    EDIT_ID, EDIT_SIZE, Image, JOB, LOCK, OUT, PROJECT, STYLES, absp, aspect_dd, comp_bg,
    comp_btn, comp_chars, comp_count, comp_name, comp_prompt, engine, hf_token, mo, pick_seed, rel,
    save_project, start_job, style_dd, time,
):
    mo.stop(not comp_btn.value)
    _names = list(comp_chars.value)
    if not _names or not comp_prompt.value.strip():
        JOB.update(error=None, message="⚠️ حداقل یک کاراکتر انتخاب کنید و صحنه را توصیف کنید.", title="")
        JOB["version"] += 1  # نمایش در به‌روزرسانی بعدی (بدون چرخه)
    else:
        _chars = PROJECT["chars"]
        _refs = [str(absp(_chars[n]["image"])) for n in _names]
        _bg = str(absp(comp_bg.value)) if comp_bg.value else None
        _lines = []
        for _i, _n in enumerate(_names):
            _lines.append(f"Image {_i + 1} is a reference photo of {_n}"
                          + (f" ({_chars[_n]['look'].rstrip('.')})" if _chars[_n]["look"] else "") + ".")
        if _bg:
            _lines.append(f"Image {len(_names) + 1} is the background location; keep this place, its layout and lighting.")
        _prompt = (
            f"{STYLES[style_dd.value]}. " + " ".join(_lines) + " "
            + f"Create one new film frame: {comp_prompt.value.strip().rstrip('.')}. "
            + f"The faces of {', '.join(_names)} must be exactly identical to their reference photos: same facial "
              "structure, eyes, nose, mouth, skin tone, age, hairstyle and clothing. Faces clearly visible and well lit, "
              "mouths closed, natural relaxed poses ready to move, eye-level camera, sharp focus, no text, no watermark."
        )
        _h, _w = EDIT_SIZE[aspect_dd.value]
        _n_img, _label, _tok = comp_count.value, comp_name.value.strip() or "صحنه", hf_token.value.strip()
        _seeds = [pick_seed() for _ in range(_n_img)]

        def _work():
            engine.job = JOB
            _imgs = [Image.open(p) for p in _refs] + ([Image.open(_bg)] if _bg else [])
            for _i, _seed in enumerate(_seeds):
                JOB["title"] = f"صحنه با چهره‌ی ثابت {_i + 1} از {_n_img}"
                _im = engine.edit(_imgs, _prompt, _h, _w, _seed, _tok)
                _p = OUT / "images" / f"scene_{int(time.time() * 1000)}.png"
                _im.save(_p)
                with LOCK:
                    PROJECT["images"].append({"path": rel(_p), "label": _label + (f" {_i + 1}" if _n_img > 1 else ""),
                                              "prompt": _prompt, "seed": _seed, "chars": _names})
                save_project()
                JOB["version"] += 1
            return f"✅ {_n_img} صحنه با چهره‌های ثابت ساخته شد."

        if not start_job("ساخت صحنه با کاراکترها", _work):
            JOB["message"] = "⏳ یک کار دیگر در حال انجام است."
            JOB["version"] += 1  # نمایش در به‌روزرسانی بعدی (بدون چرخه)
    return


@app.cell(hide_code=True)
def _(JOB, LOCK, OUT, PROJECT, img_upload, img_upload_btn, mo, rel, re, save_project, time):
    mo.stop(not img_upload_btn.value)
    _n = 0
    for _i in range(len(img_upload.value)):
        _safe = re.sub(r"[^\w.\-]+", "_", img_upload.name(_i))
        _p = OUT / "images" / f"up_{int(time.time() * 1000)}_{_i}_{_safe}"
        _p.write_bytes(img_upload.contents(_i))
        with LOCK:
            PROJECT["images"].append({"path": rel(_p), "label": img_upload.name(_i).rsplit(".", 1)[0],
                                      "prompt": "", "seed": None})
        _n += 1
    save_project()
    JOB.update(error=None, title="", message=f"✅ {_n} تصویر اضافه شد." if _n else "⚠️ اول فایلی انتخاب کنید.")
    JOB["version"] += 1  # نمایش در به‌روزرسانی بعدی (بدون چرخه)
    return


@app.cell(hide_code=True)
def _(JOB, LOCK, PROJECT, img_del_btn, img_del_dd, mo, save_project):
    mo.stop(not img_del_btn.value)
    if isinstance(img_del_dd.value, int) and 0 <= img_del_dd.value < len(PROJECT["images"]):
        with LOCK:
            _x = PROJECT["images"].pop(img_del_dd.value)
        save_project()
        JOB.update(error=None, title="", message=f"🗑 «{_x['label']}» از گالری حذف شد.")
        JOB["version"] += 1  # نمایش در به‌روزرسانی بعدی (بدون چرخه)
    return


@app.cell(hide_code=True)
def _(
    JOB, LOCK, OUT, PROJECT, absp, char_add, char_from_gallery, char_look, char_name,
    char_style, char_upload, char_voice, mo, rel, re, save_project, shutil, time,
):
    mo.stop(not char_add.value)
    _name = re.sub(r"\s+", " ", char_name.value.strip())
    if not _name:
        JOB.update(error=None, title="", message="⚠️ نام کاراکتر را بنویسید.")
    elif not char_upload.value and not char_from_gallery.value:
        JOB.update(error=None, title="", message="⚠️ یک عکس برای کاراکتر انتخاب کنید.")
    else:
        _dst = OUT / "characters" / f"{int(time.time())}_{re.sub(r'[^\w]+', '_', _name)}.png"
        if char_upload.value:
            _dst.write_bytes(char_upload.contents(0))
        else:
            shutil.copy(absp(char_from_gallery.value), _dst)
        with LOCK:
            PROJECT["chars"][_name] = {"image": rel(_dst), "look": char_look.value.strip(),
                                       "voice": char_voice.value.strip(), "style": char_style.value}
        save_project()
        JOB.update(error=None, title="", message=f"✅ کاراکتر «{_name}» ذخیره شد.")
    JOB["version"] += 1  # نمایش در به‌روزرسانی بعدی (بدون چرخه)
    return


@app.cell(hide_code=True)
def _(JOB, LOCK, PROJECT, char_del_btn, char_del_dd, mo, save_project):
    mo.stop(not char_del_btn.value)
    with LOCK:
        _ok = PROJECT["chars"].pop(char_del_dd.value, None)
    if _ok:
        save_project()
        JOB.update(error=None, title="", message=f"🗑 کاراکتر «{char_del_dd.value}» حذف شد.")
        JOB["version"] += 1  # نمایش در به‌روزرسانی بعدی (بدون چرخه)
    return


@app.cell(hide_code=True)
def _(
    DURATIONS, EDIT_SIZE, FINAL, Image, JOB, LOCK, OUT, PROJECT, absp, aspect_dd, best_end_frame, build_prompt,
    dur_dd, encode_mp4, engine, face_lock, gen_btn, hf_token, mo, others_ms, pick_seed,
    quality_dd, rel, save_project, speaker_dd, start_dd, start_job, time,
):
    mo.stop(not gen_btn.value)
    _shots = PROJECT["shots"]
    _src = start_dd.value
    _continued = _src == "continue"
    if _continued and not _shots:
        JOB.update(error=None, title="", message="⚠️ شات قبلی وجود ندارد؛ یک تصویر شروع انتخاب کنید.")
        JOB["version"] += 1  # نمایش در به‌روزرسانی بعدی (بدون چرخه)
    else:
        _start_path = (str(absp(_shots[-1]["last_frame"])) if _continued
                       else str(absp(_src[4:])) if _src.startswith("img:") else None)
        _prompt = build_prompt()
        _nf, _dur = DURATIONS[dur_dd.value], dur_dd.value
        _q, _asp, _seed, _tok = quality_dd.value, aspect_dd.value, pick_seed(), hf_token.value.strip()
        _chars = PROJECT["chars"]
        _present = [n for n in dict.fromkeys([speaker_dd.value, *others_ms.value]) if n in _chars][:3]
        _lock = face_lock.value and bool(_present) and _start_path is not None
        _refs = [(n, str(absp(_chars[n]["image"])), _chars[n]["look"]) for n in _present]
        _num = len(_shots) + 1

        def _work():
            engine.job = JOB
            _img = Image.open(_start_path).convert("RGB") if _start_path else None
            _locked_path = None
            if _lock:
                JOB["title"] = f"شات {_num}: قفل چهره"
                _desc = " ".join(f"Image {i + 2} is a reference photo of {n}"
                                 + (f" ({look.rstrip('.')})" if look else "") + "."
                                 for i, (n, _, look) in enumerate(_refs))
                _names = ", ".join(n for n, _, _ in _refs)
                _edit_prompt = (
                    f"Image 1 is a frame from a film. {_desc} Edit image 1 only: make the faces of {_names} exactly "
                    "identical to their reference photos (same facial structure, eyes, nose, mouth, skin tone, age and "
                    "hair). Keep everything else in image 1 exactly unchanged: same composition, framing, body poses, "
                    "head angles, expressions, clothing, background, lighting and colors."
                )
                _w0, _h0 = _img.size
                _s = (1_300_000 / (_w0 * _h0)) ** 0.5
                _eh, _ew = max(512, int(_h0 * _s) // 16 * 16), max(512, int(_w0 * _s) // 16 * 16)
                _img = engine.edit([_img] + [Image.open(p) for _, p, _ in _refs], _edit_prompt, _eh, _ew, _seed, _tok)
                _locked_path = OUT / "frames" / f"shot_{_num:03d}_{int(time.time())}_start_locked.png"
                _img.save(_locked_path)
            JOB["title"] = f"ساخت شات {_num} ({_dur})"
            _frames, _audio, _sr, _notes = engine.video(_img, _prompt, _nf, _q, _asp, _seed, _tok)
            engine.clean()
            JOB["detail"] = "ذخیره‌ی ویدیو…"
            _k = best_end_frame(_frames)
            _stamp = int(time.time())
            _lf = OUT / "frames" / f"shot_{_num:03d}_{_stamp}_last.png"
            Image.fromarray(_frames[_k]).save(_lf)
            _vp = OUT / "shots" / f"shot_{_num:03d}_{_stamp}.mp4"
            encode_mp4(_frames, _audio, _sr, _vp, FINAL[_q][_asp])
            with LOCK:
                PROJECT["shots"].append({
                    "video": rel(_vp), "last_frame": rel(_lf), "prompt": _prompt, "seed": _seed,
                    "continued": _continued, "duration": _dur, "quality": _q, "aspect": _asp,
                    "frames": int(len(_frames)), "end_frame": int(_k),
                    "locked_start": rel(_locked_path) if _locked_path else None,
                })
                PROJECT["final"] = None
            save_project()
            _extra = ("\n\n" + "\n".join(_notes)) if _notes else ""
            return f"✅ شات {_num} ساخته شد. برای ادامه‌ی داستان «ادامه از آخرین فریم» انتخاب شده است.{_extra}"

        if not start_job(f"ساخت شات {_num}", _work):
            JOB["message"] = "⏳ یک کار دیگر در حال انجام است."
            JOB["version"] += 1  # نمایش در به‌روزرسانی بعدی (بدون چرخه)
    return


@app.cell(hide_code=True)
def _(JOB, LOCK, PROJECT, mo, save_project, undo_btn):
    mo.stop(not undo_btn.value)
    if JOB["running"]:
        JOB["message"] = "⏳ صبر کنید تا کار فعلی تمام شود."
    elif PROJECT["shots"]:
        with LOCK:
            PROJECT["shots"].pop()
            PROJECT["final"] = None
        save_project()
        JOB.update(error=None, title="", message=f"↩️ شات {len(PROJECT['shots']) + 1} حذف شد. حالا می‌توانید دوباره بسازید.")
    JOB["version"] += 1  # نمایش در به‌روزرسانی بعدی (بدون چرخه)
    return


@app.cell(hide_code=True)
def _(FPS, JOB, LOCK, OUT, PROJECT, absp, ffmpeg_exe, merge_btn, mo, re, rel, save_project, start_job, subprocess, time):
    mo.stop(not merge_btn.value)
    _shots = list(PROJECT["shots"])
    if not _shots:
        JOB.update(error=None, title="", message="⚠️ هنوز شاتی ساخته نشده.")
        JOB["version"] += 1  # نمایش در به‌روزرسانی بعدی (بدون چرخه)
    else:
        def _work():
            JOB["detail"] = "چسباندن شات‌ها…"
            _ff = ffmpeg_exe()
            _probe = subprocess.run([_ff, "-i", str(absp(_shots[0]["video"]))], capture_output=True).stderr.decode(errors="ignore")
            _m = re.search(r"Video:.*?(\d{3,4})x(\d{3,4})", _probe)
            _W, _H = (int(_m.group(1)), int(_m.group(2))) if _m else (1920, 1080)
            _cmd = [_ff, "-y", "-loglevel", "error"]
            for _x in _shots:
                _cmd += ["-i", str(absp(_x["video"]))]
            _f = []
            for _i, _x in enumerate(_shots):
                _start = 1 if (_x.get("continued") and _i > 0) else 0
                # اگر شات بعدی از یک فریم واضح‌تر قبل از انتها ادامه داده، انتهای این شات همان‌جا بریده می‌شود
                _nxt = _shots[_i + 1] if _i + 1 < len(_shots) else None
                _end = _x.get("frames", 0)
                if _nxt and _nxt.get("continued") and _x.get("end_frame") is not None:
                    _end = _x["end_frame"] + 1
                _trim = f"trim=start_frame={_start}" + (f":end_frame={_end}" if _end else "")
                _f.append(f"[{_i}:v]{_trim},setpts=PTS-STARTPTS,scale={_W}:{_H}:force_original_aspect_ratio=increase,"
                          f"crop={_W}:{_H},setsar=1,fps={FPS}[v{_i}]")
                _atrim = f"atrim=start={_start / FPS:.5f}" + (f":end={_end / FPS:.5f}" if _end else "")
                _f.append(f"[{_i}:a]{_atrim},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo[a{_i}]")
            _f.append("".join(f"[v{_i}][a{_i}]" for _i in range(len(_shots))) + f"concat=n={len(_shots)}:v=1:a=1[v][a]")
            _out = OUT / "final" / f"movie_{int(time.time())}.mp4"
            _cmd += ["-filter_complex", ";".join(_f), "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "17",
                     "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                     "-movflags", "+faststart", str(_out)]
            _r = subprocess.run(_cmd, capture_output=True)
            if _r.returncode != 0:
                raise RuntimeError(_r.stderr.decode(errors="ignore")[-1500:])
            with LOCK:
                PROJECT["final"] = rel(_out)
            save_project()
            return f"✅ فیلم نهایی آماده شد ({len(_shots)} شات). در تب استودیو پایین تایم‌لاین است."

        if not start_job("ساخت فیلم نهایی", _work):
            JOB["message"] = "⏳ یک کار دیگر در حال انجام است."
            JOB["version"] += 1  # نمایش در به‌روزرسانی بعدی (بدون چرخه)
    return


@app.cell(hide_code=True)
def _(JOB, LOCK, OUT, PROJECT, backup_btn, mo, rel, save_project, start_job, time, zipfile):
    mo.stop(not backup_btn.value)

    def _work():
        JOB["detail"] = "فشرده‌سازی فایل‌ها…"
        save_project()
        _z = OUT / "backups" / f"ltx_project_{time.strftime('%Y%m%d_%H%M')}.zip"
        with zipfile.ZipFile(_z, "w", zipfile.ZIP_STORED) as _zf:
            for _p in OUT.rglob("*"):
                if _p.is_file() and "backups" not in _p.parts and not _p.name.endswith(".wav"):
                    _zf.write(_p, _p.relative_to(OUT))
        with LOCK:
            PROJECT["backup"] = rel(_z)
        save_project()
        return "✅ فایل پشتیبان آماده است؛ در تب «💾 پروژه و راهنما» دانلودش کنید."

    if not start_job("ساخت فایل پشتیبان", _work):
        JOB["message"] = "⏳ یک کار دیگر در حال انجام است."
    JOB["version"] += 1  # نمایش در به‌روزرسانی بعدی (بدون چرخه)
    return


@app.cell(hide_code=True)
def _(JOB, LOCK, OUT, PROJECT, json, mo, restore_btn, restore_file, save_project, zipfile):
    mo.stop(not restore_btn.value)
    import io as _io
    if not restore_file.value:
        JOB.update(error=None, title="", message="⚠️ اول فایل zip پشتیبان را انتخاب کنید.")
    else:
        try:
            with zipfile.ZipFile(_io.BytesIO(restore_file.contents(0))) as _zf:
                for _m in _zf.namelist():
                    _t = (OUT / _m).resolve()
                    if OUT not in _t.parents and _t != OUT:
                        continue
                    _t.parent.mkdir(parents=True, exist_ok=True)
                    _t.write_bytes(_zf.read(_m))
            _new = json.loads((OUT / "project.json").read_text(encoding="utf-8"))
            with LOCK:
                for _k in ("images", "chars", "shots", "final", "drafts"):
                    if _k in _new:
                        PROJECT[_k] = _new[_k]
            save_project()
            JOB.update(error=None, title="", message="✅ پروژه بازگردانی شد. برای برگشتن متن فرم‌ها، نوت‌بوک را یک بار Run all کنید.")
        except Exception as _e:
            JOB.update(error=f"بازگردانی ناموفق: {_e}", title="بازگردانی پروژه", trace="")
    JOB["version"] += 1  # نمایش در به‌روزرسانی بعدی (بدون چرخه)
    return


# ═══════════════════════ نمایش ═══════════════════════
@app.cell(hide_code=True)
def _(H, PROJECT, absp, get_rev, mo):
    get_rev()

    def _card(inner):
        return H(f'<div class="yar-root"><div class="yar-card">{inner}</div></div>')

    # گالری
    _imgs = PROJECT["images"]
    gallery_view = mo.hstack(
        [mo.vstack([mo.image(src=str(absp(_im["path"])), width=230, rounded=True),
                    H(f'<div class="yar-root"><b>{_i + 1}.</b> {_im["label"]}'
                            + (' <span class="yar-badge">🧩 چهره‌ی ثابت</span>' if _im.get("chars") else "")
                            + "</div>")], gap=0.3)
         for _i, _im in enumerate(_imgs)], wrap=True, justify="start", gap=1,
    ) if _imgs else H('<div class="yar-root yar-muted">هنوز تصویری نیست.</div>')

    # کاراکترها
    _chars = PROJECT["chars"]
    chars_view = mo.hstack([
        mo.vstack([
            mo.image(src=str(absp(_c["image"])), width=190, rounded=True),
            H(f'<div class="yar-root"><b>{_n}</b> <span class="yar-badge">🗣 {_c["style"]}</span>'
                    f'<div class="yar-muted yar-ltr" style="max-width:190px">{_c["voice"] or ""}</div></div>'),
        ], gap=0.3) for _n, _c in _chars.items()
    ], wrap=True, justify="start", gap=1) if _chars else H('<div class="yar-root yar-muted">هنوز کاراکتری نیست.</div>')

    # تایم‌لاین
    def _video(path, label, play=True):
        _p = absp(path)
        _dl = mo.download(data=lambda _p=_p: _p.read_bytes(), filename=_p.name, mimetype="video/mp4", label=label)
        if not play:
            return _dl
        return mo.vstack([mo.video(src=str(_p), controls=True, width="100%"), _dl], gap=0.3)

    _shots = PROJECT["shots"]
    _items = []
    for _i, _x in enumerate(_shots):
        _tags = f'<span class="yar-badge">{_x["duration"]}</span><span class="yar-badge">{_x["quality"].split()[0]}</span>'
        if _x.get("continued"):
            _tags += '<span class="yar-badge">🔗 ادامه‌ی شات قبل</span>'
        if _x.get("locked_start"):
            _tags += '<span class="yar-badge">🔒 چهره قفل</span>'
        _items.append(mo.vstack([
            H(f'<div class="yar-root"><b>شات {_i + 1}</b> {_tags}</div>'),
            _video(_x["video"], "⬇️ دانلود شات", play=_i >= len(_shots) - 2),
            mo.accordion({"پرامپت این شات": mo.md(f"```text\n{_x['prompt']}\n```")}),
        ], gap=0.4))
    if len(_shots) > 2:
        _items.insert(0, H('<div class="yar-root yar-muted">برای سبک ماندن صفحه فقط ۲ شات آخر پخش می‌شوند؛ '
                           'شات‌های قبلی را با دکمه‌ی دانلود بگیرید. فیلم نهایی همه را با هم دارد.</div>'))
    timeline_view = mo.vstack(_items, gap=1.2) if _items else H(
        '<div class="yar-root yar-muted">هنوز شاتی ساخته نشده. فریم شروع را انتخاب کنید و «ساخت شات بعدی» را بزنید.</div>')
    final_view = (mo.vstack([H('<div class="yar-root yar-sec">🏁 فیلم نهایی</div>'),
                             _video(PROJECT["final"], "⬇️ دانلود فیلم نهایی")])
                  if PROJECT.get("final") else mo.md(""))
    if PROJECT.get("backup"):
        _bp = absp(PROJECT["backup"])
        backup_view = mo.download(data=lambda: _bp.read_bytes(), filename=_bp.name, mimetype="application/zip",
                                  label=f"⬇️ دانلود {_bp.name} ({_bp.stat().st_size / 1e6:.0f} MB)")
    else:
        backup_view = mo.md("")
    return backup_view, chars_view, final_view, gallery_view, timeline_view


@app.cell(hide_code=True)
def _(H, 
    backup_btn, backup_view, build_prompt, camera_dd, char_add, char_del_btn, char_del_dd,
    char_from_gallery, char_look, char_name, char_style, char_upload, char_voice, chars_view,
    comp_bg, comp_btn, comp_chars, comp_count, comp_name, comp_prompt, dialogue, dlg_lang, dur_dd,
    face_lock, final_view, gallery_view, gen_btn, hf_token, img_btn, img_count, img_del_btn,
    img_del_dd, img_model, img_name, img_prompt, img_upload, img_upload_btn, img_use_style, manual,
    merge_btn, mo, others_ms, restore_btn, restore_file, scene, sfx, speaker_dd, speech_dd, start_dd,
    story, timeline_view, undo_btn,
):
    def R(x):
        return H('<div class="yar-root">' + (x.text if hasattr(x, "text") else str(x)) + "</div>")

    def sec(title, note=""):
        return H(f'<div class="yar-root"><div class="yar-sec">{title}</div>'
                       + (f'<div class="yar-muted">{note}</div>' if note else "") + "</div>")

    def card(*items):
        return H('<div class="yar-root"><div class="yar-card">'
                       + mo.vstack(list(items), gap=0.7).text + "</div></div>")

    # ── استودیو
    _form = card(
        sec("🎬 شات بعدی"),
        R(story), R(start_dd),
        R(mo.hstack([dur_dd, camera_dd], justify="start", gap=1, wrap=True)),
        R(scene),
        R(mo.hstack([speaker_dd, others_ms], justify="start", gap=1, wrap=True)),
        R(dialogue),
        R(mo.hstack([speech_dd, dlg_lang], justify="start", gap=1, wrap=True)),
        R(sfx), R(face_lock),
        H('<div class="yar-root yar-muted">قفل چهره با عکس کاراکترهای «گوینده» و «کاراکترهای دیگر» انجام '
                'می‌شود (حدود ۲–۴ دقیقه بیشتر برای هر شات).</div>'),
        mo.accordion({"✏️ پرامپت دستی": R(manual),
                      "👁 پیش‌نمایش پرامپت": mo.md(f"```text\n{build_prompt()}\n```")}),
        R(mo.hstack([gen_btn, undo_btn, merge_btn], justify="start", gap=1, wrap=True)),
    )
    _tab_studio = mo.hstack([
        mo.vstack([card(sec("🎞 تایم‌لاین"), timeline_view), final_view], gap=1),
        _form,
    ], widths=[1.15, 1], gap=1.5, align="start")

    # ── تصویرسازی
    _tab_img = mo.vstack([
        mo.hstack([
            card(sec("🧩 صحنه با چهره‌ی ثابت", "عکس کاراکترها + توصیف صحنه ← فریم شروع با همان چهره‌ها (Qwen Image Edit)"),
                 R(comp_chars), R(comp_bg), R(comp_prompt),
                 R(mo.hstack([comp_count, comp_name], justify="start", gap=1, wrap=True)), R(comp_btn)),
            card(sec("🎨 تصویر از متن", "برای محیط‌ها و عکس پرتره‌ی کاراکترها"),
                 R(img_prompt),
                 R(mo.hstack([img_model, img_count, img_name], justify="start", gap=1, wrap=True)),
                 R(mo.hstack([img_use_style, img_btn], justify="start", gap=1, wrap=True))),
        ], widths=[1, 1], gap=1.5, align="start"),
        card(sec("🖼 گالری"), gallery_view,
             R(mo.hstack([img_upload, img_upload_btn, img_del_dd, img_del_btn], justify="start", gap=1, wrap=True))),
    ], gap=1.2)

    # ── کاراکترها
    _tab_char = mo.hstack([
        mo.vstack([card(sec("👥 کاراکترهای پروژه"), chars_view),
                   card(R(mo.hstack([char_del_dd, char_del_btn], justify="start", gap=1)))], gap=1),
        card(sec("➕ کاراکتر جدید", "بهترین عکس: رو به دوربین، صورت واضح، پس‌زمینه‌ی ساده"),
             R(char_name), R(char_upload), R(char_from_gallery), R(char_look), R(char_voice), R(char_style),
             R(char_add)),
    ], widths=[1.3, 1], gap=1.5, align="start")

    # ── پروژه و راهنما
    _tab_proj = mo.hstack([
        card(sec("💾 پشتیبان پروژه", "molab فایل‌های ساخته‌شده را بعد از خاموش شدن نگه نمی‌دارد. "
                                    "قبل از بستن کار، فایل پشتیبان بسازید و دانلود کنید."),
             R(backup_btn), backup_view, R(restore_file), R(restore_btn)),
        card(sec("🔑 توکن Hugging Face"), R(hf_token),
             H('<div class="yar-root yar-muted">برای اینکه هر بار لازم به پیست نباشد: در نوار کناری molab، پنل '
                     '<b>Files</b> را باز کنید، یک فایل به اسم <code>.env</code> بسازید و داخلش بنویسید: '
                     '<code class="yar-ltr">HF_TOKEN=hf_...</code> — این فایل خصوصی می‌ماند و ذخیره می‌شود.</div>')),
    ], widths=[1, 1], gap=1.5, align="start")

    mo.ui.tabs({"🎬 استودیو": _tab_studio, "🎨 تصویرسازی": _tab_img, "👤 کاراکترها": _tab_char,
                "💾 پروژه و راهنما": _tab_proj})
    return


if __name__ == "__main__":
    app.run()
