"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

/** Shared section heading: LTR mono index + Persian title + subtitle. */
export function SectionHeader({
  index,
  en,
  title,
  subtitle,
  className,
}: {
  index: string;
  en: string;
  title: string;
  subtitle?: string;
  className?: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 18 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-60px" }}
      transition={{ duration: 0.5 }}
      className={cn("mx-auto max-w-2xl text-center", className)}
    >
      <div dir="ltr" className="font-mono text-xs tracking-widest text-emerald-400">
        [ {index} · {en} ]
      </div>
      <h2 className="mt-3 text-2xl font-extrabold tracking-tight text-zinc-100 sm:text-3xl">
        {title}
      </h2>
      {subtitle ? (
        <p className="mt-3 text-sm leading-7 text-zinc-400 sm:text-base sm:leading-8">
          {subtitle}
        </p>
      ) : null}
    </motion.div>
  );
}

/** Shared fade-in-up wrapper used by section children. */
export function FadeIn({
  children,
  delay = 0,
  className,
}: {
  children: React.ReactNode;
  delay?: number;
  className?: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.5, delay }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
