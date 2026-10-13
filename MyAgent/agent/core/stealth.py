# -*- coding: utf-8 -*-
"""ParsAgent Stealth v2 — ضد شناسایی بات با آخرین متدها (۲۰۲۵)
================================================================

سه لایهٔ دفاعی:

  ۱) آرگومان‌های لانچ:
     --disable-blink-features=AutomationControlled   ← پرچم navigator.webdriver
     ignore_default_args=["--enable-automation"]      ← نوار «کنترل خودکار توسط...»
     (در browser_engine.py اعمال می‌شود)

  ۲) تزریق init-script در «هر فریم» (کانتکست، نه صفحه):
     حذف navigator.webdriver، ساخت window.chrome واقعی، پلاگین‌های PDF،
     Permissions API سازگار، زبان/پلتفرم، نویز اثر انگشت Canvas و AudioContext،
     ماسک WebGL (رندرر ANGLE واقع‌نما)، مشخصات سخت‌افزار، محافظ WebRTC.

  ۳) رفتار انسانی (engine): تایپ حرف‌به‌حرف با تأخیر تصادفی + مکث بین گام‌ها.

نکتهٔ مهم پایداری: مقدار «نویز» و GPU با seed مشتق از «نام پروفایل» ساخته
می‌شود — یعنی اثر انگشت هر پروفایل در همهٔ اجراها یکسان می‌ماند (پایدار)،
اما بین پروفایل‌ها یکتا است. این دقیقاً همان رفتار یک سیستم واقعی است.

قابل تنظیم در config.json:

  "stealth": {
    "enabled": true,
    "level": "standard",
    "modules": { "webdriver": true, "chrome_runtime": true, ... },
    "disable_for": []          ← پلتفرم‌هایی که استثنا می‌شوند
  }

سطح‌ها (preset — فقط در پنل استفاده می‌شوند، موتور فقط modules را می‌خواند):
  basic    → webdriver, chrome_runtime, permissions
  standard → + plugins, languages_platform, hw_specs, canvas_noise, audio_noise, webgl_mask
  max      → + webrtc_shield (برای استفاده با پروکسی)
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

# --------------------------------------------------------------------------- #
# کاتالوگ ماژول‌ها (کلید → (نام فارسی، سطح پیش‌فرض))
# --------------------------------------------------------------------------- #
MODULES: Dict[str, Dict[str, Any]] = {
    "webdriver": {
        "fa": "حذف navigator.webdriver",
        "desc": "قوی‌ترین نشانهٔ اتوماسیون؛ همراه با پرچم AutomationControlled غیرفعال می‌شود",
        "levels": ["basic", "standard", "max"],
    },
    "chrome_runtime": {
        "fa": "اشیای chrome.runtime / app / csi",
        "desc": "سایت‌ها نبودِ window.chrome (نشانهٔ کرومیوم هدلس) را چک می‌کنند",
        "levels": ["basic", "standard", "max"],
    },
    "permissions": {
        "fa": "Permissions API سازگار",
        "desc": "پرس‌وجوی Notification دقیقاً مثل مرورگر واقعی جواب می‌دهد",
        "levels": ["basic", "standard", "max"],
    },
    "plugins": {
        "fa": "پلاگین‌های واقعی (PDF Viewer)",
        "desc": "مرورگر هدلس ۰ پلاگین دارد — اینستاگرام/فیسبوک این را می‌سنجند",
        "levels": ["standard", "max"],
    },
    "languages_platform": {
        "fa": "زبان و پلتفرم سیستم",
        "desc": "fa-IR و Win32 به‌جای مقادیر خالی/ناسازگار",
        "levels": ["standard", "max"],
    },
    "hw_specs": {
        "fa": "مشخصات سخت‌افزار واقع‌نما",
        "desc": "تعداد هستهٔ CPU و deviceMemory به مقدار طبیعی سیستم",
        "levels": ["standard", "max"],
    },
    "canvas_noise": {
        "fa": "نویز اثر انگشت Canvas",
        "desc": "هر پروفایل امضای یکتا و «پایدار» می‌گیرد (LSB نامرئی)",
        "levels": ["standard", "max"],
    },
    "audio_noise": {
        "fa": "نویز AudioContext",
        "desc": "اثر انگشت صوتی با نویز نامحسوس و پایدار",
        "levels": ["standard", "max"],
    },
    "webgl_mask": {
        "fa": "ماسک GPU در WebGL",
        "desc": "رندرر ANGLE واقع‌نما (Intel/NVIDIA/AMD) به‌جای SwiftShader/llvmpipe",
        "levels": ["standard", "max"],
    },
    "webrtc_shield": {
        "fa": "غیرفعال‌سازی WebRTC",
        "desc": "جلوی لو رفتن IP واقعی هنگام پروکسی — بدون پروکسی لازم نیست",
        "levels": ["max"],
    },
}

LEVEL_PRESETS: Dict[str, List[str]] = {
    "basic": ["webdriver", "chrome_runtime", "permissions"],
    "standard": ["webdriver", "chrome_runtime", "permissions", "plugins",
                 "languages_platform", "hw_specs", "canvas_noise", "audio_noise",
                 "webgl_mask"],
    "max": list(MODULES.keys()),
}

# --------------------------------------------------------------------------- #
# GPUهای واقع‌نمای ANGLE ویندوز (برای ماسک WebGL)
# --------------------------------------------------------------------------- #
WEBGL_GPUS = [
    ("Google Inc. (Intel)",
     "ANGLE (Intel, Intel(R) UHD Graphics 620 (0x00003EA0) Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Google Inc. (Intel)",
     "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics (0x00009A49) Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Google Inc. (NVIDIA)",
     "ANGLE (NVIDIA, NVIDIA GeForce GTX 1650 (0x00001F82) Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Google Inc. (NVIDIA)",
     "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 (0x00002503) Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Google Inc. (AMD)",
     "ANGLE (AMD, AMD Radeon(TM) Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)"),
]


def _stable_seed(name: str) -> int:
    """Seed پایدار برای هر پروفایل — اثر انگشت بین اجراها ثابت می‌ماند."""
    h = 2166136261
    for ch in str(name or "main"):
        h = ((h ^ ord(ch)) * 16777619) & 0xFFFFFFFF
    return h


def _plausible_cores() -> int:
    try:
        c = os.cpu_count() or 8
    except Exception:
        c = 8
    return max(4, min(c, 16))


def resolve_modules(stealth_cfg: Dict[str, Any],
                    browser_cfg: Dict[str, Any] | None = None) -> Dict[str, bool]:
    """ماژول‌های فعال نهایی را حساب می‌کند (سطح + ماژول‌های دستی + پروکسی)."""
    cfg = stealth_cfg or {}
    if not cfg.get("enabled", True):
        return {k: False for k in MODULES}
    mods = {k: False for k in MODULES}
    level = str(cfg.get("level", "standard"))
    for k in LEVEL_PRESETS.get(level, LEVEL_PRESETS["standard"]):
        mods[k] = True
    # بازنویسی دستی
    for k, v in (cfg.get("modules") or {}).items():
        if k in mods:
            mods[k] = bool(v)
    # با پروکسی، جلوی نشت IP را خودکار می‌گیریم مگر اینکه کاربر صریحاً خاموش کرده باشد
    if browser_cfg and browser_cfg.get("proxy"):
        mods.setdefault("webrtc_shield", True)
        if (cfg.get("modules") or {}).get("webrtc_shield") is not False:
            mods["webrtc_shield"] = True
    return mods


def stealth_launch_args(mods: Dict[str, bool]) -> List[str]:
    """آرگومان‌های کرومیوم — بخشی از لایهٔ ضد شناسایی."""
    args = ["--no-first-run", "--no-default-browser-check", "--start-maximized"]
    if mods.get("webdriver", True):
        args.insert(0, "--disable-blink-features=AutomationControlled")
    return args


# --------------------------------------------------------------------------- #
# اسکریپت‌های JS هر ماژول
# --------------------------------------------------------------------------- #
_JS_WEBDRIVER = """
try{ Object.defineProperty(navigator,'webdriver',{get:()=>undefined,configurable:true}); }catch(e){}
"""

_JS_CHROME_RUNTIME = """
try{
  if(!window.chrome || !window.chrome.runtime){
    window.chrome = {
      app:{ isInstalled:false,
            InstallState:{DISABLED:'disabled',INSTALLED:'installed',NOT_INSTALLED:'not_installed'},
            RunningState:{CANNOT_RUN:'cannot_run',READY_TO_RUN:'ready_to_run',RUNNING:'running'},
            getDetails:function(){return null}, getIsInstalled:function(){return false} },
      runtime:{ PlatformOs:{ANDROID:'android',CROS:'cros',LINUX:'linux',MAC:'mac',OPENBSD:'openbsd',WIN:'win'},
                OnInstalledReason:{CHROME_UPDATE:'chrome_update',INSTALL:'install',UPDATE:'update'},
                RequestUpdateCheckStatus:{NO_UPDATE:'no_update',THROTTLED:'throttled',UPDATE_AVAILABLE:'update_available'},
                connect:function(){}, sendMessage:function(){} },
      csi:function(){return {startE:Date.now()-3E4,pageT:Date.now()%6E4,tran:15}},
      loadTimes:function(){return {commitLoadTime:Date.now()/1E3,finishDocumentLoadTime:Date.now()/1E3,
        finishLoadTime:Date.now()/1E3,firstPaintAfterLoadTime:0,firstPaintTime:Date.now()/1E3,
        navigationType:'Other',npnNegotiatedProtocol:'unknown',requestTime:Date.now()/1E3,startLoadTime:Date.now()/1E3,
        wasAlternateProtocolAvailable:false,wasFetchedViaSpdy:false,wasNpnNegotiated:false}}
    };
  }
}catch(e){}
"""

_JS_PERMISSIONS = """
try{
  if(navigator.permissions && navigator.permissions.query){
    const _origQ = navigator.permissions.query.bind(navigator.permissions);
    navigator.permissions.query = (p) => {
      if(p && (p.name==='notifications')){
        const st = (typeof Notification!=='undefined' && Notification.permission) ? Notification.permission : 'denied';
        return Promise.resolve({state: st==='default'?'denied':st, name:'notifications',
                                onchange:null, addEventListener:function(){}, removeEventListener:function(){},
                                dispatchEvent:function(){return false}});
      }
      return _origQ(p);
    };
  }
}catch(e){}
"""

_JS_PLUGINS = """
try{
  if(navigator.plugins && navigator.plugins.length===0){
    function _mime(desc){ return {type:'application/pdf', suffixes:'pdf', description:desc,
                                  enabledPlugin:null}; }
    function _plugin(name, desc){
      const m = _mime(desc); m.enabledPlugin = null;
      return { name:name, filename:'internal-' + name.toLowerCase().replace(/\\s+/g,'-') + '.pdf',
               description:desc, length:1, 0:m,
               item:function(i){return i===0?m:null}, namedItem:function(n){return n==='application/pdf'?m:null} };
    }
    const _p = [
      _plugin('PDF Viewer','Portable Document Format'),
      _plugin('Chrome PDF Viewer','Portable Document Format'),
      _plugin('Chromium PDF Viewer','Portable Document Format'),
      _plugin('Microsoft Edge PDF Viewer','Portable Document Format'),
      _plugin('WebKit built-in PDF','Portable Document Format'),
    ];
    _p.item = function(i){return _p[i]||null};
    _p.namedItem = function(n){for(let i=0;i<_p.length;i++){if(_p[i].name===n)return _p[i];}return null};
    _p.refresh = function(){};
    Object.defineProperty(navigator,'plugins',{get:()=>_p,configurable:true});
    const _m = _p.map(function(p){return p[0];});
    _m.item = function(i){return _m[i]||null};
    _m.namedItem = function(n){for(let i=0;i<_m.length;i++){if(_m[i].type===n)return _m[i];}return null};
    Object.defineProperty(navigator,'mimeTypes',{get:()=>_m,configurable:true});
    Object.defineProperty(navigator,'pdfViewerEnabled',{get:()=>true,configurable:true});
  }
}catch(e){}
"""

_JS_LANG_PLATFORM = """
try{
  Object.defineProperty(navigator,'languages',{get:()=>['fa-IR','fa','en-US','en'],configurable:true});
  Object.defineProperty(navigator,'platform',{get:()=>'Win32',configurable:true});
}catch(e){}
"""

_JS_HW = """
try{
  Object.defineProperty(navigator,'hardwareConcurrency',{get:()=>__CORES__,configurable:true});
  try{ Object.defineProperty(navigator,'deviceMemory',{get:()=>8,configurable:true}); }catch(e){}
}catch(e){}
"""

_JS_CANVAS = """
try{
  const SEED=__SEED__;
  function _rnd(i){
    let x=(SEED ^ ((i+1)*2654435761))>>>0;
    x^=x<<13; x>>>=0; x^=x>>>17; x^=x<<5; x>>>=0;
    return (x>>>0)/4294967296;
  }
  const _gid = CanvasRenderingContext2D.prototype.getImageData;
  CanvasRenderingContext2D.prototype.getImageData = function(){
    const d = _gid.apply(this, arguments);
    try{
      const a = d.data;
      for(let i=0;i<a.length;i+=4){ a[i] ^= (_rnd(i)&1); }   // LSB نامرئی R
    }catch(e){}
    return d;
  };
  const _td = HTMLCanvasElement.prototype.toDataURL;
  HTMLCanvasElement.prototype.toDataURL = function(){
    try{
      const ctx = this.getContext('2d');
      if(ctx && this.width && this.height){
        const d = _gid.call(ctx, 0, 0, this.width, this.height);
        const a = d.data;
        for(let i=0;i<a.length;i+=4){ a[i] ^= (_rnd(i)&1); }
        ctx.putImageData(d, 0, 0);
      }
    }catch(e){}
    return _td.apply(this, arguments);
  };
}catch(e){}
"""

_JS_AUDIO = """
try{
  const SEED=__SEED__+7;
  function _rnd(i){
    let x=(SEED ^ ((i+1)*40503))>>>0;
    x^=x<<13; x>>>=0; x^=x>>>17; x^=x<<5; x>>>=0;
    return (x>>>0)/4294967296;
  }
  if(window.AudioBuffer && AudioBuffer.prototype.getChannelData){
    const _cd = AudioBuffer.prototype.getChannelData;
    AudioBuffer.prototype.getChannelData = function(ch){
      const d = _cd.call(this, ch);
      try{ for(let i=0;i<d.length;i++){ d[i] += (_rnd(i)-0.5)*1e-7; } }catch(e){}
      return d;
    };
  }
  if(window.AnalyserNode && AnalyserNode.prototype.getFloatFrequencyData){
    const _fd = AnalyserNode.prototype.getFloatFrequencyData;
    AnalyserNode.prototype.getFloatFrequencyData = function(arr){
      _fd.call(this, arr);
      try{ for(let i=0;i<arr.length;i++){ arr[i] += (_rnd(i)-0.5)*1e-7; } }catch(e){}
    };
  }
}catch(e){}
"""

_JS_WEBGL = """
try{
  const V=__WEBGL_VENDOR__, R=__WEBGL_RENDERER__;
  const _gp = WebGLRenderingContext.prototype.getParameter;
  WebGLRenderingContext.prototype.getParameter = function(p){
    if(p===37445) return V;
    if(p===37446) return R;
    return _gp.apply(this, arguments);
  };
  if(window.WebGL2RenderingContext){
    const _gp2 = WebGL2RenderingContext.prototype.getParameter;
    WebGL2RenderingContext.prototype.getParameter = function(p){
      if(p===37445) return V;
      if(p===37446) return R;
      return _gp2.apply(this, arguments);
    };
  }
}catch(e){}
"""

_JS_WEBRTC = """
try{
  window.RTCPeerConnection = undefined;
  window.webkitRTCPeerConnection = undefined;
}catch(e){}
"""


def build_stealth_js(config: Dict[str, Any], profile: str = "main") -> str:
    """اسکریپت نهایی ضد شناسایی برای یک پروفایل — خالی یعنی غیرفعال."""
    st = config.get("stealth") or {}
    if not st.get("enabled", True):
        return ""
    if profile in (st.get("disable_for") or []):
        return ""
    mods = resolve_modules(st, config.get("browser"))
    if not any(mods.values()):
        return ""

    seed = _stable_seed(profile)
    vendor, renderer = WEBGL_GPUS[seed % len(WEBGL_GPUS)]
    params = json.dumps({
        "seed": seed,
        "cores": _plausible_cores(),
        "vendor": vendor,
        "renderer": renderer,
    })

    parts = [
        "/* ParsAgent stealth v2 — profile: %s */" % profile,
        "(function(){",
        "const S=%s;" % params,
    ]
    if mods.get("webdriver"):
        parts.append(_JS_WEBDRIVER)
    if mods.get("chrome_runtime"):
        parts.append(_JS_CHROME_RUNTIME)
    if mods.get("permissions"):
        parts.append(_JS_PERMISSIONS)
    if mods.get("plugins"):
        parts.append(_JS_PLUGINS)
    if mods.get("languages_platform"):
        parts.append(_JS_LANG_PLATFORM)
    if mods.get("hw_specs"):
        parts.append(_JS_HW.replace("__CORES__", str(_plausible_cores())))
    if mods.get("canvas_noise"):
        parts.append(_JS_CANVAS.replace("__SEED__", str(seed)))
    if mods.get("audio_noise"):
        parts.append(_JS_AUDIO.replace("__SEED__", str(seed)))
    if mods.get("webgl_mask"):
        parts.append(
            (_JS_WEBGL.replace("__WEBGL_VENDOR__", json.dumps(vendor))
                      .replace("__WEBGL_RENDERER__", json.dumps(renderer))))
    if mods.get("webrtc_shield"):
        parts.append(_JS_WEBRTC)
    parts.append("})();")
    return "\n".join(parts)


# --------------------------------------------------------------------------- #
# کاوشگر اثر انگشت — برای دکمهٔ «تست سریع» در پنل
# --------------------------------------------------------------------------- #
PROBE_JS = """(() => {
  const gl = document.createElement('canvas').getContext('webgl');
  let vendor = 'n/a', renderer = 'n/a';
  try {
    const d = gl.getExtension('WEBGL_debug_renderer_info');
    vendor = d ? gl.getParameter(d.UNMASKED_VENDOR_WEBGL) : 'n/a';
    renderer = d ? gl.getParameter(d.UNMASKED_RENDERER_WEBGL) : 'n/a';
  } catch (e) {}
  return {
    webdriver: navigator.webdriver === undefined ? null : navigator.webdriver,
    plugins: navigator.plugins ? navigator.plugins.length : -1,
    languages: (navigator.languages || []).join(','),
    platform: navigator.platform || '',
    chrome: !!window.chrome,
    vendor: vendor, renderer: renderer,
    cores: navigator.hardwareConcurrency || 0,
    memory: navigator.deviceMemory || null,
    ua: navigator.userAgent
  };
})()"""


def evaluate_probe(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """نتیجهٔ probe_js را به چک‌لیست فارسی ✓/✗ تبدیل می‌کند (مقاوم به مقادیر عجیب)."""
    r = result if isinstance(result, dict) else {}

    def _int(v: Any) -> int:
        try:
            return int(v)
        except Exception:
            return -1

    def _str(v: Any) -> str:
        return v if isinstance(v, str) else ("" if v is None else str(v))

    bad_gpu = ("swiftshader", "llvmpipe", "google inc. (nvidia)", "mesa",
               "angle (google", "basic render")
    renderer = _str(r.get("renderer")).lower()
    plugins = _int(r.get("plugins"))
    cores = _int(r.get("cores"))
    checks = [
        ("navigator.webdriver پاک است", r.get("webdriver") in (None, False, "false", 0, "undefined"),
         "webdriver=%s" % r.get("webdriver")),
        ("پلاگین‌های مرورگر واقعی‌اند", plugins >= 3, "%s پلاگین" % r.get("plugins")),
        ("window.chrome موجود است", bool(r.get("chrome")), ""),
        ("پلتفرم = Win32", _str(r.get("platform")) == "Win32", _str(r.get("platform"))),
        ("زبان‌ها شامل fa-IR", "fa-IR" in _str(r.get("languages")),
         _str(r.get("languages"))),
        ("GPU مشکوک نیست", not any(b in renderer for b in bad_gpu),
         _str(r.get("renderer"))[:90]),
        ("هستهٔ CPU طبیعی است", 4 <= cores <= 32, "%s هسته" % r.get("cores")),
    ]
    return [{"label": lb, "pass": bool(ok), "actual": ac} for lb, ok, ac in checks]
