import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, LineChart, Line,
} from "recharts";
import { ScanSearch, ShieldAlert, ShieldCheck, Gauge, UploadCloud } from "lucide-react";
import api from "../services/api";
import StatCard from "../components/dashboard/StatCard";
import type { DashboardStats } from "../types";

const VERDICT_COLORS: Record<string, string> = {
  "Likely Genuine": "#3ecf8e",
  "Needs Manual Review": "#f5a623",
  "Highly Suspicious": "#ef4a5f",
};

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get<DashboardStats>("/analysis/stats/dashboard").then(({ data }) => {
      setStats(data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="font-mono text-sm text-ink-700 dark:text-mist-400">Loading dashboard…</div>;
  }

  const hasData = stats && stats.total_analyses > 0;
  const pieData = stats
    ? Object.entries(stats.verdict_breakdown).map(([name, value]) => ({ name, value }))
    : [];

  return (
    <div>
      <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-bold">Dashboard</h1>
          <p className="mt-1 text-sm text-ink-700/70 dark:text-mist-400">
            Your forensic analysis activity at a glance.
          </p>
        </div>
        <Link to="/upload" className="btn-primary !py-2.5">
          <UploadCloud size={16} /> New Analysis
        </Link>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={ScanSearch} label="Total Analyses" value={stats?.total_analyses ?? 0} accent="#33d6c0" />
        <StatCard icon={ShieldAlert} label="Suspicious Images" value={stats?.suspicious_count ?? 0} accent="#ef4a5f" />
        <StatCard icon={ShieldCheck} label="Genuine Images" value={stats?.genuine_count ?? 0} accent="#3ecf8e" />
        <StatCard icon={Gauge} label="Average Confidence" value={`${stats?.average_confidence ?? 0}%`} accent="#f5a623" />
      </div>

      {!hasData ? (
        <div className="card mt-8 flex flex-col items-center justify-center gap-3 p-16 text-center">
          <ScanSearch className="text-ink-700/30 dark:text-mist-400/30" size={40} />
          <p className="font-display font-semibold">No analyses yet</p>
          <p className="max-w-sm text-sm text-ink-700/70 dark:text-mist-400">
            Upload your first UPI payment screenshot to see forensic charts and history here.
          </p>
          <Link to="/upload" className="btn-primary mt-2 !py-2.5">Analyze a screenshot</Link>
        </div>
      ) : (
        <div className="mt-8 grid gap-5 lg:grid-cols-2">
          <div className="card p-6">
            <h3 className="mb-4 font-display font-semibold">Verdict Breakdown</h3>
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={60} outerRadius={90} paddingAngle={3}>
                  {pieData.map((entry) => (
                    <Cell key={entry.name} fill={VERDICT_COLORS[entry.name] || "#33d6c0"} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: "#0c1220", border: "1px solid #293457", borderRadius: 8, color: "#fff" }} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="card p-6">
            <h3 className="mb-4 font-display font-semibold">Analyses by Verdict</h3>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={pieData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#293457" opacity={0.3} />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} interval={0} />
                <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ background: "#0c1220", border: "1px solid #293457", borderRadius: 8, color: "#fff" }} />
                <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                  {pieData.map((entry) => (
                    <Cell key={entry.name} fill={VERDICT_COLORS[entry.name] || "#33d6c0"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="card p-6 lg:col-span-2">
            <h3 className="mb-4 font-display font-semibold">Analyses Over Time</h3>
            <ResponsiveContainer width="100%" height={240}>
              <LineChart data={stats?.daily_timeline ?? []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#293457" opacity={0.3} />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ background: "#0c1220", border: "1px solid #293457", borderRadius: 8, color: "#fff" }} />
                <Line type="monotone" dataKey="count" stroke="#33d6c0" strokeWidth={2.5} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
