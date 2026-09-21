import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, Download, CheckCircle2, XCircle } from "lucide-react";
import api from "../services/api";
import ConfidenceGauge from "../components/common/ConfidenceGauge";
import VerdictBadge from "../components/common/VerdictBadge";
import type { AnalysisResult } from "../types";

export default function AnalysisDetailPage() {
  const { id } = useParams();
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get<AnalysisResult>(`/analysis/${id}`).then(({ data }) => setResult(data)).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="font-mono text-sm text-ink-700 dark:text-mist-400">Loading…</div>;
  if (!result) return <div className="text-sm">Analysis not found.</div>;

  return (
    <div className="mx-auto max-w-5xl">
      <Link to="/history" className="mb-6 inline-flex items-center gap-1.5 font-mono text-xs text-ink-700/60 hover:text-signal-cyan dark:text-mist-400">
        <ArrowLeft size={14} /> Back to history
      </Link>

      <div className="card grid gap-6 p-6 md:grid-cols-[auto,1fr,auto] md:items-center">
        <ConfidenceGauge score={result.confidence_score} verdict={result.verdict} size={140} label="Confidence" />
        <div>
          <VerdictBadge verdict={result.verdict} />
          <p className="mt-2 truncate font-medium">{result.original_filename}</p>
          <p className="text-xs text-ink-700/60 dark:text-mist-400">{new Date(result.created_at).toLocaleString()}</p>
        </div>
        <a href={`/api/v1/analysis/${result.id}/report.pdf`} target="_blank" rel="noreferrer" className="btn-secondary !py-2 !text-sm">
          <Download size={14} /> PDF Report
        </a>
      </div>

      <div className="mt-6 grid gap-6 md:grid-cols-2">
        <div className="card p-6">
          <h3 className="font-display font-semibold">Extracted Payment Details</h3>
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
                {r.passed ? <CheckCircle2 size={15} className="mt-0.5 shrink-0 text-signal-green" /> : <XCircle size={15} className="mt-0.5 shrink-0 text-signal-red" />}
                <span>{r.text}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
