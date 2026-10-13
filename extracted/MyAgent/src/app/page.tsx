"use client";

import * as React from "react";
import { Header } from "@/components/agent/header";
import { Hero } from "@/components/agent/hero";
import { Features } from "@/components/agent/features";
import { Engines } from "@/components/agent/engines";
import { Platforms } from "@/components/agent/platforms";
import { Demo } from "@/components/agent/demo";
import { Architecture } from "@/components/agent/architecture";
import { CodeViewer } from "@/components/agent/code-viewer";
import { InstallGuide } from "@/components/agent/install-guide";
import { DownloadSection } from "@/components/agent/download-section";
import { Footer } from "@/components/agent/footer";
import { ControlPanel } from "@/components/agent/panel/control-panel";

type PageView = "landing" | "panel";

export default function Home() {
  const [view, setView] = React.useState<PageView>("landing");

  const openPanel = React.useCallback(() => {
    setView("panel");
    window.scrollTo({ top: 0 });
  }, []);

  const exitPanel = React.useCallback(() => {
    setView("landing");
    window.scrollTo({ top: 0 });
  }, []);

  if (view === "panel") {
    return <ControlPanel onExit={exitPanel} />;
  }

  return (
    <div className="flex min-h-screen flex-col bg-zinc-950 font-sans text-zinc-100">
      <Header onOpenPanel={openPanel} />
      <main className="flex-1">
        <Hero onOpenPanel={openPanel} />
        <Features />
        <Engines />
        <Platforms />
        <Demo />
        <Architecture />
        <CodeViewer />
        <InstallGuide />
        <DownloadSection />
      </main>
      <Footer />
    </div>
  );
}
