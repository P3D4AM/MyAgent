"use client";

import * as React from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { FileCode2, RefreshCw } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { CopyButton } from "./copy-button";
import { SectionHeader } from "./section-header";
import {
  faNumber,
  fetchAgentFiles,
  type AgentFile,
  type AgentFilesResponse,
} from "./data";

const TREE_GROUPS: { key: string; label: string }[] = [
  { key: ".", label: "ریشه" },
  { key: "core", label: "هسته" },
  { key: "platforms", label: "پلتفرم‌ها" },
  { key: "tasks", label: "تسک‌ها" },
];

const LANG_BADGE: Record<string, string> = {
  python: "bg-emerald-500/15 text-emerald-300 ring-emerald-500/30",
  json: "bg-amber-400/15 text-amber-300 ring-amber-400/30",
  markdown: "bg-zinc-700/40 text-zinc-300 ring-zinc-600",
  batch: "bg-rose-500/15 text-rose-300 ring-rose-500/30",
  text: "bg-zinc-700/40 text-zinc-300 ring-zinc-600",
};

export function CodeViewer() {
  const [data, setData] = React.useState<AgentFilesResponse | null>(null);
  const [error, setError] = React.useState(false);
  const [selected, setSelected] = React.useState<string>("panel_server.py");

  const load = React.useCallback(() => {
    setError(false);
    fetchAgentFiles()
      .then((res) => {
        setData(res);
        setSelected((cur) =>
          res.files.some((f) => f.path === cur) ? cur : (res.files[0]?.path ?? ""),
        );
      })
      .catch(() => setError(true));
  }, []);

  React.useEffect(() => {
    load();
  }, [load]);

  const file: AgentFile | undefined = data?.files.find(
    (f) => f.path === selected,
  );

  const codeNode = React.useMemo(() => {
    if (!file) return null;
    return (
      <SyntaxHighlighter
        language={file.language}
        style={oneDark}
        showLineNumbers
        customStyle={{
          margin: 0,
          background: "transparent",
          fontSize: "13px",
          padding: "1rem 1.1rem",
        }}
        lineNumberStyle={{
          color: "#52525b",
          minWidth: "2.6em",
          userSelect: "none",
        }}
        codeTagProps={{
          style: {
            fontFamily: "'JetBrains Mono', 'Consolas', monospace",
          },
        }}
      >
        {file.content}
      </SyntaxHighlighter>
    );
  }, [file]);

  const grouped = React.useMemo(() => {
    const map = new Map<string, AgentFile[]>();
    for (const g of TREE_GROUPS) {
      const files = (data?.files ?? []).filter((f) => f.dir === g.key);
      if (files.length) map.set(g.key, files);
    }
    return map;
  }, [data]);

  // -------------------------------- error --------------------------------
  if (error) {
    return (
      <section id="code" className="scroll-mt-24 py-16 sm:py-20">
        <div className="mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8">
          <SectionHeader index="۰۶" en="source" title="مرور سورس‌کد" />
          <div className="mt-10 flex flex-col items-center gap-4 rounded-xl border border-red-500/30 bg-red-500/5 p-10 text-center">
            <p className="text-sm text-red-300">
              خطا در دریافت سورس‌کد — اتصال به API برقرار نشد.
            </p>
            <Button
              onClick={load}
              variant="outline"
              className="border-red-500/40 text-red-300 hover:bg-red-500/10"
            >
              <RefreshCw className="size-4" aria-hidden="true" />
              تلاش دوباره
            </Button>
          </div>
        </div>
      </section>
    );
  }

  // ------------------------------- loading --------------------------------
  if (!data) {
    return (
      <section id="code" className="scroll-mt-24 py-16 sm:py-20">
        <div className="mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8">
          <SectionHeader index="۰۶" en="source" title="مرور سورس‌کد" />
          <div className="mt-10 grid gap-6 lg:grid-cols-[256px_minmax(0,1fr)]">
            <div className="hidden space-y-2 lg:block">
              <Skeleton className="h-5 w-24" />
              {Array.from({ length: 9 }).map((_, i) => (
                <Skeleton key={i} className="h-9 w-full" />
              ))}
            </div>
            <div className="space-y-3">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-[420px] w-full rounded-xl" />
            </div>
          </div>
        </div>
      </section>
    );
  }

  // -------------------------------- ready ---------------------------------
  return (
    <section id="code" className="scroll-mt-24 py-16 sm:py-20">
      <div className="mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionHeader
          index="۰۶"
          en="source"
          title="مرور سورس‌کد"
          subtitle="کل ایجنت، فایل به فایل؛ از موتور تسک تا ماژول هر پلتفرم — بدون ترک کردن همین صفحه."
        />

        {/* stats strip */}
        <p className="mt-6 text-center text-xs text-zinc-500">
          <span className="font-mono text-emerald-400/90">
            {faNumber(data.stats.totalFiles)}
          </span>{" "}
          فایل ·{" "}
          <span className="font-mono text-emerald-400/90">
            {faNumber(data.stats.totalLines)}
          </span>{" "}
          خط کد · ~
          <span className="font-mono text-emerald-400/90">
            {faNumber(Math.max(1, Math.round(data.stats.totalSize / 1024)))}
          </span>{" "}
          کیلوبایت
        </p>

        {/* mobile file picker */}
        <div className="mt-6 lg:hidden">
          <Select value={selected} onValueChange={setSelected}>
            <SelectTrigger className="w-full border-zinc-800 bg-zinc-900 font-mono text-sm">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="border-zinc-800 bg-zinc-900">
              {[...grouped.entries()].map(([key, files]) => {
                const label = TREE_GROUPS.find((g) => g.key === key)?.label ?? key;
                return (
                  <SelectGroup key={key}>
                    <SelectLabel>{label}</SelectLabel>
                    {files.map((f) => (
                      <SelectItem key={f.path} value={f.path} className="font-mono text-xs">
                        {f.path}
                      </SelectItem>
                    ))}
                  </SelectGroup>
                );
              })}
            </SelectContent>
          </Select>
        </div>

        <div className="mt-6 grid gap-6 lg:grid-cols-[256px_minmax(0,1fr)]">
          {/* sidebar tree (desktop) */}
          <nav
            aria-label="فهرست فایل‌های سورس"
            className="hidden max-h-[620px] flex-col gap-4 overflow-y-auto scrollbar-thin rounded-xl border border-zinc-800/80 bg-zinc-900/40 p-3 lg:flex"
          >
            {[...grouped.entries()].map(([key, files]) => {
              const label = TREE_GROUPS.find((g) => g.key === key)?.label ?? key;
              return (
                <div key={key}>
                  <div className="flex items-center justify-between px-2 pb-1.5">
                    <span className="text-[11px] font-bold uppercase tracking-wide text-zinc-500">
                      {label}
                    </span>
                    <span className="font-mono text-[10px] text-zinc-600">
                      {faNumber(files.length)}
                    </span>
                  </div>
                  <ul className="space-y-0.5">
                    {files.map((f) => {
                      const active = f.path === selected;
                      return (
                        <li key={f.path}>
                          <button
                            type="button"
                            onClick={() => setSelected(f.path)}
                            aria-current={active ? "true" : undefined}
                            className={cn(
                              "flex w-full items-center gap-2 rounded-md border-s-2 px-2 py-1.5 text-left font-mono text-xs transition-colors",
                              active
                                ? "border-s-emerald-500 bg-emerald-500/10 text-emerald-300"
                                : "border-s-transparent text-zinc-400 hover:bg-zinc-800/60 hover:text-zinc-200",
                            )}
                          >
                            <FileCode2
                              className={cn(
                                "size-3.5 shrink-0",
                                active ? "text-emerald-400" : "text-zinc-600",
                              )}
                              aria-hidden="true"
                            />
                            <span dir="ltr" className="truncate">
                              {f.path}
                            </span>
                          </button>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              );
            })}
          </nav>

          {/* main panel */}
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2 rounded-t-xl border border-zinc-800 bg-zinc-900/60 px-4 py-3">
              <span dir="ltr" className="font-mono text-sm text-zinc-200">
                {file?.dir !== "." && file ? (
                  <span className="text-zinc-500">{file.dir}/</span>
                ) : null}
                {file?.name}
              </span>
              {file ? (
                <Badge
                  variant="outline"
                  className={cn(
                    "border-transparent font-mono text-[10px]",
                    LANG_BADGE[file.language] ?? LANG_BADGE.text,
                  )}
                >
                  {file.language}
                </Badge>
              ) : null}
              <span className="text-[11px] text-zinc-500">
                {file ? `${faNumber(file.lines)} خط` : ""}
              </span>
              <span dir="ltr" className="font-mono text-[11px] text-zinc-500">
                {file ? `${(file.size / 1024).toFixed(1)} KB` : ""}
              </span>
              <span className="ms-auto">
                {file ? <CopyButton text={file.content} label="کپی سورس" /> : null}
              </span>
            </div>
            <div
              dir="ltr"
              className="max-h-[560px] overflow-auto scrollbar-thin rounded-b-xl border border-t-0 border-zinc-800 bg-zinc-950 text-left"
            >
              {codeNode}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
