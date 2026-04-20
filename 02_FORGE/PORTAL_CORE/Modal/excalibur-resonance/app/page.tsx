"use client";

import { HudHeader } from "../components/hud-header";
import { TheArmory } from "../components/the-armory";
import { Actuator } from "../components/actuator";

export default function Page() {
  return (
    <main className="min-h-screen bg-[#020203] text-slate-100 px-6 py-8">
      <HudHeader />
      <section className="mt-8 grid gap-6 lg:grid-cols-[2fr_1fr]">
        <TheArmory />
        <Actuator />
      </section>
    </main>
  );
}
