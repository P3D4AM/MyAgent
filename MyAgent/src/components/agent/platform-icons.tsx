"use client";

import { Facebook, Instagram, Linkedin, MessageCircle, Send, Twitter } from "lucide-react";
import { cn } from "@/lib/utils";

export interface PlatformVisual {
  Icon?: React.ComponentType<{ className?: string }>;
  letter?: string;
  /** tint classes for the circular badge */
  cls: string;
  /** short Persian name for compact buttons */
  short: string;
}

export const PLATFORM_VISUALS: Record<string, PlatformVisual> = {
  instagram: {
    Icon: Instagram,
    cls: "bg-emerald-500/10 text-emerald-300 ring-emerald-500/30",
    short: "اینستاگرام",
  },
  twitter: {
    Icon: Twitter,
    cls: "bg-zinc-800 text-zinc-300 ring-zinc-700",
    short: "توییتر",
  },
  telegram: {
    Icon: Send,
    cls: "bg-emerald-500/10 text-emerald-300 ring-emerald-500/30",
    short: "تلگرام",
  },
  whatsapp: {
    Icon: MessageCircle,
    cls: "bg-emerald-500/10 text-emerald-300 ring-emerald-500/30",
    short: "واتساپ",
  },
  facebook: {
    Icon: Facebook,
    cls: "bg-zinc-800 text-zinc-300 ring-zinc-700",
    short: "فیسبوک",
  },
  linkedin: {
    Icon: Linkedin,
    cls: "bg-zinc-800 text-zinc-300 ring-zinc-700",
    short: "لینکدین",
  },
  bale: {
    letter: "ب",
    cls: "bg-emerald-500/10 text-emerald-300 ring-emerald-500/30",
    short: "بله",
  },
  rubika: {
    letter: "ر",
    cls: "bg-amber-400/10 text-amber-300 ring-amber-400/30",
    short: "روبیکا",
  },
  eitaa: {
    letter: "ا",
    cls: "bg-rose-500/10 text-rose-300 ring-rose-500/30",
    short: "ایتا",
  },
};

/** Circular platform badge: lucide icon for global brands, Persian letter for Iranian ones. */
export function PlatformIcon({
  id,
  className,
}: {
  id: string;
  className?: string;
}) {
  const visual = PLATFORM_VISUALS[id];
  if (!visual) return null;
  if (visual.Icon) {
    const Icon = visual.Icon;
    return <Icon className={className} />;
  }
  return (
    <span className={cn("font-extrabold leading-none", className)}>
      {visual.letter}
    </span>
  );
}
