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
#  استودیو نبرد سینمایی (LTX 2.5) — برای molab (marimo)
#  1) GPU را از دکمه‌ی مشخصات بالای صفحه روشن کنید   2) Run all

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="full", app_title="Battle Studio")


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
    OUT = Path("battle_studio_output").resolve()
    for _d in ("images", "characters", "shots", "frames", "final", "backups"):
        (OUT / _d).mkdir(parents=True, exist_ok=True)
    PROJECT_FILE = OUT / "project.json"
    LOCK = threading.RLock()

    def _empty():
        return {"images": [], "chars": {}, "shots": [], "final": None, "drafts": {}, "log": "", "backup": None,
                "battle": {"shots": [], "keys": {}, "final": None}}

    def load_project():
        _p = _empty()
        try:
            _p.update(json.loads(PROJECT_FILE.read_text(encoding="utf-8")))
        except Exception:
            pass
        _p["images"] = [i for i in _p["images"] if (OUT / i["path"]).exists()]
        _p["chars"] = {k: v for k, v in _p["chars"].items() if (OUT / v["image"]).exists()}
        _p["shots"] = [s for s in _p["shots"] if (OUT / s["video"]).exists()]
        _b = {"shots": [], "keys": {}, "final": None}
        _b.update(_p.get("battle") or {})
        _b["shots"] = [s for s in _b["shots"] if (OUT / s["video"]).exists()]
        _b["keys"] = {k: v for k, v in _b["keys"].items() if (OUT / v).exists()}
        if _b.get("final") and not (OUT / _b["final"]).exists():
            _b["final"] = None
        _p["battle"] = _b
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
def _(DURATIONS, EDIT_ID, FPS, Image, LTX_ID, STAGE1, SINGLE, gc, inspect, np, shutil, subprocess, wave):
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

        def clear(self):
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        def _text_models(self, where):
            """مدل‌های متنی بزرگ فقط موقع خواندن پرامپت روی GPU هستند"""
            for _name in ("text_encoder", "prompt_enhancer"):
                _m = getattr(self.pipe, _name, None)
                if _m is None or (_name == "prompt_enhancer" and where == "cuda"):
                    continue
                try:
                    if next(_m.parameters()).device.type != where:
                        _m.to(where)
                except Exception:
                    pass
            self.clear()

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
                self._text_models("cpu")
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

            _text = dict(prompt=prompt, negative_prompt=DEFAULT_NEGATIVE_PROMPT)
            try:
                self._say("خواندن پرامپت…")
                self._text_models("cuda")
                with torch.no_grad():
                    _pe, _pm, _ne, _nm = self.pipe.encode_prompt(
                        prompt=prompt, negative_prompt=DEFAULT_NEGATIVE_PROMPT,
                        do_classifier_free_guidance=not _distilled, device=torch.device("cuda"))
                _text = dict(prompt=None, prompt_embeds=_pe, prompt_attention_mask=_pm)
                if not _distilled:
                    _text.update(negative_prompt_embeds=_ne, negative_prompt_attention_mask=_nm)
            except Exception as _e:
                _notes.append(f"خواندن جداگانه‌ی پرامپت انجام نشد ({type(_e).__name__}).")
            finally:
                self._text_models("cpu")

            def _run(img, **kw):
                _base = dict(**_text, num_frames=nf,
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
    _tok = "🔑 توکن از فایل .env خوانده شد" if _env_token else "🔑 توکن Hugging Face را در تب «💾 پروژه و تنظیمات» تنظیم کنید"
    H(f"""<div class="yar-root"><div class="yar-head">
      <h1 style="margin:0;font-size:26px;color:#fff">⚔️ استودیو نبرد سینمایی</h1>
      <div style="opacity:.85;font-size:14px;margin-top:4px">عکس شخصیت‌ها + پرامپت نبرد ← فیلم سینمایی ۴۵ ثانیه تا ۱ دقیقه، 1080p، با صدا</div>
      <span class="yar-pill">{_gpu}</span><span class="yar-pill">{_tok}</span>
    </div></div>""")
    return


@app.cell(hide_code=True)
def _(ASPECTS, PROJECT, STYLES, mo, read_env_token):
    _d = PROJECT["drafts"]

    def _pick(key, options, default):
        _v = _d.get(key)
        return _v if _v in options else default

    style_dd = mo.ui.dropdown(options=list(STYLES), value=_pick("style", STYLES, "🎬 فیلم سینمایی"), label="سبک")
    aspect_dd = mo.ui.dropdown(options=ASPECTS, value=_pick("aspect", ASPECTS, "16:9 افقی"), label="نسبت تصویر")
    seed_in = mo.ui.number(start=-1, stop=2**31 - 1, value=int(_d.get("seed", -1)), label="Seed (‎-1 = تصادفی)")
    hf_token = mo.ui.text(kind="password", value=read_env_token(), label="توکن Hugging Face", full_width=True)
    return aspect_dd, hf_token, seed_in, style_dd


@app.cell(hide_code=True)
def _(mo):
    ticker = mo.ui.refresh(options=["2s", "5s"], default_interval="2s", label="به‌روزرسانی خودکار")
    SEEN = {"v": 0}
    return SEEN, ticker


@app.cell(hide_code=True)
def _(H, JOB, SEEN, aspect_dd, bump, mo, seed_in, style_dd, ticker, time):
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
        H('<div class="yar-root">' + mo.hstack([style_dd, aspect_dd, seed_in, ticker],
                                                      justify="start", gap=1.2, wrap=True).text + "</div>"),
        _status,
    ])
    return


@app.cell(hide_code=True)
def _(random, seed_in):
    def pick_seed():
        return random.randint(0, 2**31 - 1) if seed_in.value is None or seed_in.value < 0 else int(seed_in.value)
    return (pick_seed,)


# ═══════════════════════ ⚔️ نبرد سینمایی: ابزارها ═══════════════════════
@app.cell(hide_code=True)
def _(FPS, Image, absp, ffmpeg_exe, re, subprocess):
    BATTLE_LENGTHS = {
        "۴۵ تا ۵۰ ثانیه (۵ شات)": 5,
        "حدود ۱ دقیقه (۶ شات)": 6,
        "حدود ۷۰ ثانیه (۷ شات)": 7,
    }
    BATTLE_MODES = {
        "🔗 پیوسته: هر شات از آخرین فریم شات قبل ادامه می‌دهد": "continue",
        "🎬 کات سینمایی: هر شات یک زاویه‌ی دوربین جدید (سریع‌تر)": "cut",
    }
    BATTLE_SFX = ("epic orchestral battle music with heavy drums, powerful punch and weapon impacts, metal clashing, "
                  "whooshes, explosions, rumbling ground, grunts and battle cries, no dialogue")

    def _join(names):
        return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]

    def make_battle_plan(names, n):
        """برنامه‌ی پیش‌فرض شات‌ها؛ کاربر می‌تواند هر خط را عوض کند"""
        _a = names[0]
        _b = names[1] if len(names) > 1 else "the enemy"
        _rest = names[2:]
        _all = _join(names)
        _beats = [
            f"Wide establishing shot: {_all} stand facing each other at a distance in a tense standoff, dust and "
            f"embers drifting in the wind, they slowly get into fighting stance, ready to attack. The camera slowly pushes in.",
            f"{_a} charges forward and strikes {_b} with full force; {_b} blocks, and the impact sends a shockwave "
            f"that cracks the ground and throws debris into the air. Dynamic tracking camera.",
            (f"{_rest[0]} leaps into the fight and attacks {_a} and {_b}"
             + (f", while {_rest[1]} strikes from behind" if len(_rest) > 1 else "")
             + "; a chaotic brawl breaks out, heavy blows land on every side. Handheld camera, fast motion.")
            if _rest else
            f"{_b} counterattacks with a brutal combo, pushing {_a} back across the battlefield, sparks flying at "
            f"every hit. Low-angle camera following the action.",
            f"Fast close-quarters exchange of punches, kicks and weapon strikes between {_all}; one is slammed into "
            f"the ground and gets back up. The camera orbits around the fight.",
            f"{_a} gains the upper hand for a moment, then is knocked back hard through a wall of rubble; the others "
            f"press the attack. Slow-motion on the impact, then real speed.",
            f"{_all} each unleash their most powerful attack at the same moment; the energies collide in the center "
            f"with a blinding explosion of light, fire and debris. Wide shot.",
            f"Aftermath: smoke slowly clears over the ruined battlefield, {_all} breathing heavily, battle-damaged, "
            f"still glaring at each other. Slow cinematic push-in.",
        ]
        _order = {5: [0, 1, 2, 3, 5], 6: [0, 1, 2, 3, 5, 6], 7: [0, 1, 2, 3, 4, 5, 6]}[n]
        return "\n".join(_beats[i] for i in _order)

    def collage(paths, h=768, gap=24):
        """چند عکس کاراکتر کنار هم (بدون هوش مصنوعی؛ چهره‌ها دست نمی‌خورند)"""
        _ims = [Image.open(p).convert("RGB") for p in paths]
        _ims = [i.resize((max(1, round(i.width * h / i.height)), h), Image.LANCZOS) for i in _ims]
        _W = sum(i.width for i in _ims) + gap * (len(_ims) + 1)
        _c = Image.new("RGB", (_W, h + 2 * gap), (245, 245, 245))
        _x = gap
        for _i in _ims:
            _c.paste(_i, (_x, gap))
            _x += _i.width + gap
        return _c

    def cast_refs(cast, first_index, max_imgs):
        """cast = [(name, path, look)] ← حداکثر max_imgs عکس مرجع + توضیح انگلیسی"""
        if len(cast) <= max_imgs:
            _groups = [[c] for c in cast]
        else:
            _groups = [[c] for c in cast[:max_imgs - 1]] + [cast[max_imgs - 1:]]
        _imgs, _desc = [], []
        for _i, _g in enumerate(_groups):
            _idx = first_index + _i
            if len(_g) == 1:
                _n, _p, _look = _g[0]
                _imgs.append(Image.open(_p).convert("RGB"))
                _desc.append(f"Image {_idx} is a reference photo of {_n}"
                             + (f" ({_look.rstrip('.')})" if _look else "") + ".")
            else:
                _imgs.append(collage([p for _, p, _ in _g]))
                _who = ", ".join(n + (f" ({look.rstrip('.')})" if look else "") for n, _, look in _g)
                _desc.append(f"Image {_idx} shows reference photos side by side, from left to right: {_who}.")
        return _imgs, " ".join(_desc)

    def concat_videos(shots, out_path):
        """چسباندن شات‌ها به یک فیلم (در حالت پیوسته فریم تکراری اول هر شات حذف می‌شود)"""
        _ff = ffmpeg_exe()
        _probe = subprocess.run([_ff, "-i", str(absp(shots[0]["video"]))], capture_output=True).stderr.decode(errors="ignore")
        _m = re.search(r"Video:.*?(\d{3,4})x(\d{3,4})", _probe)
        _W, _H = (int(_m.group(1)), int(_m.group(2))) if _m else (1920, 1080)
        _cmd = [_ff, "-y", "-loglevel", "error"]
        for _x in shots:
            _cmd += ["-i", str(absp(_x["video"]))]
        _f = []
        for _i, _x in enumerate(shots):
            _start = 1 if (_x.get("continued") and _i > 0) else 0
            _nxt = shots[_i + 1] if _i + 1 < len(shots) else None
            _end = _x.get("frames", 0)
            if _nxt and _nxt.get("continued") and _x.get("end_frame") is not None:
                _end = _x["end_frame"] + 1
            _trim = f"trim=start_frame={_start}" + (f":end_frame={_end}" if _end else "")
            _f.append(f"[{_i}:v]{_trim},setpts=PTS-STARTPTS,scale={_W}:{_H}:force_original_aspect_ratio=increase,"
                      f"crop={_W}:{_H},setsar=1,fps={FPS}[v{_i}]")
            _atrim = f"atrim=start={_start / FPS:.5f}" + (f":end={_end / FPS:.5f}" if _end else "")
            _f.append(f"[{_i}:a]{_atrim},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo[a{_i}]")
        _f.append("".join(f"[v{_i}][a{_i}]" for _i in range(len(shots))) + f"concat=n={len(shots)}:v=1:a=1[v][a]")
        _cmd += ["-filter_complex", ";".join(_f), "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "17",
                 "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                 "-movflags", "+faststart", str(out_path)]
        _r = subprocess.run(_cmd, capture_output=True)
        if _r.returncode != 0:
            raise RuntimeError(_r.stderr.decode(errors="ignore")[-1500:])
        return out_path
    return BATTLE_LENGTHS, BATTLE_MODES, BATTLE_SFX, cast_refs, concat_videos, make_battle_plan


@app.cell(hide_code=True)
def _(mo):
    get_brev, set_brev = mo.state(0)
    return get_brev, set_brev


@app.cell(hide_code=True)
def _(BATTLE_LENGTHS, BATTLE_MODES, PROJECT, QUALITIES, mo):
    _d = PROJECT["drafts"]

    def _bo(key, options, default):
        _x = _d.get(key)
        return _x if _x in options else default

    b_desc = mo.ui.text_area(
        label="میدان نبرد و حال‌وهوا (انگلیسی)", value=_d.get("b_desc", ""), rows=4, full_width=True,
        placeholder="A ruined futuristic city at night, burning buildings, heavy rain and lightning. "
                    "A brutal, evenly matched fight with no mercy.")
    b_len = mo.ui.dropdown(options=list(BATTLE_LENGTHS), value=_bo("b_len", BATTLE_LENGTHS, "حدود ۱ دقیقه (۶ شات)"),
                           label="مدت فیلم")
    b_mode = mo.ui.dropdown(options=list(BATTLE_MODES), value=_bo("b_mode", BATTLE_MODES, list(BATTLE_MODES)[0]),
                            label="نوع پیوستگی")
    b_quality = mo.ui.dropdown(options=QUALITIES, value=_bo("b_quality", QUALITIES, "1080p (1920×1080)"), label="کیفیت")
    b_lock = mo.ui.checkbox(value=bool(_d.get("b_lock", True)),
                            label="🔒 قفل چهره در هر شات (چهره‌ها تا آخر فیلم عوض نشوند)")
    b_sfx = mo.ui.text(label="صدا و موسیقی (خالی = موسیقی حماسی + صدای ضربه و انفجار)", value=_d.get("b_sfx", ""),
                       full_width=True)
    b_plan_btn = mo.ui.run_button(label="📝 ساخت خودکار برنامه‌ی شات‌ها")
    b_go_btn = mo.ui.run_button(label="⚔️ ساخت / ادامه‌ی نبرد", kind="success")
    b_undo_btn = mo.ui.run_button(label="↩️ حذف آخرین شات نبرد", kind="warn")
    b_reset_btn = mo.ui.run_button(label="🔄 شروع نبرد جدید", kind="danger")
    b_merge_btn = mo.ui.run_button(label="🎞 ساخت دوباره‌ی فیلم نهایی")
    return b_desc, b_go_btn, b_len, b_lock, b_merge_btn, b_mode, b_plan_btn, b_quality, b_reset_btn, b_sfx, b_undo_btn


@app.cell(hide_code=True)
def _(PROJECT, get_rev, mo):
    get_rev()
    _names = list(PROJECT["chars"])
    b_chars = mo.ui.multiselect(options=_names,
                                value=[n for n in PROJECT["drafts"].get("b_chars", []) if n in _names][:4],
                                max_selections=4, label="جنگجوها (۲ تا ۴ کاراکتر)")
    return (b_chars,)


@app.cell(hide_code=True)
def _(PROJECT, get_brev, mo):
    get_brev()
    b_plan = mo.ui.text_area(
        label="برنامه‌ی شات‌ها (انگلیسی) — هر خط = یک شات ۱۰ ثانیه‌ای", value=PROJECT["drafts"].get("b_plan", ""),
        rows=12, full_width=True,
        placeholder="Shot 1 on line 1...\nShot 2 on line 2...")
    return (b_plan,)


@app.cell(hide_code=True)
def _(LOCK, PROJECT, b_chars, b_desc, b_len, b_lock, b_mode, b_plan, b_quality, b_sfx, save_project):
    with LOCK:
        PROJECT["drafts"].update(
            b_chars=list(b_chars.value), b_desc=b_desc.value, b_len=b_len.value, b_mode=b_mode.value,
            b_quality=b_quality.value, b_lock=b_lock.value, b_sfx=b_sfx.value, b_plan=b_plan.value,
        )
    save_project()
    return


@app.cell(hide_code=True)
def _(PROJECT, get_rev, mo):
    get_rev()
    _names = list(PROJECT["chars"])
    _prev = PROJECT["drafts"].get("b_fight_char")
    b_fight_char = mo.ui.dropdown(options=_names or ["—"], value=_prev if _prev in _names else (_names or ["—"])[0],
                                  label="کاراکتر")
    return (b_fight_char,)


@app.cell(hide_code=True)
def _(PROJECT, b_fight_char, get_rev, mo):
    get_rev()
    _c = PROJECT["chars"].get(b_fight_char.value, {})
    b_fight_text = mo.ui.text_area(
        label="سلاح، ابزار و سبک مبارزه‌ی این کاراکتر (انگلیسی)", value=_c.get("fight", ""), rows=5, full_width=True,
        placeholder="Wields the twin Blades of Chaos on long chains: swings them in wide fiery arcs, pulls enemies in "
                    "with the chains, then finishes with brutal close-range punches and a ground-pound shockwave.")
    b_fight_save = mo.ui.run_button(label="💾 ذخیره‌ی سبک مبارزه", kind="success")
    return b_fight_save, b_fight_text


@app.cell(hide_code=True)
def _(JOB, LOCK, PROJECT, b_fight_char, b_fight_save, b_fight_text, mo, save_project):
    mo.stop(not b_fight_save.value)
    if b_fight_char.value in PROJECT["chars"]:
        with LOCK:
            PROJECT["chars"][b_fight_char.value]["fight"] = b_fight_text.value.strip()
            PROJECT["drafts"]["b_fight_char"] = b_fight_char.value
        save_project()
        JOB.update(error=None, title="", message=f"✅ سبک مبارزه‌ی «{b_fight_char.value}» ذخیره شد.")
    else:
        JOB.update(error=None, title="", message="⚠️ اول در تب «👤 جنگجوها» کاراکتر بسازید.")
    JOB["version"] += 1
    return


# ═══════════════════════ فرم‌ها (مقدارها خودکار ذخیره می‌شوند) ═══════════════════════
@app.cell(hide_code=True)
def _(mo):
    char_name = mo.ui.text(label="نام (انگلیسی)", placeholder="Kratos")
    char_upload = mo.ui.file(filetypes=[".png", ".jpg", ".jpeg", ".webp"], kind="area", label="عکس کاراکتر")
    char_look = mo.ui.text_area(label="ظاهر (انگلیسی)", rows=3, full_width=True,
                                placeholder="a huge bald warrior with ash-white skin, red tattoo, thick beard, ...")
    char_fight = mo.ui.text_area(label="⚔️ سلاح، ابزار و سبک مبارزه (انگلیسی)", rows=4, full_width=True,
                                 placeholder="Wields twin chained blades: swings them in wide fiery arcs, ...")
    char_add = mo.ui.run_button(label="💾 ذخیره‌ی کاراکتر", kind="success")
    backup_btn = mo.ui.run_button(label="📦 ساخت فایل پشتیبان پروژه")
    restore_file = mo.ui.file(filetypes=[".zip"], kind="area", label="فایل پشتیبان (zip)", max_size=1_500_000_000)
    restore_btn = mo.ui.run_button(label="♻️ بازگردانی پروژه", kind="warn")
    return backup_btn, char_add, char_fight, char_look, char_name, char_upload, restore_btn, restore_file


@app.cell(hide_code=True)
def _(PROJECT, get_rev, mo):
    get_rev()
    _names = list(PROJECT["chars"])
    char_del_dd = mo.ui.dropdown(options=_names or ["—"], label="کاراکتر")
    char_del_btn = mo.ui.run_button(label="🗑 حذف کاراکتر")
    return char_del_btn, char_del_dd


@app.cell(hide_code=True)
def _(JOB, LOCK, OUT, PROJECT, char_add, char_fight, char_look, char_name, char_upload, mo, rel, re, save_project, time):
    mo.stop(not char_add.value)
    _name = re.sub(r"\s+", " ", char_name.value.strip())
    if not _name:
        JOB.update(error=None, title="", message="⚠️ نام کاراکتر را بنویسید.")
    elif not char_upload.value:
        JOB.update(error=None, title="", message="⚠️ یک عکس برای کاراکتر انتخاب کنید.")
    else:
        _dst = OUT / "characters" / f"{int(time.time())}_{re.sub(r'[^\w]+', '_', _name)}.png"
        _dst.write_bytes(char_upload.contents(0))
        with LOCK:
            PROJECT["chars"][_name] = {"image": rel(_dst), "look": char_look.value.strip(),
                                       "fight": char_fight.value.strip()}
        save_project()
        JOB.update(error=None, title="", message=f"✅ کاراکتر «{_name}» ذخیره شد.")
    JOB["version"] += 1
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
        return "✅ فایل پشتیبان آماده است؛ در تب «💾 پروژه و تنظیمات» دانلودش کنید."

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
                for _k in ("images", "chars", "shots", "final", "drafts", "battle"):
                    if _k in _new:
                        PROJECT[_k] = _new[_k]
            save_project()
            JOB.update(error=None, title="", message="✅ پروژه بازگردانی شد. برای برگشتن متن فرم‌ها، نوت‌بوک را یک بار Run all کنید.")
        except Exception as _e:
            JOB.update(error=f"بازگردانی ناموفق: {_e}", title="بازگردانی پروژه", trace="")
    JOB["version"] += 1  # نمایش در به‌روزرسانی بعدی (بدون چرخه)
    return


# ═══════════════════════ ⚔️ نبرد سینمایی: کارها ═══════════════════════
@app.cell(hide_code=True)
def _(BATTLE_LENGTHS, JOB, LOCK, PROJECT, b_chars, b_len, b_plan_btn, make_battle_plan, mo, save_project, set_brev):
    mo.stop(not b_plan_btn.value)
    _names = list(b_chars.value)
    if len(_names) < 2:
        JOB.update(error=None, title="", message="⚠️ حداقل ۲ جنگجو انتخاب کنید.")
    else:
        with LOCK:
            PROJECT["drafts"]["b_plan"] = make_battle_plan(_names, BATTLE_LENGTHS[b_len.value])
        save_project()
        set_brev(lambda v: v + 1)
        JOB.update(error=None, title="", message="✅ برنامه‌ی شات‌ها نوشته شد. هر خط را می‌توانید عوض کنید.")
    JOB["version"] += 1
    return


@app.cell(hide_code=True)
def _(
    BATTLE_MODES, BATTLE_SFX, DURATIONS, EDIT_SIZE, FINAL, Image, JOB, LOCK, OUT, PROJECT, STYLES, absp,
    aspect_dd, b_chars, b_desc, b_go_btn, b_lock, b_mode, b_plan, b_quality, b_sfx, best_end_frame,
    cast_refs, concat_videos, encode_mp4, engine, hf_token, mo, pick_seed, rel, save_project, start_job,
    style_dd, time,
):
    mo.stop(not b_go_btn.value)
    _names = list(b_chars.value)
    _beats = [l.strip() for l in b_plan.value.splitlines() if l.strip()][:8]
    if len(_names) < 2:
        JOB.update(error=None, title="", message="⚠️ حداقل ۲ جنگجو انتخاب کنید.")
        JOB["version"] += 1
    elif not _beats:
        JOB.update(error=None, title="", message="⚠️ برنامه‌ی شات‌ها خالی است؛ «📝 ساخت خودکار برنامه» را بزنید.")
        JOB["version"] += 1
    elif len(PROJECT["battle"]["shots"]) >= len(_beats) and PROJECT["battle"].get("final"):
        JOB.update(error=None, title="", message="✅ این نبرد کامل است. برای نبرد تازه «🔄 شروع نبرد جدید» را بزنید.")
        JOB["version"] += 1
    else:
        def _launch():
            _chars = PROJECT["chars"]
            _cast = [(n, str(absp(_chars[n]["image"])), _chars[n].get("look", "")) for n in _names]
            _fight = {n: _chars[n].get("fight", "") for n in _names}
            _mode = BATTLE_MODES[b_mode.value]
            _lock = b_lock.value
            _q, _asp, _tok = b_quality.value, aspect_dd.value, hf_token.value.strip()
            _style = STYLES[style_dd.value]
            _desc = b_desc.value.strip().rstrip(".")
            _sfx = b_sfx.value.strip() or BATTLE_SFX
            _nf = DURATIONS["۱۰ ثانیه"]
            _n = len(_beats)
            _all = ", ".join(_names[:-1]) + " and " + _names[-1]
            _eh, _ew = EDIT_SIZE[_asp]
            _looks = " ".join(
                f"{n} is {look.rstrip('.')}." for n, _, look in _cast if look
            )
            _moves = " ".join(f"{n}'s fighting style: {f.rstrip('.')}." for n, f in _fight.items() if f)
            _faces = (f"The faces of {_all} must be exactly identical to their reference photos: same facial structure, "
                      "eyes, nose, mouth, skin tone, age, hair, costume, armor and weapons.")

            def _shot_prompt(beat, continued):
                _p = [_style + ".",
                      "Epic live-action blockbuster battle scene, photorealistic, realistic VFX, intense fast fluid fight "
                      "choreography, powerful impacts with real weight."]
                if _desc:
                    _p.append(_desc + ".")
                if _looks:
                    _p.append(_looks)
                if _moves:
                    _p.append(_moves)
                if continued:
                    _p.append("The shot continues seamlessly from the opening frame: same location, lighting and color grade.")
                _p.append(f"{_all} keep exactly the same faces, bodies, costumes, armor and weapons as in the opening "
                          "frame throughout the whole shot.")
                _p.append(beat.rstrip(".") + ".")
                _p.append(f"Audio: {_sfx.rstrip('.')}.")
                return " ".join(_p)

            def _key_prompt(beat, with_scene):
                _refs_first = 2 if with_scene else 1
                _imgs, _rdesc = cast_refs(_cast, _refs_first, 3 - (1 if with_scene else 0))
                _p = [_style + "."]
                if with_scene:
                    _p.append("Image 1 is an earlier frame of this same battle: keep the same location, weather, lighting, "
                              "costumes, armor and weapons.")
                _p.append(_rdesc)
                _p.append(("Create the next shot of the same battle from a new dramatic camera angle: " if with_scene
                           else "Create one new widescreen cinematic film frame of an epic battle: ")
                          + (_desc + ". " if _desc else "") + beat.rstrip(".") + ".")
                if _moves:
                    _p.append(_moves)
                _p.append(_faces + f" All of {_all} clearly visible, dynamic action poses, weapons in hand, sharp focus, "
                          "photorealistic, no text, no watermark.")
                return _imgs, " ".join(_p)

            def _save_key(img, k):
                _p = OUT / "frames" / f"battle_key_{k + 1:02d}_{int(time.time())}.png"
                img.save(_p)
                with LOCK:
                    PROJECT["battle"]["keys"][str(k)] = rel(_p)
                save_project()
                JOB["version"] += 1
                return img

            def _work():
                engine.job = JOB
                _B = PROJECT["battle"]
                _t0 = time.time()
                # ── فریم‌های کلیدی
                if "0" not in _B["keys"]:
                    JOB["title"] = f"نبرد — صحنه‌ی آغاز (۱ از {_n})"
                    _imgs, _p = _key_prompt(_beats[0], False)
                    _save_key(engine.edit(_imgs, _p, _eh, _ew, pick_seed(), _tok), 0)
                _first = Image.open(absp(_B["keys"]["0"])).convert("RGB")
                if _mode == "cut":
                    for _k in range(1, _n):
                        if str(_k) in _B["keys"] or _k < len(_B["shots"]):
                            continue
                        JOB["title"] = f"نبرد — فریم کلیدی شات {_k + 1} از {_n}"
                        _imgs, _p = _key_prompt(_beats[_k], True)
                        _save_key(engine.edit([_first] + _imgs, _p, _eh, _ew, pick_seed(), _tok), _k)
                # ── شات‌ها
                for _k in range(len(_B["shots"]), _n):
                    _seed = pick_seed()
                    _cont = _mode == "continue" and _k > 0
                    if _k == 0 or _mode == "cut":
                        _start = Image.open(absp(_B["keys"][str(_k)])).convert("RGB")
                    else:
                        _start = Image.open(absp(_B["shots"][-1]["last_frame"])).convert("RGB")
                        if _lock:
                            JOB["title"] = f"نبرد — قفل چهره‌ی شات {_k + 1} از {_n}"
                            _imgs, _rdesc = cast_refs(_cast, 2, 2)
                            _ep = (f"Image 1 is a frame from a film. {_rdesc} Edit image 1 only: make the faces, costumes "
                                   f"and weapons of {_all} exactly identical to their reference photos. Keep everything "
                                   "else in image 1 exactly unchanged: same composition, framing, body poses, motion, "
                                   "head angles, background, lighting and colors.")
                            _w0, _h0 = _start.size
                            _s = (1_300_000 / (_w0 * _h0)) ** 0.5
                            _lh, _lw = max(512, int(_h0 * _s) // 16 * 16), max(512, int(_w0 * _s) // 16 * 16)
                            _start = engine.edit([_start] + _imgs, _ep, _lh, _lw, _seed, _tok)
                    JOB["title"] = f"نبرد — ساخت شات {_k + 1} از {_n} (۱۰ ثانیه)"
                    _prompt = _shot_prompt(_beats[_k], _cont)
                    try:
                        _frames, _audio, _sr, _notes = engine.video(_start, _prompt, _nf, _q, _asp, _seed, _tok)
                    except Exception as _err:
                        if "out of memory" not in str(_err).lower() or _q.startswith("720"):
                            raise
                        engine.clear()
                        JOB["title"] = f"نبرد — شات {_k + 1}: حافظه کم بود، ساخت با 720p و بزرگ‌نمایی به 1080p"
                        _frames, _audio, _sr, _notes = engine.video(_start, _prompt, _nf, "720p (1280×720)", _asp,
                                                                    _seed, _tok)
                    JOB["detail"] = "ذخیره‌ی ویدیو…"
                    _e = best_end_frame(_frames)
                    _stamp = int(time.time())
                    _lf = OUT / "frames" / f"battle_{_k + 1:02d}_{_stamp}_last.png"
                    Image.fromarray(_frames[_e]).save(_lf)
                    _vp = OUT / "shots" / f"battle_{_k + 1:02d}_{_stamp}.mp4"
                    encode_mp4(_frames, _audio, _sr, _vp, FINAL[_q][_asp])
                    with LOCK:
                        _B["shots"].append({"video": rel(_vp), "last_frame": rel(_lf), "prompt": _prompt, "seed": _seed,
                                            "continued": _cont, "frames": int(len(_frames)), "end_frame": int(_e),
                                            "beat": _beats[_k]})
                        _B["final"] = None
                    save_project()
                    JOB["version"] += 1
                # ── فیلم نهایی
                JOB["title"] = "نبرد — چسباندن شات‌ها"
                JOB["detail"] = "ساخت فیلم نهایی…"
                _out = concat_videos(_B["shots"], OUT / "final" / f"battle_{int(time.time())}.mp4")
                with LOCK:
                    _B["final"] = rel(_out)
                save_project()
                _min = int((time.time() - _t0) / 60)
                return f"✅ نبرد آماده شد: {len(_B['shots'])} شات، حدود {_min} دقیقه طول کشید. پایین تب «⚔️ نبرد سینمایی» است."

            if not start_job("نبرد سینمایی", _work):
                JOB["message"] = "⏳ یک کار دیگر در حال انجام است."
                JOB["version"] += 1
        _launch()
    return


@app.cell(hide_code=True)
def _(JOB, LOCK, PROJECT, b_undo_btn, mo, save_project):
    mo.stop(not b_undo_btn.value)
    _B = PROJECT["battle"]
    if JOB["running"]:
        JOB["message"] = "⏳ صبر کنید تا کار فعلی تمام شود."
    elif _B["shots"]:
        with LOCK:
            _B["shots"].pop()
            _B["keys"].pop(str(len(_B["shots"])), None)
            _B["final"] = None
        save_project()
        JOB.update(error=None, title="",
                   message=f"↩️ شات {len(_B['shots']) + 1} حذف شد. «⚔️ ساخت / ادامه‌ی نبرد» آن را دوباره می‌سازد.")
    elif _B["keys"]:
        with LOCK:
            _B["keys"] = {}
        save_project()
        JOB.update(error=None, title="", message="↩️ صحنه‌ی آغاز حذف شد؛ دفعه‌ی بعد صحنه‌ی تازه ساخته می‌شود.")
    JOB["version"] += 1
    return


@app.cell(hide_code=True)
def _(JOB, LOCK, PROJECT, b_reset_btn, mo, save_project):
    mo.stop(not b_reset_btn.value)
    if JOB["running"]:
        JOB["message"] = "⏳ صبر کنید تا کار فعلی تمام شود."
    else:
        with LOCK:
            PROJECT["battle"] = {"shots": [], "keys": {}, "final": None}
        save_project()
        JOB.update(error=None, title="", message="🔄 آماده‌ی نبرد جدید. (فیلم‌های قبلی در پوشه‌ی final باقی می‌مانند.)")
    JOB["version"] += 1
    return


@app.cell(hide_code=True)
def _(JOB, LOCK, OUT, PROJECT, b_merge_btn, concat_videos, mo, rel, save_project, start_job, time):
    mo.stop(not b_merge_btn.value)
    _B = PROJECT["battle"]
    if not _B["shots"]:
        JOB.update(error=None, title="", message="⚠️ هنوز شات نبردی ساخته نشده.")
        JOB["version"] += 1
    else:
        def _launch():
            def _work():
                JOB["detail"] = "چسباندن شات‌ها…"
                _out = concat_videos(_B["shots"], OUT / "final" / f"battle_{int(time.time())}.mp4")
                with LOCK:
                    _B["final"] = rel(_out)
                save_project()
                return "✅ فیلم نهایی نبرد دوباره ساخته شد."

            if not start_job("فیلم نهایی نبرد", _work):
                JOB["message"] = "⏳ یک کار دیگر در حال انجام است."
                JOB["version"] += 1
        _launch()
    return


@app.cell(hide_code=True)
def _(
    H, PROJECT, absp, b_chars, b_desc, b_fight_char, b_fight_save, b_fight_text, b_go_btn, b_len, b_lock,
    b_merge_btn, b_mode, b_plan, b_plan_btn, b_quality, b_reset_btn, b_sfx, b_undo_btn, get_rev, mo,
):
    get_rev()

    def _R(x):
        return H('<div class="yar-root">' + (x.text if hasattr(x, "text") else str(x)) + "</div>")

    def _sec(title, note=""):
        return H(f'<div class="yar-root"><div class="yar-sec">{title}</div>'
                 + (f'<div class="yar-muted">{note}</div>' if note else "") + "</div>")

    def _card(*items):
        return H('<div class="yar-root"><div class="yar-card">' + mo.vstack(list(items), gap=0.7).text + "</div></div>")

    def _video(path, label):
        _p = absp(path)
        return mo.vstack([
            mo.video(src=str(_p), controls=True, width="100%"),
            mo.download(data=lambda _p=_p: _p.read_bytes(), filename=_p.name, mimetype="video/mp4", label=label),
        ], gap=0.3)

    _B = PROJECT["battle"]
    _chars = PROJECT["chars"]
    _fighters = [n for n in b_chars.value if n in _chars]
    _roster = mo.hstack([
        mo.vstack([mo.image(src=str(absp(_chars[n]["image"])), width=150, rounded=True),
                   H(f'<div class="yar-root"><b>{n}</b>'
                     + ('' if _chars[n].get("fight") else ' <span class="yar-badge">⚠️ سبک مبارزه ندارد</span>')
                     + "</div>")], gap=0.3)
        for n in _fighters], wrap=True, justify="start", gap=1) if _fighters else H(
        '<div class="yar-root yar-muted">جنگجوها را انتخاب کنید. عکس‌ها را اول در تب «👤 جنگجوها» اضافه کنید.</div>')

    _items = []
    if _B["keys"].get("0"):
        _items.append(mo.vstack([H('<div class="yar-root"><b>🖼 صحنه‌ی آغاز</b></div>'),
                                 mo.image(src=str(absp(_B["keys"]["0"])), width="100%", rounded=True)], gap=0.3))
    for _i, _x in enumerate(_B["shots"]):
        _items.append(mo.vstack([
            H(f'<div class="yar-root"><b>شات {_i + 1}</b>'
              + (' <span class="yar-badge">🔗 ادامه‌ی شات قبل</span>' if _x.get("continued") else "") + "</div>"),
            _video(_x["video"], "⬇️ دانلود شات"),
            mo.accordion({"پرامپت این شات": mo.md(f"```text\n{_x['prompt']}\n```")}),
        ], gap=0.4))
    _timeline = mo.vstack(_items, gap=1.2) if _items else H(
        '<div class="yar-root yar-muted">هنوز چیزی ساخته نشده.</div>')
    _final = (mo.vstack([H('<div class="yar-root yar-sec">🏁 فیلم نهایی نبرد</div>'),
                         _video(_B["final"], "⬇️ دانلود فیلم نهایی")])
              if _B.get("final") else mo.md(""))

    _form = mo.vstack([
        _card(_sec("⚔️ جنگجوها", "۲ تا ۴ کاراکتر. هرچه کمتر، مبارزه تمیزتر و چهره‌ها دقیق‌تر."),
              _R(b_chars), _roster),
        _card(_sec("🗡 سلاح و سبک مبارزه‌ی هر کاراکتر",
                   "بنویسید با چه سلاحی، چطور حمله می‌کند و حرکت خاصش چیست. در همه‌ی شات‌ها استفاده می‌شود."),
              _R(b_fight_char), _R(b_fight_text), _R(b_fight_save)),
        _card(_sec("🎬 نبرد"),
              _R(b_desc),
              _R(mo.hstack([b_len, b_quality], justify="start", gap=1, wrap=True)),
              _R(b_mode), _R(b_lock),
              _R(b_plan_btn), _R(b_plan), _R(b_sfx),
              H('<div class="yar-muted yar-root">هر شات حدود ۵ تا ۸ دقیقه طول می‌کشد؛ کل نبرد ۱ دقیقه‌ای حدود '
                '۳۰ تا ۵۰ دقیقه. اگر وسط کار قطع شد، دوباره «ساخت / ادامه» بزنید؛ از همان‌جا ادامه می‌دهد.</div>'),
              _R(mo.hstack([b_go_btn, b_undo_btn, b_merge_btn, b_reset_btn], justify="start", gap=1, wrap=True))),
    ], gap=1)
    battle_tab = mo.hstack([
        mo.vstack([_card(_sec("🎞 شات‌های نبرد"), _timeline), _final], gap=1),
        _form,
    ], widths=[1.15, 1], gap=1.5, align="start")
    return (battle_tab,)


# ═══════════════════════ نمایش ═══════════════════════
@app.cell(hide_code=True)
def _(H, PROJECT, absp, get_rev, mo):
    get_rev()
    _chars = PROJECT["chars"]
    chars_view = mo.hstack([
        mo.vstack([
            mo.image(src=str(absp(_c["image"])), width=190, rounded=True),
            H(f'<div class="yar-root"><b>{_n}</b>'
              f'<div class="yar-muted yar-ltr" style="max-width:190px">{_c.get("fight", "")[:140]}</div></div>'),
        ], gap=0.3) for _n, _c in _chars.items()
    ], wrap=True, justify="start", gap=1) if _chars else H('<div class="yar-root yar-muted">هنوز کاراکتری نیست.</div>')
    if PROJECT.get("backup"):
        _bp = absp(PROJECT["backup"])
        backup_view = mo.download(data=lambda: _bp.read_bytes(), filename=_bp.name, mimetype="application/zip",
                                  label=f"⬇️ دانلود {_bp.name} ({_bp.stat().st_size / 1e6:.0f} MB)")
    else:
        backup_view = mo.md("")
    return backup_view, chars_view


@app.cell(hide_code=True)
def _(
    H, backup_btn, backup_view, battle_tab, char_add, char_del_btn, char_del_dd, char_fight, char_look,
    char_name, char_upload, chars_view, hf_token, mo, restore_btn, restore_file,
):
    def _R(x):
        return H('<div class="yar-root">' + (x.text if hasattr(x, "text") else str(x)) + "</div>")

    def _sec(title, note=""):
        return H(f'<div class="yar-root"><div class="yar-sec">{title}</div>'
                 + (f'<div class="yar-muted">{note}</div>' if note else "") + "</div>")

    def _card(*items):
        return H('<div class="yar-root"><div class="yar-card">' + mo.vstack(list(items), gap=0.7).text + "</div></div>")

    _tab_char = mo.hstack([
        mo.vstack([_card(_sec("👥 جنگجوها"), chars_view),
                   _card(_R(mo.hstack([char_del_dd, char_del_btn], justify="start", gap=1)))], gap=1),
        _card(_sec("➕ کاراکتر جدید", "بهترین عکس: صورت و بدن واضح، با لباس و سلاح خود کاراکتر"),
              _R(char_name), _R(char_upload), _R(char_look), _R(char_fight), _R(char_add)),
    ], widths=[1.3, 1], gap=1.5, align="start")

    _tab_proj = mo.hstack([
        _card(_sec("💾 پشتیبان پروژه", "molab فایل‌ها را بعد از خاموش شدن نگه نمی‌دارد. قبل از بستن، پشتیبان بسازید."),
              _R(backup_btn), backup_view, _R(restore_file), _R(restore_btn)),
        _card(_sec("🔑 توکن Hugging Face"), _R(hf_token),
              H('<div class="yar-root yar-muted">در پنل <b>Files</b> فایلی به اسم <code>.env</code> بسازید و بنویسید: '
                '<code class="yar-ltr">HF_TOKEN=hf_...</code></div>')),
    ], widths=[1, 1], gap=1.5, align="start")

    mo.ui.tabs({"⚔️ نبرد": battle_tab, "👤 جنگجوها": _tab_char, "💾 پروژه و تنظیمات": _tab_proj})
    return

if __name__ == "__main__":
    app.run()
