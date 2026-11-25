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
#  Ƴα૨ Studio — استودیوی فیلم سینمایی با LTX 2.5 (برای molab / marimo)
#  1) GPU (RTX Pro 6000) را از دکمه‌ی مشخصات بالای صفحه روشن کنید   2) Run all
#
#  ساختار پایدار: هر مدل فقط یک‌بار بار می‌شود و بعد کامل پاک می‌شود
#    مرحله‌ی ۱  تصویر شروع هر صحنه (Qwen Image Edit، با چهره‌ی شخصیت‌ها) ← شما تصویرها را می‌بینید و تأیید می‌کنید
#    مرحله‌ی ۲  خواندن پرامپت همه‌ی صحنه‌ها (مدل متن LTX) ← پاک می‌شود
#    مرحله‌ی ۳  ساخت ویدیوی همه‌ی صحنه‌ها (LTX 2.5، روش رسمی دومرحله‌ای) ← چسباندن فیلم نهایی
#  هر قدمِ تمام‌شده روی دیسک ذخیره می‌شود؛ بعد از قطعی همان دکمه را دوباره بزنید.

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="full", app_title="Ƴα૨ Studio")


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
    import torch
    return (torch,)


@app.cell(hide_code=True)
def _():
    LTX_ID = "Lightricks/LTX-2.5-Diffusers"
    EDIT_ID = "Qwen/Qwen-Image-Edit-2511"
    FPS = 24
    STYLES = {
        "🎬 فیلم سینمایی واقعی": (
            "Photorealistic live-action movie still from a big-budget Hollywood film, shot on ARRI Alexa 65 with "
            "anamorphic lenses, real actors in real practical costumes, realistic skin texture with pores, sweat and "
            "dirt, physically accurate lighting, natural film color grading, subtle film grain"),
        "🎥 واقعی و طبیعی": (
            "Natural photorealistic live-action footage, real people, modern cinema camera, natural light, "
            "true-to-life colors"),
        "🕯 تاریک و ترسناک": (
            "Photorealistic dark live-action thriller, low-key lighting, deep shadows, desaturated cold tones, "
            "drifting fog"),
        "🐉 فانتزی حماسی": (
            "Photorealistic live-action epic fantasy film, grand scale, volumetric god rays, real practical "
            "costumes, sweeping cinematography"),
        "🧸 انیمیشن سه‌بعدی": "High-quality 3D animated feature film, stylized characters, soft global illumination",
        "🌸 انیمه": "Japanese anime, cel-shaded characters, detailed painted backgrounds, dynamic anime camera",
    }
    REAL_STYLES = {k for k in STYLES if "انیم" not in k}
    NEG_REAL = ("cartoon, anime, illustration, painting, drawing, concept art, digital art, 3d render, CGI look, "
                "video game graphics, plastic skin, waxy face, oversaturated colors, extra weapons, wrong weapon, "
                "extra limbs, extra fingers, deformed hands, blurry, text, watermark")
    NEG_ANY = "extra limbs, extra fingers, deformed hands, blurry, text, watermark, extra weapons"
    # ارتفاع و پهنا باید بر ۶۴ بخش‌پذیر باشند (روش دومرحله‌ای رسمی). خروجی نهایی به اندازه‌ی استاندارد بریده می‌شود.
    QUALITY = {
        "720p": {"16:9 افقی": ((384, 640), (720, 1280)), "9:16 عمودی": ((640, 384), (1280, 720))},
        "1080p": {"16:9 افقی": ((544, 960), (1080, 1920)), "9:16 عمودی": ((960, 544), (1920, 1080))},
    }
    EDIT_SIZE = {"16:9 افقی": (928, 1664), "9:16 عمودی": (1664, 928)}
    SECONDS = {"۵ ثانیه": 121, "۷ ثانیه": 169, "۱۰ ثانیه": 241}  # فریم‌ها: 8n+1
    DEFAULT_SFX = ("cinematic orchestral score, realistic sound effects matching every action: footsteps, cloth, "
                   "impacts, ambience")
    return DEFAULT_SFX, EDIT_ID, EDIT_SIZE, FPS, LTX_ID, NEG_ANY, NEG_REAL, QUALITY, REAL_STYLES, SECONDS, STYLES


@app.cell(hide_code=True)
def _(Path, json, os, threading):
    # ───────────── پروژه روی دیسک ─────────────
    OUT = Path("yar_studio_output").resolve()
    for _d in ("characters", "keyframes", "embeds", "scenes", "final", "backups"):
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
            for _f in ("image", "embeds", "video"):
                if _s.get(_f) and not (OUT / _s[_f]).exists():
                    _s[_f] = None
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
    # ───────────── کار در پس‌زمینه: صفحه هیچ‌وقت قفل نمی‌شود ─────────────
    JOB = {"running": False, "title": "", "detail": "", "step": 0, "total": 0, "start": 0.0, "version": 0,
           "error": None, "message": "", "stop": False}

    def start_job(title, fn):
        if JOB["running"]:
            return False
        JOB.update(running=True, title=title, detail="آماده‌سازی…", step=0, total=0, start=time.time(),
                   error=None, message="", stop=False)

        def _run():
            try:
                JOB["message"] = fn() or "✅ انجام شد."
            except Exception as _e:
                _t = str(_e).lower()
                if "out of memory" in _t:
                    JOB["error"] = "حافظه‌ی کارت گرافیک کافی نبود. کیفیت 720p یا صحنه‌های کوتاه‌تر را امتحان کنید."
                elif "no space left" in _t:
                    JOB["error"] = "فضای دیسک molab پر شد."
                elif any(x in _t for x in ("401", "403", "gated", "unauthorized", "access to model")):
                    JOB["error"] = ("دسترسی به مدل ندارید: در Hugging Face شرایط مدل را قبول کنید و توکن را در تب "
                                    "«⚙️ تنظیمات» بگذارید.")
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
def _(EDIT_ID, FPS, Image, LTX_ID, OUT, gc, os, re, shutil, subprocess, torch):
    # ───────────── موتور: هر لحظه فقط یک مدل روی کارت گرافیک ─────────────
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

    def fit_image(img, h, w):
        img = img.convert("RGB")
        _s = max(w / img.width, h / img.height)
        img = img.resize((max(w, round(img.width * _s)), max(h, round(img.height * _s))), Image.LANCZOS)
        _l, _t = (img.width - w) // 2, (img.height - h) // 2
        return img.crop((_l, _t, _l + w, _t + h))

    def collage(paths, h=768, gap=24):
        """چند عکس کنار هم (برای بیش از ۳ شخصیت)؛ چهره‌ها دست نمی‌خورند"""
        _ims = [load_rgb(p) for p in paths]
        _ims = [i.resize((max(1, round(i.width * h / i.height)), h), Image.LANCZOS) for i in _ims]
        _c = Image.new("RGB", (sum(i.width for i in _ims) + gap * (len(_ims) + 1), h + 2 * gap), (245, 245, 245))
        _x = gap
        for _i in _ims:
            _c.paste(_i, (_x, gap))
            _x += _i.width + gap
        return _c

    def cast_refs(cast, first_index, max_imgs):
        """cast = [(name, path, look)] ← حداکثر max_imgs عکس + توضیح انگلیسی برای مدل تصویر"""
        if len(cast) <= max_imgs:
            _groups = [[c] for c in cast]
        else:
            _groups = [[c] for c in cast[:max_imgs - 1]] + [cast[max_imgs - 1:]]
        _imgs, _desc = [], []
        for _i, _g in enumerate(_groups):
            _idx = first_index + _i
            if len(_g) == 1:
                _n, _p, _look = _g[0]
                _imgs.append(load_rgb(_p))
                _desc.append(f"Image {_idx} is a reference photo of {_n}" + (f" ({_look.rstrip('.')})" if _look else "") + ".")
            else:
                _imgs.append(collage([p for _, p, _ in _g]))
                _who = ", ".join(n + (f" ({l.rstrip('.')})" if l else "") for n, _, l in _g)
                _desc.append(f"Image {_idx} shows reference photos side by side, from left to right: {_who}.")
        return _imgs, " ".join(_desc)

    def wipe(module):
        """وزن‌ها مستقیم از کارت گرافیک پاک می‌شوند (به رم ۳۲ گیگی منتقل نمی‌شوند)"""
        if not isinstance(module, torch.nn.Module):
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

    def use_token(token):
        if token:
            os.environ["HF_TOKEN"] = token

    def disk_free_gb():
        try:
            return shutil.disk_usage(OUT).free / 1e9
        except Exception:
            return -1

    def drop_cached(repo_id):
        """اگر دیسک کم بود، فایل‌های دانلودی یک مدلِ استفاده‌شده پاک می‌شود"""
        try:
            from huggingface_hub import scan_cache_dir
            _info = scan_cache_dir()
            _revs = [r.commit_hash for repo in _info.repos if repo.repo_id == repo_id for r in repo.revisions]
            if _revs:
                _info.delete_revisions(*_revs).execute()
        except Exception:
            pass

    class Engine:
        def __init__(self):
            self.kind = None
            self.pipe = None
            self.up = None
            self.job = None

        def say(self, detail, step=None, total=None):
            if self.job is not None:
                self.job["detail"] = detail
                if step is not None:
                    self.job["step"], self.job["total"] = step, total

        def _cb(self, label, total):
            def _f(pipe, i, t, kw):
                self.say(label, i + 1, total)
                return kw
            return _f

        def free(self):
            for _p in (self.pipe, self.up):
                if _p is None:
                    continue
                try:
                    _p.reset_device_map()
                except Exception:
                    pass
                for _m in list(getattr(_p, "components", {}).values()):
                    wipe(_m)
            self.pipe = self.up = None
            self.kind = None
            clear()

        def _need(self, pipe, names):
            _missing = [n for n in names if getattr(pipe, n, None) is None]
            if _missing:
                raise RuntimeError("این بخش‌های مدل بار نشدند: " + ", ".join(_missing))

        def _load(self, cls, repo, token, **kw):
            self.say("دانلود/بارگذاری مدل (بار اول ممکن است ۱۰ تا ۲۰ دقیقه طول بکشد)…", 0, 0)
            clear()
            try:
                return cls.from_pretrained(repo, torch_dtype=torch.bfloat16, device_map="cuda",
                                           token=token or None, **kw)
            except Exception as _e:
                _t = str(_e).lower()
                if any(x in _t for x in ("gated", "401", "403")):
                    raise RuntimeError(f"دسترسی به مدل {repo} ندارید (403/401). شرایط را در Hugging Face قبول کنید "
                                       "و توکن را بگذارید.") from _e
                raise

        # ── مرحله‌ی ۱: مدل تصویر
        def load_edit(self, token):
            if self.kind == "edit":
                return
            self.free()
            from diffusers import QwenImageEditPlusPipeline
            self.pipe = self._load(QwenImageEditPlusPipeline, EDIT_ID, token)
            self.kind = "edit"

        def edit(self, images, prompt, h, w, seed, negative):
            _g = torch.Generator("cuda").manual_seed(int(seed))
            return self.pipe(image=[i.convert("RGB") for i in images], prompt=prompt, negative_prompt=negative,
                             true_cfg_scale=4.0, num_inference_steps=40, height=h, width=w, generator=_g,
                             callback_on_step_end=self._cb("ساخت تصویر صحنه", 40)).images[0]

        # ── مرحله‌ی ۲: فقط مدل متن LTX
        def load_reader(self, token):
            if self.kind == "reader":
                return
            self.free()
            from diffusers import LTX2ImageToVideoPipeline
            self.pipe = self._load(LTX2ImageToVideoPipeline, LTX_ID, token, transformer=None, vae=None,
                                   audio_vae=None, connectors=None, vocoder=None, duration_head=None,
                                   prompt_enhancer=None, processor=None)
            self._need(self.pipe, ("text_encoder", "tokenizer"))
            self.kind = "reader"

        def read(self, prompt):
            with torch.no_grad():
                _pe, _pm, _, _ = self.pipe.encode_prompt(prompt=prompt, do_classifier_free_guidance=False,
                                                         device=torch.device("cuda"))
            return {"prompt_embeds": _pe.detach().cpu(), "prompt_attention_mask": _pm.detach().cpu()}

        # ── مرحله‌ی ۳: مدل ویدیو LTX (بدون مدل متن)
        def load_maker(self, token):
            if self.kind == "maker":
                return
            self.free()
            from diffusers import LTX2ImageToVideoPipeline, LTX2LatentUpsamplePipeline
            try:
                from diffusers.models.latent_upscaler import LTX2LatentUpsamplerModel
            except Exception:
                from diffusers.pipelines.ltx2.latent_upsampler import LTX2LatentUpsamplerModel
            self.pipe = self._load(LTX2ImageToVideoPipeline, LTX_ID, token, text_encoder=None,
                                   prompt_enhancer=None, processor=None)
            self._need(self.pipe, ("transformer", "vae", "audio_vae", "connectors", "vocoder"))
            try:
                self.pipe.vae.enable_tiling()
            except Exception:
                pass
            self.say("بارگذاری بزرگ‌نمای ×۲…")
            _m = LTX2LatentUpsamplerModel.from_pretrained(LTX_ID, subfolder="latent_upsampler",
                                                          torch_dtype=torch.bfloat16, token=token or None).to("cuda")
            self.up = LTX2LatentUpsamplePipeline(vae=self.pipe.vae, latent_upsampler=_m)
            self.kind = "maker"

        def make(self, image, embeds, nf, stage1_hw, seed, out_path):
            """روش رسمی LTX 2.5: مرحله‌ی ۱ نصف اندازه ← بزرگ‌نمایی ×۲ ← مرحله‌ی ۲ اندازه‌ی کامل"""
            from diffusers.pipelines.ltx2.utils import DISTILLED_SIGMA_VALUES, STAGE_2_DISTILLED_SIGMA_VALUES
            from diffusers.utils.export_utils import encode_video
            _h, _w = stage1_hw
            _pe = embeds["prompt_embeds"].to("cuda")
            _pm = embeds["prompt_attention_mask"].to("cuda")
            _g = torch.Generator("cuda").manual_seed(int(seed))
            _common = dict(prompt=None, prompt_embeds=_pe, prompt_attention_mask=_pm, num_frames=nf,
                           frame_rate=float(FPS), guidance_scale=1.0, audio_guidance_scale=1.0, image_crf=18,
                           generator=_g, return_dict=False)
            with torch.no_grad():
                _vl, _al = self.pipe(image=fit_image(image, _h, _w), height=_h, width=_w,
                                     sigmas=DISTILLED_SIGMA_VALUES, output_type="latent",
                                     callback_on_step_end=self._cb("ویدیو — مرحله‌ی ۱ از ۲",
                                                                   len(DISTILLED_SIGMA_VALUES)), **_common)
                self.say("بزرگ‌نمایی ×۲…")
                _up = self.up(latents=_vl, latents_normalized=False, output_type="latent", return_dict=False)[0]
                _v, _a = self.pipe(image=fit_image(image, _h * 2, _w * 2), height=_h * 2, width=_w * 2,
                                   latents=_up, audio_latents=_al, sigmas=STAGE_2_DISTILLED_SIGMA_VALUES,
                                   noise_scale=STAGE_2_DISTILLED_SIGMA_VALUES[0], output_type="np",
                                   callback_on_step_end=self._cb("ویدیو — مرحله‌ی ۲ از ۲",
                                                                 len(STAGE_2_DISTILLED_SIGMA_VALUES)), **_common)
            self.say("ذخیره‌ی ویدیو…")
            encode_video(_v[0], fps=FPS, audio=_a[0].float().cpu(),
                         audio_sample_rate=self.pipe.vocoder.config.output_sampling_rate, output_path=str(out_path))
            del _vl, _al, _up, _v, _a, _pe, _pm
            clear()
            return out_path

    def concat(paths, out_path, out_hw):
        _ff = ffmpeg_exe()
        _H, _W = out_hw
        _cmd = [_ff, "-y", "-loglevel", "error"]
        for _p in paths:
            _cmd += ["-i", str(_p)]
        _f = []
        for _i in range(len(paths)):
            _f.append(f"[{_i}:v]scale={_W}:{_H}:force_original_aspect_ratio=increase:flags=lanczos,"
                      f"crop={_W}:{_H},setsar=1,fps={FPS}[v{_i}]")
            _f.append(f"[{_i}:a]aresample=48000,aformat=channel_layouts=stereo[a{_i}]")
        _f.append("".join(f"[v{_i}][a{_i}]" for _i in range(len(paths))) + f"concat=n={len(paths)}:v=1:a=1[v][a]")
        _cmd += ["-filter_complex", ";".join(_f), "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "17",
                 "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                 "-movflags", "+faststart", str(out_path)]
        _r = subprocess.run(_cmd, capture_output=True)
        if _r.returncode != 0:
            raise RuntimeError(re.sub(r"\s+", " ", _r.stderr.decode(errors="ignore"))[-1500:])
        return out_path

    engine = Engine()
    return cast_refs, clear, concat, disk_free_gb, drop_cached, engine, use_token


@app.cell(hide_code=True)
def _(mo, re):
    # ───────────── ظاهر ─────────────
    _F = "font-family:Vazirmatn,Tahoma,sans-serif;"
    STY = {
        "y-root": "direction:rtl;" + _F,
        "y-card": "border:1px solid #e6e2f3;border-radius:16px;padding:16px 18px;background:#ffffff;"
                  "box-shadow:0 1px 3px rgba(40,20,90,.06);" + _F,
        "y-sec": "font-weight:800;color:#2d1f73;font-size:17px;margin:0 0 4px;",
        "y-step": "display:inline-flex;align-items:center;justify-content:center;width:26px;height:26px;"
                  "border-radius:50%;background:#5b3fd1;color:#fff;font-size:14px;font-weight:800;margin-left:8px;",
        "y-muted": "color:#75708a;font-size:13px;line-height:1.9;",
        "y-badge": "display:inline-block;border-radius:999px;padding:2px 10px;font-size:12px;font-weight:700;"
                   "background:#efeaff;color:#4a2fb5;margin:0 4px;",
        "y-ok": "display:inline-block;border-radius:999px;padding:2px 10px;font-size:12px;font-weight:700;"
                "background:#e3f6ea;color:#17793d;margin:0 4px;",
        "y-wait": "display:inline-block;border-radius:999px;padding:2px 10px;font-size:12px;font-weight:700;"
                  "background:#f3f1f8;color:#77738c;margin:0 4px;",
        "y-ltr": "direction:ltr;text-align:left;",
        "y-head": "background:linear-gradient(120deg,#160f33,#3d2696 55%,#7655ee);color:#fff;border-radius:18px;"
                  "padding:20px 26px;" + _F,
        "y-pill": "display:inline-block;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.18);"
                  "border-radius:999px;padding:3px 12px;margin:10px 0 0 6px;font-size:13px;",
        "y-scene": "border:1px solid #ece8f7;border-radius:14px;padding:12px;background:#fbfaff;" + _F,
        "y-empty": "border:2px dashed #ddd6f5;border-radius:14px;padding:26px;text-align:center;color:#8f89a8;"
                   "background:#fcfbff;" + _F,
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

    def R(x):
        return H('<div class="y-root">' + (x.text if hasattr(x, "text") else str(x)) + "</div>")

    def sec(title, note="", step=None):
        _s = f'<span class="y-step">{step}</span>' if step else ""
        return H(f'<div class="y-root"><div class="y-sec">{_s}{title}</div>'
                 + (f'<div class="y-muted">{note}</div>' if note else "") + "</div>")

    def F(label, widget):
        """برچسب فارسی راست‌چین + جعبه‌ی متن انگلیسی چپ‌چین"""
        return H(f'<div class="y-root"><div style="font-size:14px;font-weight:600;color:#3a335a;margin-bottom:5px">{label}</div>'
                 '<div style="direction:ltr;text-align:left">' + widget.text + "</div></div>")

    def card(*items):
        return H('<div class="y-root"><div class="y-card">' + mo.vstack(list(items), gap=0.8).text + "</div></div>")

    mo.Html('<link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">')
    return F, H, R, card, sec


@app.cell(hide_code=True)
def _(H, disk_free_gb, read_env_token, torch):
    if torch.cuda.is_available():
        _p = torch.cuda.get_device_properties(0)
        _gpu = f"✅ {_p.name.replace('NVIDIA ', '')} — {_p.total_memory / 1e9:.0f} GB"
    else:
        _gpu = "❌ GPU روشن نیست — از دکمه‌ی مشخصات بالای صفحه RTX Pro 6000 را انتخاب کنید"
    _disk = disk_free_gb()
    # بعضی دیسک‌های molab عدد بی‌معنی (خیلی بزرگ) برمی‌گردانند
    _dk = f"💽 دیسک آزاد: {_disk:.0f} GB" if 0 <= _disk < 100000 else "💽 دیسک: بدون محدودیت مشخص"
    _tok = "✅ توکن Hugging Face" if read_env_token() else "🔑 توکن را در تب «⚙️ تنظیمات» بگذارید"
    H(f"""<div class="y-root"><div class="y-head">
      <div style="font-size:28px;font-weight:900;letter-spacing:.5px">Ƴα૨ Studio</div>
      <div style="opacity:.92;margin-top:2px">استودیوی فیلم سینمایی با LTX 2.5 — شخصیت‌ها ← داستان ← تصویر صحنه‌ها ← فیلم</div>
      <span class="y-pill">{_gpu}</span><span class="y-pill">{_dk}</span><span class="y-pill">{_tok}</span>
    </div></div>""")
    return


@app.cell(hide_code=True)
def _(PROJECT, QUALITY, SECONDS, STYLES, mo, read_env_token):
    _d = PROJECT["drafts"]

    def _pick(key, options, default):
        _v = _d.get(key)
        return _v if _v in options else default

    _aspects = ["16:9 افقی", "9:16 عمودی"]
    style_dd = mo.ui.dropdown(options=list(STYLES), value=_pick("style", STYLES, list(STYLES)[0]), label="سبک تصویر")
    aspect_dd = mo.ui.dropdown(options=_aspects, value=_pick("aspect", _aspects, _aspects[0]), label="نسبت تصویر")
    quality_dd = mo.ui.dropdown(options=list(QUALITY), value=_pick("quality", QUALITY, "720p"), label="کیفیت")
    sec_dd = mo.ui.dropdown(options=list(SECONDS), value=_pick("seconds", SECONDS, "۷ ثانیه"), label="طول هر صحنه")
    story_in = mo.ui.text_area(
        value=_d.get("story", ""), rows=3, full_width=True,
        placeholder="A frozen Norse mountain plateau at dusk, ancient stone ruins, heavy falling snow, cold blue light.")
    scenes_in = mo.ui.text_area(
        value=_d.get("scenes", ""), rows=10, full_width=True,
        placeholder="Wide shot: the two warriors face each other in the snow...\n"
                    "Close-up: Kratos grips his axe and growls...")
    sfx_in = mo.ui.text(value=_d.get("sfx", ""), full_width=True,
                        placeholder="epic orchestral music, heavy impacts, howling wind")
    seed_in = mo.ui.number(value=-1, start=-1, stop=2**31 - 1, step=1, label="Seed (‎-1 = تصادفی)")
    hf_token = mo.ui.text(value=read_env_token(), kind="password", full_width=True, placeholder="hf_...")
    ticker = mo.ui.refresh(options=["2s", "5s"], default_interval="2s", label="به‌روزرسانی")
    img_btn = mo.ui.run_button(label="🖼 ساخت تصویر صحنه‌ها", kind="success")
    vid_btn = mo.ui.run_button(label="🎬 ساخت ویدیوها و فیلم نهایی", kind="success")
    merge_btn = mo.ui.run_button(label="🎞 چسباندن دوباره‌ی فیلم")
    stop_btn = mo.ui.run_button(label="⏹ توقف بعد از صحنه‌ی فعلی", kind="warn")
    reset_btn = mo.ui.run_button(label="🗑 پاک کردن همه‌ی صحنه‌ها", kind="danger")
    return (
        aspect_dd, hf_token, img_btn, merge_btn, quality_dd, reset_btn, scenes_in, sec_dd, seed_in, sfx_in,
        stop_btn, story_in, style_dd, ticker, vid_btn,
    )


@app.cell(hide_code=True)
def _(LOCK, PROJECT, aspect_dd, quality_dd, save_project, scenes_in, sec_dd, sfx_in, story_in, style_dd):
    with LOCK:
        PROJECT["drafts"].update(style=style_dd.value, aspect=aspect_dd.value, quality=quality_dd.value,
                                 seconds=sec_dd.value, story=story_in.value, scenes=scenes_in.value, sfx=sfx_in.value)
    save_project()
    return


@app.cell(hide_code=True)
def _(mo):
    char_name = mo.ui.text(placeholder="Kratos", full_width=True)
    char_upload = mo.ui.file(filetypes=[".png", ".jpg", ".jpeg", ".webp"], kind="area", label="عکس شخصیت")
    char_look = mo.ui.text_area(rows=3, full_width=True,
                                placeholder="a huge bald warrior with ash-white skin, a red tattoo and a thick beard")
    char_role = mo.ui.text_area(rows=3, full_width=True,
                                placeholder="Fights with a frost axe that he throws and calls back; slow, heavy strikes.")
    char_add = mo.ui.run_button(label="💾 ذخیره‌ی شخصیت", kind="success")
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
    char_del_dd = mo.ui.dropdown(options=_names or ["—"], label="شخصیت")
    char_del_btn = mo.ui.run_button(label="🗑 حذف")
    _opts = [f"صحنه {i + 1}" for i in range(len(PROJECT["scenes"]))] or ["—"]
    redo_dd = mo.ui.dropdown(options=_opts, value=_opts[0], label="صحنه")
    redo_img_btn = mo.ui.run_button(label="🖼 تصویر تازه")
    redo_vid_btn = mo.ui.run_button(label="🎬 ویدیوی تازه")
    return cast_ms, char_del_btn, char_del_dd, redo_dd, redo_img_btn, redo_vid_btn


@app.cell(hide_code=True)
def _(LOCK, PROJECT, cast_ms, save_project):
    with LOCK:
        PROJECT["drafts"]["cast"] = list(cast_ms.value)
    save_project()
    return


@app.cell(hide_code=True)
def _(Path, os):
    def hf_cache_gb():
        """حجم فایل‌های دانلودشده‌ی Hugging Face (برای نمایش پیشرفت دانلود)"""
        _root = Path(os.environ.get("HF_HUB_CACHE") or Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface")) / "hub")
        _tot = 0
        for _dp, _dn, _fn in os.walk(_root):
            for _f in _fn:
                try:
                    _p = os.path.join(_dp, _f)
                    if not os.path.islink(_p):
                        _tot += os.path.getsize(_p)
                except OSError:
                    pass
        return _tot / 1e9
    return (hf_cache_gb,)


@app.cell(hide_code=True)
def _(H, JOB, bump, hf_cache_gb, mo, ticker, time):
    # نوار وضعیت؛ هر ۲ ثانیه تازه می‌شود
    ticker
    if JOB["version"] != getattr(bump, "seen", 0):
        bump.seen = JOB["version"]
        bump()
    if JOB["running"]:
        _el = int(time.time() - JOB["start"])
        _pct = int(100 * JOB["step"] / JOB["total"]) if JOB["total"] else 4
        _steps = f" — {JOB['step']} از {JOB['total']}" if JOB["total"] else ""
        if "دانلود" in JOB["detail"]:
            # شمارنده‌ی دانلود: حجم و سرعت (اگر عدد بالا می‌رود یعنی کار گیر نکرده)
            _gb, _now = hf_cache_gb(), time.time()
            _prev = getattr(bump, "dl", None)
            _spd = ""
            if _prev and _now > _prev[1]:
                _mbs = max(0.0, (_gb - _prev[0]) * 1000 / (_now - _prev[1]))
                _spd = f" — سرعت: {_mbs:.0f} MB/s"
            bump.dl = (_gb, _now)
            _steps = f"<br>📥 دانلود شده تا الان: <b>{_gb:.1f} GB</b>{_spd}"
        _status = H(f"""<div class="y-root"><div class="y-card" style="border-color:#cfc3ff">
          <div class="y-sec">⏳ {JOB['title']}</div>
          <div>{JOB['detail']}{_steps} <span class="y-badge">{_el // 60:02d}:{_el % 60:02d}</span></div>
          <div style="height:10px;background:#ece8fb;border-radius:99px;overflow:hidden;margin:10px 0 6px"><div style="height:100%;width:{_pct}%;background:linear-gradient(90deg,#5b3fd1,#a48bff)"></div></div>
          <div class="y-muted">کار در پس‌زمینه ادامه دارد؛ هر قدمِ تمام‌شده ذخیره می‌شود.</div>
        </div></div>""")
    elif JOB.get("error"):
        _status = mo.callout(mo.vstack([
            mo.md(f"**❌ خطا در «{JOB['title']}»:** {JOB['error']}"),
            mo.accordion({"جزئیات فنی (برای فرستادن)": mo.md(f"```\n{JOB.get('trace', '')}\n```")}),
        ]), kind="danger")
    elif JOB.get("message"):
        _status = mo.callout(mo.md(JOB["message"]), kind="success")
    else:
        _status = mo.md("")
    mo.vstack([H('<div class="y-root" style="display:flex;justify-content:flex-start">' + ticker.text + "</div>"),
               _status], gap=0.4)
    return


@app.cell(hide_code=True)
def _(DEFAULT_SFX, REAL_STYLES, STYLES, hashlib):
    # ───────────── پرامپت‌ها ─────────────
    REAL = ("Photorealistic live-action movie still, real actors, real practical costumes, realistic skin, real "
            "locations. Not an illustration, not a painting, not 3D animation, not a video game render.")

    def image_prompt(scene, idx, cast, chars, story, style, ref_desc, with_scene):
        _p = [STYLES[style] + "."]
        if style in REAL_STYLES:
            _p.append(REAL)
        if with_scene:
            _p.append("Image 1 is a frame from the first scene of this same film: keep the same location, weather, "
                      "lighting, color grade, costumes and weapons.")
        _p.append(ref_desc)
        _p.append(("Create the next shot of the same film from a new cinematic camera angle: " if with_scene
                   else "Create one widescreen cinematic film frame: ")
                  + (story.strip().rstrip(".") + ". " if story.strip() else "") + scene.strip().rstrip(".") + ".")
        for _n in cast:
            if chars[_n].get("role"):
                _p.append(f"{_n}: {chars[_n]['role'].rstrip('.')}.")
        _p.append("Each character's face, body, hair, costume and weapons must be exactly identical to their reference "
                  "photo; each character holds only the weapons shown in their own photo. Characters clearly visible, "
                  "sharp focus, no text, no watermark.")
        return " ".join(_p)

    def video_prompt(scene, cast, chars, story, style, sfx):
        _p = [STYLES[style] + "."]
        if style in REAL_STYLES:
            _p.append(REAL)
        if story.strip():
            _p.append(story.strip().rstrip(".") + ".")
        for _n in cast:
            _c = chars[_n]
            if _c.get("look"):
                _p.append(f"{_n} is {_c['look'].rstrip('.')}.")
            if _c.get("role"):
                _p.append(f"{_n}: {_c['role'].rstrip('.')}.")
        _p.append("Every character keeps exactly the same face, body, costume and weapons as in the opening frame "
                  "throughout the shot.")
        _p.append(scene.strip().rstrip(".") + ".")
        _p.append("Audio: " + (sfx.strip() or DEFAULT_SFX).rstrip(".") + ".")
        return " ".join(_p)

    def hkey(*parts):
        return hashlib.sha1("|".join(str(p) for p in parts).encode("utf-8")).hexdigest()[:16]
    return hkey, image_prompt, video_prompt


@app.cell(hide_code=True)
def _(LOCK, PROJECT, absp, hkey, image_prompt, save_project, video_prompt):
    def sync_scenes(lines, cast, story, style, sfx, aspect):
        """فهرست صحنه‌ها با متن فعلی هماهنگ می‌شود؛ فقط صحنه‌هایی که چیزی‌شان عوض شده دوباره ساخته می‌شوند"""
        _chars = PROJECT["chars"]
        _refs = [str(absp(_chars[n]["image"])) for n in cast]
        _old = {s.get("ikey"): s for s in PROJECT["scenes"]}
        _new = []
        _first_key = None
        for _i, _line in enumerate(lines):
            _ip = image_prompt(_line, _i + 1, cast, _chars, story, style, "{refs}", _i > 0)
            # تصویر هر صحنه به صحنه‌ی ۱ وابسته است (مکان یکسان)
            _ik = hkey(_ip, _refs, aspect, _first_key if _i > 0 else "")
            if _i == 0:
                _first_key = _ik
            _vp = video_prompt(_line, cast, _chars, story, style, sfx)
            _s = dict(_old.get(_ik) or {"ikey": _ik, "image": None, "embeds": None, "video": None})
            _s["text"] = _line
            if _s.get("vprompt") != _vp:
                _s.update(vprompt=_vp, embeds=None, video=None)
            _new.append(_s)
        with LOCK:
            PROJECT["scenes"] = _new
            PROJECT["final"] = None
        save_project()
        return _new
    return (sync_scenes,)


@app.cell(hide_code=True)
def _(
    EDIT_SIZE, JOB, LOCK, NEG_ANY, NEG_REAL, OUT, PROJECT, REAL_STYLES, absp, aspect_dd, cast_ms, cast_refs,
    engine, hf_token, image_prompt, img_btn, mo, random, rel, save_project, scenes_in, seed_in, sfx_in, start_job,
    story_in, style_dd, sync_scenes, time, use_token, Image,
):
    # ───────────── مرحله‌ی ۱: تصویر صحنه‌ها ─────────────
    mo.stop(not img_btn.value)
    _lines = [l.strip() for l in scenes_in.value.splitlines() if l.strip()][:12]
    _cast = [n for n in cast_ms.value if n in PROJECT["chars"]]
    if not _cast:
        JOB.update(error=None, title="", message="⚠️ در تب «📖 داستان» حداقل یک شخصیت انتخاب کنید.")
        JOB["version"] += 1
    elif not _lines:
        JOB.update(error=None, title="", message="⚠️ صحنه‌ها را بنویسید (هر خط یک صحنه).")
        JOB["version"] += 1
    else:
        def _launch(lines, cast, cfg):
            _scenes = sync_scenes(lines, cast, cfg["story"], cfg["style"], cfg["sfx"], cfg["aspect"])
            _chars = PROJECT["chars"]
            _cast_t = [(n, str(absp(_chars[n]["image"])), _chars[n].get("look", "")) for n in cast]
            _neg = NEG_REAL if cfg["style"] in REAL_STYLES else NEG_ANY
            _h, _w = EDIT_SIZE[cfg["aspect"]]

            def _work():
                engine.job = JOB
                use_token(cfg["token"])
                _todo = [s for s in _scenes if not s.get("image")]
                if not _todo:
                    return "✅ تصویر همه‌ی صحنه‌ها آماده است. حالا «🎬 ساخت ویدیوها» را بزنید."
                engine.load_edit(cfg["token"])
                for _j, _s in enumerate(_todo):
                    if JOB["stop"]:
                        return "⏹ متوقف شد. هر وقت خواستید دوباره دکمه را بزنید."
                    _i = _scenes.index(_s)
                    JOB["title"] = f"مرحله‌ی ۱ — تصویر صحنه‌ی {_i + 1} ({_j + 1} از {len(_todo)})"
                    _seed = cfg["seed"] if cfg["seed"] >= 0 else random.randint(0, 2**31 - 1)
                    if _i == 0 or not _scenes[0].get("image"):
                        _imgs, _rd = cast_refs(_cast_t, 1, 3)
                        _p = image_prompt(_s["text"], _i + 1, cast, _chars, cfg["story"], cfg["style"], _rd, False)
                    else:
                        _imgs, _rd = cast_refs(_cast_t, 2, 2)
                        _first = Image.open(absp(_scenes[0]["image"])).convert("RGB")
                        _imgs = [_first] + _imgs
                        _p = image_prompt(_s["text"], _i + 1, cast, _chars, cfg["story"], cfg["style"], _rd, True)
                    _img = engine.edit(_imgs, _p, _h, _w, _seed, _neg)
                    _f = OUT / "keyframes" / f"scene_{_i + 1:02d}_{int(time.time())}.png"
                    _img.save(_f)
                    with LOCK:
                        _s.update(image=rel(_f), video=None)
                    save_project()
                    JOB["version"] += 1
                return ("✅ تصویر صحنه‌ها آماده شد. نگاهشان کنید: هر کدام بد بود «🖼 تصویر تازه» بزنید؛ "
                        "اگر همه خوب‌اند «🎬 ساخت ویدیوها و فیلم نهایی» را بزنید.")

            if not start_job("مرحله‌ی ۱ — تصویر صحنه‌ها", _work):
                JOB["message"] = "⏳ یک کار دیگر در حال انجام است."
                JOB["version"] += 1

        _launch(_lines, _cast, {
            "story": story_in.value, "style": style_dd.value, "sfx": sfx_in.value, "aspect": aspect_dd.value,
            "seed": int(seed_in.value if seed_in.value is not None else -1), "token": hf_token.value.strip(),
        })
    return


@app.cell(hide_code=True)
def _(
    JOB, LOCK, OUT, PROJECT, QUALITY, SECONDS, LTX_ID, EDIT_ID, Image, absp, aspect_dd, clear, concat,
    disk_free_gb, drop_cached, engine, hf_token, mo, quality_dd, random, rel, save_project, sec_dd, seed_in,
    start_job, time, torch, use_token, vid_btn,
):
    # ───────────── مرحله‌ی ۲ و ۳: خواندن پرامپت‌ها ← ساخت ویدیوها ← فیلم نهایی ─────────────
    mo.stop(not vid_btn.value)
    _scenes0 = PROJECT["scenes"]
    if not _scenes0:
        JOB.update(error=None, title="", message="⚠️ اول «🖼 ساخت تصویر صحنه‌ها» را بزنید.")
        JOB["version"] += 1
    elif any(not s.get("image") for s in _scenes0):
        JOB.update(error=None, title="", message="⚠️ بعضی صحنه‌ها هنوز تصویر ندارند؛ اول «🖼 ساخت تصویر صحنه‌ها» را بزنید.")
        JOB["version"] += 1
    else:
        def _launch(scenes, cfg):
            def _work():
                engine.job = JOB
                use_token(cfg["token"])
                _t0 = time.time()
                # ── مرحله‌ی ۲: خواندن پرامپت همه‌ی صحنه‌ها (فقط مدل متن روی GPU)
                _read = [s for s in scenes if not s.get("video") and not s.get("embeds")]
                if _read:
                    JOB["title"] = "مرحله‌ی ۲ — خواندن پرامپت صحنه‌ها"
                    engine.load_reader(cfg["token"])
                    for _j, _s in enumerate(_read):
                        engine.say(f"خواندن صحنه‌ی {scenes.index(_s) + 1}", _j, len(_read))
                        _e = engine.read(_s["vprompt"])
                        _p = OUT / "embeds" / f"{_s['ikey']}_{int(time.time())}.pt"
                        torch.save(_e, _p)
                        with LOCK:
                            _s["embeds"] = rel(_p)
                        save_project()
                    engine.free()
                # ── مرحله‌ی ۳: ساخت ویدیوها (فقط مدل ویدیو روی GPU)
                _make = [s for s in scenes if not s.get("video")]
                if _make:
                    if 0 <= disk_free_gb() < 60:
                        engine.say("دیسک کم است؛ پاک کردن فایل‌های مدل تصویر…")
                        drop_cached(EDIT_ID)
                    JOB["title"] = "مرحله‌ی ۳ — ساخت ویدیوها"
                    engine.load_maker(cfg["token"])
                    for _j, _s in enumerate(_make):
                        if JOB["stop"]:
                            return "⏹ متوقف شد. صحنه‌های ساخته‌شده ذخیره‌اند؛ دوباره دکمه را بزنید تا ادامه دهد."
                        _i = scenes.index(_s)
                        JOB["title"] = f"مرحله‌ی ۳ — ویدیوی صحنه‌ی {_i + 1} ({_j + 1} از {len(_make)})"
                        _e = torch.load(absp(_s["embeds"]), weights_only=False)
                        _img = Image.open(absp(_s["image"])).convert("RGB")
                        _seed = cfg["seed"] if cfg["seed"] >= 0 else random.randint(0, 2**31 - 1)
                        _vp = OUT / "scenes" / f"scene_{_i + 1:02d}_{int(time.time())}.mp4"
                        try:
                            engine.make(_img, _e, cfg["nf"], cfg["stage1"], _seed, _vp)
                        except Exception as _err:
                            if "out of memory" not in str(_err).lower() or cfg["stage1"] == cfg["stage1_720"]:
                                raise
                            clear()
                            engine.say(f"صحنه‌ی {_i + 1}: حافظه برای 1080p کم بود؛ ساخت با 720p")
                            engine.make(_img, _e, cfg["nf"], cfg["stage1_720"], _seed, _vp)
                        with LOCK:
                            _s.update(video=rel(_vp), seed=_seed)
                        save_project()
                        JOB["version"] += 1
                # ── فیلم نهایی
                JOB["title"] = "فیلم نهایی"
                engine.say("چسباندن صحنه‌ها…", 0, 0)
                _out = concat([absp(s["video"]) for s in scenes], OUT / "final" / f"film_{int(time.time())}.mp4",
                              cfg["out_hw"])
                with LOCK:
                    PROJECT["final"] = rel(_out)
                save_project()
                return f"✅ فیلم آماده شد: {len(scenes)} صحنه، حدود {int((time.time() - _t0) / 60)} دقیقه."

            if not start_job("مرحله‌ی ۲ و ۳ — ویدیوها", _work):
                JOB["message"] = "⏳ یک کار دیگر در حال انجام است."
                JOB["version"] += 1

        _q = QUALITY[quality_dd.value][aspect_dd.value]
        _launch(list(_scenes0), {
            "nf": SECONDS[sec_dd.value], "stage1": _q[0], "out_hw": _q[1],
            "stage1_720": QUALITY["720p"][aspect_dd.value][0],
            "seed": int(seed_in.value if seed_in.value is not None else -1), "token": hf_token.value.strip(),
        })
    return


@app.cell(hide_code=True)
def _(JOB, mo, stop_btn):
    mo.stop(not stop_btn.value)
    if JOB["running"]:
        JOB["stop"] = True
        JOB["message"] = "⏹ بعد از تمام شدن صحنه‌ی فعلی متوقف می‌شود."
    JOB["version"] += 1
    return


@app.cell(hide_code=True)
def _(JOB, LOCK, PROJECT, mo, redo_dd, redo_img_btn, redo_vid_btn, save_project):
    mo.stop(not (redo_img_btn.value or redo_vid_btn.value))
    if JOB["running"]:
        JOB["message"] = "⏳ صبر کنید تا کار فعلی تمام شود."
    else:
        try:
            _i = int(redo_dd.value.split()[-1]) - 1
            _s = PROJECT["scenes"][_i]
            with LOCK:
                if redo_img_btn.value:
                    _s.update(image=None, video=None)
                    _msg = f"🖼 تصویر صحنه‌ی {_i + 1} پاک شد؛ «🖼 ساخت تصویر صحنه‌ها» تصویر تازه می‌سازد."
                else:
                    _s.update(video=None)
                    _msg = f"🎬 ویدیوی صحنه‌ی {_i + 1} پاک شد؛ «🎬 ساخت ویدیوها» آن را دوباره می‌سازد."
                PROJECT["final"] = None
            save_project()
            JOB.update(error=None, title="", message=_msg)
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
        JOB.update(error=None, title="", message="🗑 صحنه‌ها پاک شدند. (فیلم‌های قبلی در پوشه‌ی final می‌مانند.)")
    JOB["version"] += 1
    return


@app.cell(hide_code=True)
def _(JOB, LOCK, OUT, PROJECT, QUALITY, absp, aspect_dd, concat, merge_btn, mo, quality_dd, rel, save_project,
      start_job, time):
    mo.stop(not merge_btn.value)
    _done = [s for s in PROJECT["scenes"] if s.get("video")]
    if not _done:
        JOB.update(error=None, title="", message="⚠️ هنوز ویدیویی ساخته نشده.")
        JOB["version"] += 1
    else:
        def _launch(done, out_hw):
            def _work():
                JOB["detail"] = "چسباندن صحنه‌ها…"
                _out = concat([absp(s["video"]) for s in done], OUT / "final" / f"film_{int(time.time())}.mp4", out_hw)
                with LOCK:
                    PROJECT["final"] = rel(_out)
                save_project()
                return f"✅ فیلم از {len(done)} صحنه ساخته شد."

            if not start_job("فیلم نهایی", _work):
                JOB["message"] = "⏳ یک کار دیگر در حال انجام است."
                JOB["version"] += 1
        _launch(_done, QUALITY[quality_dd.value][aspect_dd.value][1])
    return


@app.cell(hide_code=True)
def _(
    JOB, LOCK, OUT, PROJECT, char_add, char_look, char_name, char_role, char_upload, mo, re, rel, save_project,
    time,
):
    mo.stop(not char_add.value)
    _name = re.sub(r"\s+", " ", char_name.value.strip())
    if not _name:
        JOB.update(error=None, title="", message="⚠️ نام شخصیت را بنویسید.")
    elif not char_upload.value:
        JOB.update(error=None, title="", message="⚠️ یک عکس برای شخصیت انتخاب کنید.")
    else:
        _dst = OUT / "characters" / f"{int(time.time())}_{re.sub(r'[^A-Za-z0-9]+', '_', _name)}.png"
        _dst.write_bytes(char_upload.contents(0))
        with LOCK:
            PROJECT["chars"][_name] = {"image": rel(_dst), "look": char_look.value.strip(),
                                       "role": char_role.value.strip()}
        save_project()
        JOB.update(error=None, title="", message=f"✅ شخصیت «{_name}» ذخیره شد.")
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
def _(JOB, LOCK, OUT, PROJECT, backup_btn, mo, rel, save_project, start_job, time, zipfile):
    mo.stop(not backup_btn.value)

    def _work():
        JOB["detail"] = "ساخت فایل پشتیبان…"
        _zp = OUT / "backups" / f"yar_studio_backup_{time.strftime('%Y%m%d_%H%M%S')}.zip"
        with zipfile.ZipFile(_zp, "w", zipfile.ZIP_STORED) as _z:
            _z.writestr("project.json", (OUT / "project.json").read_text(encoding="utf-8"))
            for _sub in ("characters", "keyframes", "scenes", "final"):
                for _f in (OUT / _sub).glob("*"):
                    _z.write(_f, f"{_sub}/{_f.name}")
        with LOCK:
            PROJECT["backup"] = rel(_zp)
        save_project()
        return "✅ فایل پشتیبان آماده است؛ در تب «⚙️ تنظیمات» دانلودش کنید."

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
                if _m != "project.json" and not _m.endswith("/") and ".." not in _m:
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
        JOB.update(error=None, title="", message="♻️ پروژه برگشت. برای دیدن متن‌ها یک‌بار Run all بزنید.")
    JOB["version"] += 1
    return


@app.cell(hide_code=True)
def _(H, PROJECT, absp, get_rev, mo):
    # ───────────── نمای شخصیت‌ها و صحنه‌ها ─────────────
    get_rev()
    _chars = PROJECT["chars"]

    def _char_card(n, c):
        return mo.vstack([
            mo.image(src=str(absp(c["image"])), width=170, height=230, rounded=True, style={"object-fit": "contain",
                                                                                           "background": "#f4f2fa"}),
            H(f'<div class="y-root" style="max-width:170px"><b>{n}</b>'
              f'<div class="y-muted y-ltr" style="font-size:12px">{(c.get("role") or c.get("look") or "")[:90]}</div></div>'),
        ], gap=0.3)

    chars_view = (mo.hstack([_char_card(n, c) for n, c in _chars.items()], wrap=True, justify="start", gap=1.2)
                  if _chars else H('<div class="y-empty">هنوز شخصیتی نیست — از فرم کنار، اولین شخصیت را بسازید.</div>'))

    def _video(path, label):
        _p = absp(path)
        return mo.vstack([
            mo.video(src=str(_p), controls=True, width="100%"),
            mo.download(data=lambda _p=_p: _p.read_bytes(), filename=_p.name, mimetype="video/mp4", label=label),
        ], gap=0.3)

    _cards = []
    for _i, _s in enumerate(PROJECT["scenes"], start=1):
        if _s.get("video"):
            _b = '<span class="y-ok">✅ ویدیو آماده</span>'
        elif _s.get("image"):
            _b = '<span class="y-badge">🖼 تصویر آماده</span>'
        else:
            _b = '<span class="y-wait">⏳ در صف</span>'
        _body = [H(f'<div class="y-root"><b>صحنه {_i}</b> {_b}'
                   f'<div class="y-muted y-ltr" style="margin-top:4px">{_s["text"]}</div></div>')]
        if _s.get("video"):
            _body.append(_video(_s["video"], "⬇️ دانلود صحنه"))
        elif _s.get("image"):
            _body.append(mo.image(src=str(absp(_s["image"])), width="100%", rounded=True))
        _cards.append(H('<div class="y-scene">' + mo.vstack(_body, gap=0.5).text + "</div>"))
    _rows = [mo.hstack(_cards[k:k + 2], widths="equal", gap=1, align="start") for k in range(0, len(_cards), 2)]
    scenes_view = (mo.vstack(_rows, gap=1) if _rows else
                   H('<div class="y-empty">هنوز صحنه‌ای ساخته نشده — در تب «📖 داستان» صحنه‌ها را بنویسید و '
                     '«🖼 ساخت تصویر صحنه‌ها» را بزنید.</div>'))
    final_view = (_video(PROJECT["final"], "⬇️ دانلود فیلم نهایی") if PROJECT.get("final") else None)
    if PROJECT.get("backup"):
        _bp = absp(PROJECT["backup"])
        backup_view = mo.download(data=lambda: _bp.read_bytes(), filename=_bp.name, mimetype="application/zip",
                                  label=f"⬇️ دانلود {_bp.name}")
    else:
        backup_view = mo.md("")
    return backup_view, chars_view, final_view, scenes_view


@app.cell(hide_code=True)
def _(
    F, H, R, aspect_dd, backup_btn, backup_view, card, cast_ms, char_add, char_del_btn, char_del_dd, char_look,
    char_name, char_role, char_upload, chars_view, final_view, hf_token, img_btn, merge_btn, mo, quality_dd,
    redo_dd, redo_img_btn, redo_vid_btn, reset_btn, restore_btn, restore_file, scenes_in, scenes_view, sec,
    sec_dd, seed_in, sfx_in, stop_btn, story_in, style_dd, vid_btn,
):
    # ───────────── چیدمان صفحه ─────────────
    _tab_chars = mo.hstack([
        mo.vstack([card(sec("👥 شخصیت‌ها"), chars_view),
                   card(sec("🗑 حذف شخصیت"), R(mo.hstack([char_del_dd, char_del_btn], justify="start", gap=1)))],
                  gap=1),
        card(sec("➕ شخصیت جدید", "بهترین عکس: تمام‌قد، از جلو، با لباس و سلاح خودش. عکس بدون پس‌زمینه هم خوب است."),
             F("نام (انگلیسی)", char_name), R(char_upload), F("ظاهر (انگلیسی)", char_look),
             F("سلاح، توانایی و نقش (انگلیسی — اختیاری)", char_role), R(char_add)),
    ], widths=[1.4, 1], gap=1.5, align="start")

    _tab_story = mo.hstack([
        mo.vstack([
            card(sec("شخصیت‌ها", "ترتیب انتخاب مهم نیست؛ حداکثر ۴ نفر.", step="۱"), R(cast_ms)),
            card(sec("داستان", "متن‌ها انگلیسی باشند. هر خطِ «صحنه‌ها» یک صحنه است.", step="۲"),
                 F("فضای داستان — مکان، زمان و حال‌وهوا (در همه‌ی صحنه‌ها استفاده می‌شود)", story_in),
                 F("صحنه‌ها — هر خط یک صحنه", scenes_in),
                 F("صدا و موسیقی (خالی = موسیقی سینمایی + صداهای واقعی)", sfx_in)),
        ], gap=1),
        card(sec("تنظیمات فیلم", step="۳"),
             R(style_dd), R(mo.hstack([aspect_dd, quality_dd], justify="start", gap=1, wrap=True)), R(sec_dd),
             H('<div class="y-root y-muted">720p مطمئن‌ترین است. 1080p اگر حافظه کم بیاید، خودش به 720p برمی‌گردد. '
               'هر صحنه با تصویر خودش شروع می‌شود و صحنه‌ها مثل فیلم سینمایی به هم کات می‌خورند.</div>')),
    ], widths=[1.4, 1], gap=1.5, align="start")

    _steps = card(
        sec("ساخت فیلم در دو قدم"),
        H('<div class="y-root y-muted"><b>قدم ۱:</b> تصویر شروع هر صحنه ساخته می‌شود (با چهره‌ی شخصیت‌ها). '
          'نگاهشان کنید؛ هر کدام بد بود «🖼 تصویر تازه». <br><b>قدم ۲:</b> ویدیوی همه‌ی صحنه‌ها و فیلم نهایی. '
          'اگر وسط کار قطع شد، همان دکمه را دوباره بزنید؛ از همان‌جا ادامه می‌دهد.</div>'),
        R(mo.hstack([img_btn, vid_btn], justify="start", gap=1, wrap=True)),
        R(mo.hstack([stop_btn, merge_btn, reset_btn], justify="start", gap=1, wrap=True)),
    )
    _redo = card(sec("🔁 درست کردن یک صحنه"),
                 R(mo.hstack([redo_dd, redo_img_btn, redo_vid_btn], justify="start", gap=1, wrap=True)))
    _final = card(sec("🏁 فیلم نهایی"), final_view) if final_view is not None else mo.md("")
    _tab_make = mo.hstack([
        mo.vstack([_final, card(sec("🎞 صحنه‌ها"), scenes_view)], gap=1),
        mo.vstack([_steps, _redo], gap=1),
    ], widths=[1.6, 1], gap=1.5, align="start")

    _tab_set = mo.hstack([
        card(sec("🔑 توکن Hugging Face"), F("توکن", hf_token),
             H('<div class="y-root y-muted">یک‌بار در صفحه‌ی مدل‌های <span class="y-ltr">Lightricks/LTX-2.5-Diffusers</span> '
               'و <span class="y-ltr">Qwen/Qwen-Image-Edit-2511</span> شرایط را قبول کنید. می‌توانید در پنل '
               '<b>Files</b> فایلی به اسم <code>.env</code> بسازید با متن <code class="y-ltr">HF_TOKEN=hf_...</code> '
               'تا هر بار لازم نباشد.</div>'),
             R(seed_in)),
        card(sec("💾 پشتیبان", "molab فایل‌ها را بعد از خاموش شدن نگه نمی‌دارد. قبل از بستن، پشتیبان بگیرید."),
             R(backup_btn), backup_view, R(restore_file), R(restore_btn)),
    ], widths=[1, 1], gap=1.5, align="start")

    mo.ui.tabs({"🎬 ساخت": _tab_make, "📖 داستان": _tab_story, "👤 شخصیت‌ها": _tab_chars, "⚙️ تنظیمات": _tab_set})
    return


if __name__ == "__main__":
    app.run()
