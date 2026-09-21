import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import { UploadCloud, ImageIcon, X, Download, CheckCircle2, XCircle, Loader2 } from "lucide-react";
import api from "../services/api";
import ConfidenceGauge from "../components/common/ConfidenceGauge";
import VerdictBadge from "../components/common/VerdictBadge";
import type { AnalysisResult } from "../types";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((accepted: File[]) => {
    const f = accepted[0];
    if (!f) return;
    setFile(f);
    setResult(null);
    setError(null);
    setPreview(URL.createObjectURL(f));
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/png": [".png"], "image/jpeg": [".jpg", ".jpeg"] },
    maxFiles: 1,
    maxSize: 8 * 1024 * 1024,
  });

  const handleAnalyze = async () => {
    if (!file) return;
    setAnalyzing(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const { data } = await api.post<AnalysisResult>("/analysis/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Analysis failed. Please try another image.");
    } finally {
      setAnalyzing(false);
    }
  };

  const reset = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
  };

  const downloadReport = () => {
    if (!result) return;
    window.open(`/api/v1/analysis/${result.id}/report.pdf`, "_blank");
  };

  return (
    <div className="mx-auto max-w-5xl">
      <h1 className="font-display text-2xl font-bold">Analyze a Screenshot</h1>
      <p className="mt-1 text-sm text-ink-700/70 dark:text-mist-400">
        Upload a UPI payment screenshot (PNG or JPG, max 8MB) for forensic analysis.
      </p>

      {!result && (
        <div className="mt-8 grid gap-6 md:grid-cols-2">
          <div
            {...getRootProps()}
            className={`card flex min-h-[280px] cursor-pointer flex-col items-center justify-center gap-3 border-2 border-dashed p-8 text-center transition ${
              isDragActive ? "border-signal-cyan bg-signal-cyan/5" : "border-mist-300 dark:border-ink-600"
            }`}
          >
            <input {...getInputProps()} />
            {preview ? (
              <div className="relative w-full">
                <img src={preview} alt="Preview" className="mx-auto max-h-56 rounded-lg object-contain" />
                <button
                  onClick={(e) => { e.stopPropagation(); reset(); }}
                  className="absolute -right-2 -top-2 grid h-7 w-7 place-items-center rounded-full bg-ink-950 text-white"
                >
                  <X size={14} />
                </button>
              </div>
            ) : (
              <>
                <UploadCloud className="text-signal-cyan" size={32} />
                <p className="font-medium">Drag & drop a screenshot here</p>
                <p className="text-xs text-ink-700/60 dark:text-mist-400">or click to browse · PNG, JPG, JPEG</p>
              </>
            )}
          </div>

          <div className="card p-6">
            <h3 className="font-display font-semibold">What we check</h3>
            <ul className="mt-4 space-y-2.5 text-sm text-ink-700/80 dark:text-mist-300">
              {[
                "OCR extraction of amount, date, time, UTR, bank & UPI IDs",
                "Font & stroke consistency across the screenshot",
                "Copy-paste / cloned region detection",
                "Compression-artifact (ELA) analysis",
                "Blur inconsistency & crop plausibility",
                "Metadata anomalies & fake QR code detection",
              ].map((t) => (
                <li key={t} className="flex items-start gap-2">
                  <ImageIcon size={14} className="mt-0.5 shrink-0 text-signal-cyan" />
                  {t}
                </li>
              ))}
            </ul>
            {error && <p className="mt-4 rounded-lg bg-signal-red/10 px-3 py-2 text-xs text-signal-red">{error}</p>}
            <button
              onClick={handleAnalyze}
              disabled={!file || analyzing}
              className="btn-primary mt-6 w-full"
            >
              {analyzing ? <><Loader2 className="animate-spin" size={16} /> Analyzing…</> : "Run Forensic Analysis"}
            </button>
          </div>
        </div>
      )}

      <AnimatePresence>
        {result && (
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="mt-8 space-y-6">
            <div className="card grid gap-6 p-6 md:grid-cols-[auto,1fr] md:items-center">
              <ConfidenceGauge score={result.confidence_score} verdict={result.verdict} size={150} label="Confidence" />
              <div>
                <VerdictBadge verdict={result.verdict} />
                <p className="mt-3 text-sm text-ink-700/70 dark:text-mist-400">
                  {result.forensic_flags_count} of {result.forensic_findings.length} forensic checks flagged.
                  This is an automated image-forensics result, not a bank-confirmed verification.
                </p>
                <div className="mt-4 flex flex-wrap gap-3">
                  <button onClick={downloadReport} className="btn-secondary !py-2 !text-sm">
                    <Download size={14} /> Download PDF Report
                  </button>
                  <button onClick={reset} className="btn-secondary !py-2 !text-sm">Analyze another</button>
                </div>
              </div>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
              <div className="card p-6">
                <h3 className="font-display font-semibold">Extracted Payment Details (OCR)</h3>
                <dl className="mt-4 space-y-2 font-mono text-xs">
                  {Object.entries({
                    Amount: result.ocr.amount, Date: result.ocr.date, Time: result.ocr.time,
                    "UTR / Ref No.": result.ocr.utr, Bank: result.ocr.bank_name,
                    "Sender UPI": result.ocr.sender_upi, "Receiver UPI": result.ocr.receiver_upi,
                    "Status (as printed)": result.ocr.payment_status,
                  }).map(([k, v]) => (
                    <div key={k} className="flex justify-between border-b border-mist-200 dark:border-ink-700 py-1.5">
                      <dt className="text-ink-700/60 dark:text-mist-400">{k}</dt>
                      <dd>{v || "—"}</dd>
                    </div>
                  ))}
                </dl>
              </div>

              <div className="card p-6">
                <h3 className="font-display font-semibold">Explainability</h3>
                <ul className="mt-4 space-y-2.5">
                  {result.explanation_reasons.map((r, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm">
                      {r.passed ? (
                        <CheckCircle2 size={15} className="mt-0.5 shrink-0 text-signal-green" />
                      ) : (
                        <XCircle size={15} className="mt-0.5 shrink-0 text-signal-red" />
                      )}
                      <span>{r.text}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="card p-6">
              <h3 className="font-display font-semibold">Forensic Findings Detail</h3>
              <div className="mt-4 overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-mist-200 text-xs uppercase tracking-wider text-ink-700/50 dark:border-ink-700 dark:text-mist-400">
                      <th className="py-2 pr-4">Check</th>
                      <th className="py-2 pr-4">Result</th>
                      <th className="py-2 pr-4">Severity</th>
                      <th className="py-2">Detail</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.forensic_findings.map((f) => (
                      <tr key={f.code} className="border-b border-mist-100 dark:border-ink-800">
                        <td className="py-2.5 pr-4 font-medium">{f.label}</td>
                        <td className="py-2.5 pr-4">
                          <span className={f.detected ? "text-signal-red" : "text-signal-green"}>
                            {f.detected ? "Flagged" : "Passed"}
                          </span>
                        </td>
                        <td className="py-2.5 pr-4 capitalize text-ink-700/70 dark:text-mist-400">{f.severity}</td>
                        <td className="py-2.5 font-mono text-xs text-ink-700/70 dark:text-mist-400">{f.detail}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
