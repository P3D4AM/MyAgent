import AdmZip from "adm-zip";
import path from "path";

export const dynamic = "force-dynamic";

const AGENT_ROOT = path.join(process.cwd(), "parsagent");

// user-data folders created at runtime — must never ship inside the ZIP
// (offline_bundle = wheels the user builds locally; can be hundreds of MB)
const RUNTIME_DIRS = new Set([
  "config",
  "media",
  "macros",
  "profiles",
  "logs",
  "offline_bundle",
]);
const ZIP_ROOT = "pars-agent";

export async function GET() {
  try {
    const zip = new AdmZip();
    // package the whole agent folder as pars-agent/
    // note: adm-zip passes the FULL zip entry path to the filter
    // (e.g. "pars-agent/static/index.html", dirs keep a trailing "/")
    zip.addLocalFolder(AGENT_ROOT, ZIP_ROOT, (entryPath) => {
      const p = entryPath.split("\\").join("/");
      if (p.includes("__pycache__")) {
        return false;
      }
      const rel = p.startsWith(`${ZIP_ROOT}/`) ? p.slice(ZIP_ROOT.length + 1) : p;
      const root = rel.replace(/\/+$/, "").split("/")[0];
      if (root && RUNTIME_DIRS.has(root)) {
        return false;
      }
      return true;
    });

    const buffer = zip.toBuffer();

    return new Response(new Uint8Array(buffer), {
      status: 200,
      headers: {
        "Content-Type": "application/zip",
        "Content-Disposition": 'attachment; filename="ParsAgent-v2.15.0.zip"',
        "Content-Length": String(buffer.length),
        "Cache-Control": "no-store",
      },
    });
  } catch (err) {
    return new Response(
      JSON.stringify({ ok: false, error: "zip generation failed" }),
      { status: 500, headers: { "Content-Type": "application/json" } },
    );
  }
}
