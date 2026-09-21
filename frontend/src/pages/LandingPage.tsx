import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import {
  ScanLine, FileSearch, Fingerprint, Braces, ShieldAlert, FileOutput,
  Cpu, Database, Server, Layout, ArrowRight, Ban, Microscope,
} from "lucide-react";
import LandingNavbar from "../components/landing/Navbar";
import ConfidenceGauge from "../components/common/ConfidenceGauge";

const FEATURES = [
  {
    icon: FileSearch,
    title: "OCR Field Extraction",
    desc: "Pulls amount, date, time, UTR, bank name, and UPI IDs directly off the screenshot using EasyOCR/Tesseract.",
  },
  {
    icon: Fingerprint,
    title: "Copy-Paste Detection",
    desc: "ORB keypoint matching flags cloned or duplicated pixel regions — a classic signature of pasted-in edits.",
  },
  {
    icon: ScanLine,
    title: "Compression Artifact Analysis",
    desc: "Error-Level-Analysis style re-encoding surfaces regions with a different compression history than the rest of the image.",
  },
  {
    icon: Braces,
    title: "Font & Stroke Consistency",
    desc: "Measures stroke-width uniformity across text to catch amounts or names rendered in a different app or editor.",
  },
  {
    icon: ShieldAlert,
    title: "Explainable Confidence Score",
    desc: "Every verdict comes with a plain-language checklist of exactly which signals passed and which failed.",
  },
  {
    icon: FileOutput,
    title: "Downloadable Forensic Report",
    desc: "Export a shareable PDF with the screenshot, OCR text, AI findings and timestamp for your records.",
  },
];

const ARCHITECTURE_LAYERS = [
  { icon: Layout, title: "Frontend", desc: "React + TypeScript + Tailwind CSS SPA — upload, dashboard, history, reports." },
  { icon: Server, title: "Backend API", desc: "FastAPI REST service with JWT auth, rate limiting, and input validation." },
  { icon: Cpu, title: "AI Pipeline", desc: "OCR → OpenCV forensics → CNN signal → rule-based confidence scoring." },
  { icon: Database, title: "PostgreSQL", desc: "Stores users, analyses, forensic findings and system logs." },
];

export default function LandingPage() {
  return (
    <div className="bg-ink-950 text-mist-100">
      <LandingNavbar />

      {/* ---------------- HERO ---------------- */}
      <section className="relative overflow-hidden border-b border-white/5">
        <div className="grid-bg pointer-events-none absolute inset-0 opacity-60" />
        <div className="pointer-events-none absolute -top-32 left-1/2 h-96 w-96 -translate-x-1/2 rounded-full bg-signal-cyan/10 blur-3xl" />
        <div className="relative mx-auto grid max-w-7xl gap-12 px-6 py-20 md:grid-cols-2 md:items-center md:py-28">
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
            <span className="label-eyebrow">Forensic AI · OCR · Computer Vision</span>
            <h1 className="mt-4 font-display text-4xl font-bold leading-tight md:text-5xl">
              Spot an edited UPI payment screenshot <span className="text-signal-cyan">before you trust it.</span>
            </h1>
            <p className="mt-5 max-w-xl text-mist-300">
              Fake Payment Detector AI runs every uploaded screenshot through OCR, image forensics, and a
              CNN-based classifier to produce an explainable confidence score — flagging font
              mismatches, copy-paste artifacts, edited amounts, and fake QR codes.
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-4">
              <Link to="/register" className="btn-primary">
                Analyze a screenshot <ArrowRight size={16} />
              </Link>
              <a href="#about-ai" className="btn-secondary !border-white/15 !text-mist-100">
                How it works
              </a>
            </div>
            <div className="mt-8 flex items-start gap-2 rounded-xl border border-signal-amber/25 bg-signal-amber/5 px-4 py-3 text-xs text-mist-300">
              <Ban size={15} className="mt-0.5 shrink-0 text-signal-amber" />
              <p>
                Fake Payment Detector AI analyzes image evidence only. It does <strong className="text-mist-100">not</strong>{" "}
                connect to any bank, UPI switch, or NPCI system, and never confirms real transaction settlement.
              </p>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.92 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.7, delay: 0.15 }}
            className="relative mx-auto w-full max-w-sm"
          >
            <div className="card !bg-ink-900/80 p-6 shadow-glow">
              <div className="flex items-center justify-between">
                <span className="label-eyebrow">Live Analysis Preview</span>
                <span className="h-2 w-2 animate-pulse rounded-full bg-signal-cyan" />
              </div>
              <div className="mt-6 flex justify-center">
                <ConfidenceGauge score={26} verdict="Highly Suspicious" label="Confidence" />
              </div>
              <div className="mt-6 space-y-2 font-mono text-xs">
                {[
                  { text: "Font inconsistencies", ok: false },
                  { text: "Metadata anomaly detected", ok: false },
                  { text: "UTR format valid", ok: true },
                  { text: "QR mismatch", ok: false },
                ].map((r) => (
                  <div key={r.text} className="flex items-center justify-between rounded-lg bg-ink-800/70 px-3 py-2">
                    <span className="text-mist-300">{r.text}</span>
                    <span className={r.ok ? "text-signal-green" : "text-signal-red"}>{r.ok ? "PASS" : "FLAG"}</span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ---------------- FEATURE CARDS ---------------- */}
      <section id="features" className="mx-auto max-w-7xl px-6 py-24">
        <span className="label-eyebrow">Capabilities</span>
        <h2 className="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
          A full forensic checklist, not just a yes/no answer.
        </h2>
        <div className="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.05 }}
              className="card p-6 !bg-ink-900/50"
            >
              <f.icon className="text-signal-cyan" size={22} />
              <h3 className="mt-4 font-display text-lg font-semibold">{f.title}</h3>
              <p className="mt-2 text-sm text-mist-300">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ---------------- ARCHITECTURE ---------------- */}
      <section id="architecture" className="border-y border-white/5 bg-ink-900/40 py-24">
        <div className="mx-auto max-w-7xl px-6">
          <span className="label-eyebrow">System Architecture</span>
          <h2 className="mt-3 max-w-2xl font-display text-3xl font-bold md:text-4xl">
            Four layers, one pipeline.
          </h2>
          <div className="mt-14 grid gap-4 md:grid-cols-4">
            {ARCHITECTURE_LAYERS.map((layer, i) => (
              <div key={layer.title} className="relative">
                <div className="card !bg-ink-950/60 p-6 text-center">
                  <div className="mx-auto grid h-12 w-12 place-items-center rounded-full bg-signal-cyan/10">
                    <layer.icon className="text-signal-cyan" size={20} />
                  </div>
                  <h4 className="mt-4 font-display font-semibold">{layer.title}</h4>
                  <p className="mt-2 text-xs text-mist-400">{layer.desc}</p>
                </div>
                {i < ARCHITECTURE_LAYERS.length - 1 && (
                  <ArrowRight className="absolute -right-5 top-1/2 hidden -translate-y-1/2 text-mist-400/40 md:block" size={18} />
                )}
              </div>
            ))}
          </div>
          <p className="mx-auto mt-10 max-w-2xl text-center font-mono text-xs text-mist-400">
            Upload → Storage (UUID-named) → OCR Extraction → Forensic CV Checks + CNN Signal →
            Confidence Scoring → PostgreSQL → Dashboard / History / PDF Report
          </p>
        </div>
      </section>

      {/* ---------------- ABOUT THE AI ---------------- */}
      <section id="about-ai" className="mx-auto max-w-7xl px-6 py-24">
        <div className="grid gap-12 md:grid-cols-2 md:items-center">
          <div>
            <span className="label-eyebrow">About the AI</span>
            <h2 className="mt-3 font-display text-3xl font-bold md:text-4xl">
              Explainable by design — every flag has a reason.
            </h2>
            <p className="mt-5 text-mist-300">
              Rather than a single opaque "fake / real" black box, Fake Payment Detector AI runs nine
              independent forensic checks — compression artifacts, copy-paste duplication, font
              consistency, blur mapping, metadata inspection, crop plausibility, QR structural
              validation, edited-amount halo detection, and UTR format checks — plus a CNN-based
              manipulation classifier. Each check contributes a transparent, signed score to the
              final confidence percentage, and every result is shown to the user with a plain
              explanation of what was measured.
            </p>
            <div className="mt-6 flex items-center gap-3 rounded-xl border border-white/10 bg-ink-900/60 px-4 py-3">
              <Microscope size={18} className="shrink-0 text-signal-cyan" />
              <p className="text-xs text-mist-400">
                The CNN classifier ships as a real, trainable architecture with an explainable
                heuristic fallback — see <span className="text-mist-200">Future Scope</span> for the
                path to a fully trained model.
              </p>
            </div>
          </div>
          <div className="card !bg-ink-900/50 p-6">
            <p className="label-eyebrow">Confidence bands</p>
            <div className="mt-5 space-y-4">
              {[
                { label: "Likely Genuine", range: "≥ 75%", color: "bg-signal-green" },
                { label: "Needs Manual Review", range: "45% – 74%", color: "bg-signal-amber" },
                { label: "Highly Suspicious", range: "< 45%", color: "bg-signal-red" },
              ].map((b) => (
                <div key={b.label} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className={`h-2.5 w-2.5 rounded-full ${b.color}`} />
                    <span className="text-sm">{b.label}</span>
                  </div>
                  <span className="font-mono text-xs text-mist-400">{b.range}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ---------------- FUTURE SCOPE ---------------- */}
      <section id="future" className="border-t border-white/5 bg-ink-900/40 py-24">
        <div className="mx-auto max-w-4xl px-6 text-center">
          <span className="label-eyebrow">Future Scope</span>
          <h2 className="mt-3 font-display text-3xl font-bold md:text-4xl">
            Intentionally out of scope, for now: bank-side verification.
          </h2>
          <p className="mx-auto mt-5 max-w-2xl text-mist-300">
            This project performs forensic image analysis only. Confirming that a transaction
            actually settled requires direct integration with official NPCI/bank APIs, which
            demand regulated institutional access this academic project does not have and does
            not attempt to simulate. A natural next phase is:
          </p>
          <div className="mx-auto mt-10 grid max-w-2xl gap-4 text-left sm:grid-cols-2">
            {[
              "Optional NPCI/bank-partner API integration for real settlement checks",
              "A larger labeled dataset to train the CNN classifier to convergence",
              "On-device mobile capture to reduce screenshot re-compression noise",
              "Multi-language OCR support for regional-language payment apps",
            ].map((item) => (
              <div key={item} className="card !bg-ink-950/60 p-4 text-sm text-mist-300">
                {item}
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t border-white/5 px-6 py-10 text-center font-mono text-xs text-mist-500">
        Fake Payment Detector AI — Final-year B.Tech AI & ML project. Forensic analysis only; not a bank verification service.
      </footer>
    </div>
  );
}
