import { NextResponse } from "next/server";
import { readdir, readFile, stat } from "fs/promises";
import path from "path";

export const dynamic = "force-dynamic";

const AGENT_ROOT = path.join(process.cwd(), "parsagent");

const LANG_BY_EXT: Record<string, string> = {
  ".py": "python",
  ".json": "json",
  ".md": "markdown",
  ".bat": "batch",
  ".txt": "text",
  ".cfg": "ini",
  ".toml": "ini",
  ".html": "markup",
};

const SKIP_DIRS = new Set([
  "__pycache__",
  "node_modules",
  ".git",
  "logs",
  "profiles",
  "media",
  "macros",
  "config",
]);

interface AgentFile {
  path: string;
  name: string;
  dir: string;
  language: string;
  size: number;
  lines: number;
  content: string;
}

async function walk(dir: string, base: string, out: string[]) {
  const entries = await readdir(dir, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.name.startsWith(".") || SKIP_DIRS.has(entry.name)) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      await walk(full, base, out);
    } else if (entry.isFile()) {
      out.push(path.relative(base, full));
    }
  }
}

// Nice presentation order: entry files first, then the panel UI
const ORDER: { match: (p: string) => boolean; weight: number }[] = [
  { match: (p) => p === "panel_server.py", weight: 0 },
  { match: (p) => p === "ai_agent.py", weight: 1 },
  { match: (p) => p === "ai_media.py", weight: 2 },
  { match: (p) => p === "dm_reply.py", weight: 3 },
  { match: (p) => p === "README.md", weight: 4 },
  { match: (p) => p === "requirements.txt", weight: 5 },
  { match: (p) => p === "launcher.py", weight: 6 },
  { match: (p) => p === "ParsAgent.bat", weight: 7 },
  { match: (p) => p.startsWith("static/"), weight: 8 },
];

export async function GET() {
  try {
    const relPaths: string[] = [];
    await walk(AGENT_ROOT, AGENT_ROOT, relPaths);

    const files: AgentFile[] = [];
    let totalSize = 0;

    for (const rel of relPaths) {
      const full = path.join(AGENT_ROOT, rel);
      const [content, info] = await Promise.all([
        readFile(full, "utf-8"),
        stat(full),
      ]);
      totalSize += info.size;
      files.push({
        path: rel.split(path.sep).join("/"),
        name: path.basename(rel),
        dir: path.dirname(rel).split(path.sep).join("/"),
        language: LANG_BY_EXT[path.extname(rel)] ?? "text",
        size: info.size,
        lines: content.split("\n").length,
        content,
      });
    }

    files.sort((a, b) => {
      const wa = ORDER.find((o) => o.match(a.path))?.weight ?? 99;
      const wb = ORDER.find((o) => o.match(b.path))?.weight ?? 99;
      return wa === wb ? a.path.localeCompare(b.path) : wa - wb;
    });

    return NextResponse.json({
      ok: true,
      stats: {
        totalFiles: files.length,
        totalSize,
        totalLines: files.reduce((acc, f) => acc + f.lines, 0),
      },
      files,
    });
  } catch (err) {
    return NextResponse.json(
      { ok: false, error: "failed to read agent sources", detail: String(err) },
      { status: 500 },
    );
  }
}
