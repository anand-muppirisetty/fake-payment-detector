import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Search, Download, Trash2, ArrowUpDown, Eye } from "lucide-react";
import api from "../services/api";
import VerdictBadge from "../components/common/VerdictBadge";
import type { AnalysisListItem } from "../types";

export default function HistoryPage() {
  const [items, setItems] = useState<AnalysisListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [verdictFilter, setVerdictFilter] = useState<string>("");
  const [sortBy, setSortBy] = useState<"created_at" | "confidence_score">("created_at");
  const [order, setOrder] = useState<"asc" | "desc">("desc");

  const fetchHistory = async () => {
    setLoading(true);
    const { data } = await api.get<AnalysisListItem[]>("/analysis/history", {
      params: { search: search || undefined, verdict: verdictFilter || undefined, sort_by: sortBy, order },
    });
    setItems(data);
    setLoading(false);
  };

  useEffect(() => {
    const t = setTimeout(fetchHistory, 300);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search, verdictFilter, sortBy, order]);

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this analysis? This cannot be undone.")) return;
    await api.delete(`/analysis/${id}`);
    setItems((prev) => prev.filter((i) => i.id !== id));
  };

  const toggleSort = (field: "created_at" | "confidence_score") => {
    if (sortBy === field) setOrder(order === "asc" ? "desc" : "asc");
    else { setSortBy(field); setOrder("desc"); }
  };

  return (
    <div>
      <h1 className="font-display text-2xl font-bold">Analysis History</h1>
      <p className="mt-1 text-sm text-ink-700/70 dark:text-mist-400">
        Search, filter, and manage every screenshot you've analyzed.
      </p>

      <div className="mt-6 flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[220px]">
          <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-ink-700/40 dark:text-mist-400" size={15} />
          <input
            value={search} onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by filename or UTR…" className="input-field pl-9"
          />
        </div>
        <select value={verdictFilter} onChange={(e) => setVerdictFilter(e.target.value)} className="input-field w-auto">
          <option value="">All verdicts</option>
          <option value="Likely Genuine">Likely Genuine</option>
          <option value="Needs Manual Review">Needs Manual Review</option>
          <option value="Highly Suspicious">Highly Suspicious</option>
        </select>
      </div>

      <div className="card mt-6 overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-mist-200 text-xs uppercase tracking-wider text-ink-700/50 dark:border-ink-700 dark:text-mist-400">
              <th className="px-5 py-3">File</th>
              <th className="px-5 py-3">Amount</th>
              <th className="px-5 py-3">Verdict</th>
              <th className="cursor-pointer px-5 py-3" onClick={() => toggleSort("confidence_score")}>
                <span className="inline-flex items-center gap-1">Confidence <ArrowUpDown size={12} /></span>
              </th>
              <th className="cursor-pointer px-5 py-3" onClick={() => toggleSort("created_at")}>
                <span className="inline-flex items-center gap-1">Date <ArrowUpDown size={12} /></span>
              </th>
              <th className="px-5 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={6} className="px-5 py-8 text-center text-ink-700/50 dark:text-mist-400">Loading…</td></tr>
            ) : items.length === 0 ? (
              <tr><td colSpan={6} className="px-5 py-8 text-center text-ink-700/50 dark:text-mist-400">No analyses found.</td></tr>
            ) : (
              items.map((item) => (
                <tr key={item.id} className="border-b border-mist-100 last:border-0 dark:border-ink-800">
                  <td className="max-w-[160px] truncate px-5 py-3 font-medium">{item.original_filename}</td>
                  <td className="px-5 py-3 font-mono text-xs">{item.ocr_amount || "—"}</td>
                  <td className="px-5 py-3"><VerdictBadge verdict={item.verdict} /></td>
                  <td className="px-5 py-3 font-mono">{item.confidence_score}%</td>
                  <td className="px-5 py-3 text-xs text-ink-700/60 dark:text-mist-400">
                    {new Date(item.created_at).toLocaleString()}
                  </td>
                  <td className="px-5 py-3">
                    <div className="flex justify-end gap-2">
                      <Link to={`/history/${item.id}`} className="rounded-lg p-1.5 text-ink-700/60 hover:bg-mist-200 hover:text-signal-cyan dark:text-mist-400 dark:hover:bg-ink-800">
                        <Eye size={15} />
                      </Link>
                      <a href={`/api/v1/analysis/${item.id}/report.pdf`} target="_blank" rel="noreferrer"
                         className="rounded-lg p-1.5 text-ink-700/60 hover:bg-mist-200 hover:text-signal-cyan dark:text-mist-400 dark:hover:bg-ink-800">
                        <Download size={15} />
                      </a>
                      <button onClick={() => handleDelete(item.id)} className="rounded-lg p-1.5 text-ink-700/60 hover:bg-signal-red/10 hover:text-signal-red dark:text-mist-400">
                        <Trash2 size={15} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
