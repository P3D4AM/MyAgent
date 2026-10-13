"""تست اندپوینت‌های جدید سرور پنل (credentials / login / stealth / state)
با هارنس stub — روی پورت 8799.
"""
import json
import sys
import threading
import time
import urllib.request

BASE = "http://127.0.0.1:8799"


def call(path, method="GET", body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        BASE + path, data=data, method=method,
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")


def wait_job(jid, timeout=60):
    t0 = time.time()
    while time.time() - t0 < timeout:
        st, j = call("/api/jobs/" + jid)
        if st == 200 and j.get("status") != "running":
            return j
        time.sleep(0.4)
    return {"status": "timeout"}


ok = 0


def check(label, cond, extra=""):
    global ok
    print(("  ✓ " if cond else "  ✗ FAIL ") + label + (" " + extra if extra else ""))
    if cond:
        ok += 1
    else:
        sys.exit(1)


# --- پاک‌سازی وضعیت اجراهای قبلی (تست باید idempotent باشد) ---
for pid in ("instagram", "facebook", "twitter", "telegram"):
    call("/api/credentials/delete", "POST", {"platform": pid})

# --- سلامت ---
st, h = call("/api/health")
check("health", st == 200 and h["ok"], h.get("version"))

st, s = call("/api/state")
check("state has credentials", st == 200 and "credentials" in s)
check("state platform has_creds", all("has_creds" in p for p in s["platforms"]))

# --- credentials CRUD ---
st, c = call("/api/credentials")
check("credentials GET", st == 200 and set(c["platforms"].keys()) >= {
    "instagram", "facebook", "bale"})

st, r = call("/api/credentials", "POST",
             {"platform": "instagram", "username": "test_user",
              "password": "pw123", "totp_secret": "JBSWY3DPEHPK3PXP"})
check("credentials POST", st == 200 and r["ok"], str(r.get("saved")))

st, c = call("/api/credentials")
ig = c["platforms"]["instagram"]
check("masked (no password leak)",
      ig["username"] == "test_user" and ig["has_password"] is True
      and ig["has_totp"] is True and "password" not in ig)

st, s = call("/api/state")
igp = [p for p in s["platforms"] if p["id"] == "instagram"][0]
check("platform has_creds flag", igp["has_creds"] is True)

st, r = call("/api/credentials/delete", "POST", {"platform": "instagram"})
check("credentials DELETE", st == 200 and r["existed"] is True)

st, c = call("/api/credentials")
check("cleared", c["platforms"]["instagram"]["username"] == "")

st, r = call("/api/credentials", "POST", {"platform": "instagram"})
check("empty POST rejected", st == 400)

st, r = call("/api/credentials", "POST", {"platform": "nope", "username": "x"})
check("bad platform rejected", st == 400)

# --- ورود خودکار: بدون اعتبارنامه → خطای فارسی واضح ---
st, r = call("/api/platform/login", "POST", {"platform": "facebook"})
# 400 فوری نباید باشد؛ job ساخته می‌شود و داخلش خطا می‌دهد (یا فوراً 503 اگر ایجنت نبود)
if st == 200:
    j = wait_job(r["id"])
    check("auto-login no-creds fails gracefully",
          j["status"] == "failed" and "ذخیره" in (j.get("error") or ""),
          str(j.get("error"))[:60])
else:
    check("auto-login no-creds fails gracefully", st in (400, 503), str(st))

# --- ورود خودکار: با اعتبارنامه → job اجرا می‌شود (با stub صفحه) ---
call("/api/credentials", "POST", {"platform": "facebook",
                                  "username": "me@test.com", "password": "pw"})
st, r = call("/api/platform/login", "POST", {"platform": "facebook"})
check("auto-login job created", st == 200, str(r)[:80])
j = wait_job(r["id"])
res = j.get("result") or {}
check("auto-login job ran",
      j["status"] in ("done", "failed") and isinstance(res.get("steps", []), list),
      f"status={j['status']} steps={len(res.get('steps', []))} err={str(j.get('error'))[:80]}")

call("/api/credentials/delete", "POST", {"platform": "facebook"})

# --- تست اثر انگشت (stealth probe) ---
st, r = call("/api/stealth/probe", "POST", {"platform": "instagram"})
check("stealth probe job created", st == 200)
if st == 200:
    j = wait_job(r["id"])
    # با stub ممکن است شکست بخورد ولی نباید crash کند — بررسی ساختار
    print(f"  ℹ probe status={j['status']} err={str(j.get('error'))[:70]}")
    check("probe job completed", j["status"] in ("done", "failed"))

st, r = call("/api/stealth/probe", "POST", {"platform": "bad"})
check("stealth probe bad platform 400", st == 400)

st, r = call("/api/stealth/test", "POST", {"platform": "bad"})
check("stealth test bad platform 400", st == 400)

# --- config roundtrip با stealth/captcha ---
st, r = call("/api/config")
check("config GET", st == 200 and "content" in r)
cfg = json.loads(r["content"])
check("config has stealth+captcha", "stealth" in cfg and "captcha" in cfg)

# --- ورود: پلتفرم نامعتبر ---
st, r = call("/api/platform/login", "POST", {"platform": "bad"})
check("login bad platform 404", st == 404)

print(f"\nALL {ok} ENDPOINT CHECKS PASSED ✅")
