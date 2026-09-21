import { useEffect, useState } from "react";
import { Users, ScanSearch, ShieldAlert, Activity, Ban, CheckCircle } from "lucide-react";
import api from "../services/api";
import StatCard from "../components/dashboard/StatCard";
import type { AdminStats, AdminUser, SystemLog } from "../types";

type Tab = "users" | "logs";

export default function AdminPage() {
  const [tab, setTab] = useState<Tab>("users");
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [logs, setLogs] = useState<SystemLog[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    const [statsRes, usersRes, logsRes] = await Promise.all([
      api.get<AdminStats>("/admin/stats"),
      api.get<AdminUser[]>("/admin/users"),
      api.get<SystemLog[]>("/admin/logs"),
    ]);
    setStats(statsRes.data);
    setUsers(usersRes.data);
    setLogs(logsRes.data);
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  const toggleActive = async (user: AdminUser) => {
    await api.patch(`/admin/users/${user.id}`, { is_active: !user.is_active });
    setUsers((prev) => prev.map((u) => (u.id === user.id ? { ...u, is_active: !u.is_active } : u)));
  };

  if (loading) return <div className="font-mono text-sm text-ink-700 dark:text-mist-400">Loading admin dashboard…</div>;

  return (
    <div>
      <h1 className="font-display text-2xl font-bold">Admin Dashboard</h1>
      <p className="mt-1 text-sm text-ink-700/70 dark:text-mist-400">System-wide statistics, user management, and audit logs.</p>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={Users} label="Total Users" value={stats?.total_users ?? 0} accent="#33d6c0" />
        <StatCard icon={ScanSearch} label="Total Analyses" value={stats?.total_analyses ?? 0} accent="#f5a623" />
        <StatCard icon={ShieldAlert} label="Suspicious Rate" value={`${stats?.suspicious_rate_percent ?? 0}%`} accent="#ef4a5f" />
        <StatCard icon={Activity} label="Analyses (7 days)" value={stats?.analyses_last_7_days ?? 0} accent="#3ecf8e" />
      </div>

      <div className="mt-8 flex gap-2 border-b border-mist-200 dark:border-ink-700">
        {(["users", "logs"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2.5 text-sm font-medium capitalize transition ${
              tab === t ? "border-b-2 border-signal-cyan text-signal-cyan" : "text-ink-700/60 dark:text-mist-400"
            }`}
          >
            {t === "users" ? "User Management" : "System Logs"}
          </button>
        ))}
      </div>

      {tab === "users" ? (
        <div className="card mt-6 overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-mist-200 text-xs uppercase tracking-wider text-ink-700/50 dark:border-ink-700 dark:text-mist-400">
                <th className="px-5 py-3">Name</th>
                <th className="px-5 py-3">Email</th>
                <th className="px-5 py-3">Role</th>
                <th className="px-5 py-3">Analyses</th>
                <th className="px-5 py-3">Status</th>
                <th className="px-5 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-b border-mist-100 last:border-0 dark:border-ink-800">
                  <td className="px-5 py-3 font-medium">{u.full_name}</td>
                  <td className="px-5 py-3 font-mono text-xs">{u.email}</td>
                  <td className="px-5 py-3 capitalize">{u.role}</td>
                  <td className="px-5 py-3">{u.total_analyses}</td>
                  <td className="px-5 py-3">
                    <span className={u.is_active ? "text-signal-green" : "text-signal-red"}>
                      {u.is_active ? "Active" : "Disabled"}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-right">
                    <button
                      onClick={() => toggleActive(u)}
                      className="rounded-lg p-1.5 text-ink-700/60 hover:bg-mist-200 dark:text-mist-400 dark:hover:bg-ink-800"
                      title={u.is_active ? "Disable user" : "Enable user"}
                    >
                      {u.is_active ? <Ban size={15} /> : <CheckCircle size={15} />}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="card mt-6 max-h-[500px] overflow-y-auto">
          <table className="w-full text-left text-sm">
            <thead className="sticky top-0 bg-white dark:bg-ink-900">
              <tr className="border-b border-mist-200 text-xs uppercase tracking-wider text-ink-700/50 dark:border-ink-700 dark:text-mist-400">
                <th className="px-5 py-3">Event</th>
                <th className="px-5 py-3">Message</th>
                <th className="px-5 py-3">Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((l) => (
                <tr key={l.id} className="border-b border-mist-100 last:border-0 dark:border-ink-800">
                  <td className="px-5 py-3"><span className="rounded-full bg-mist-200 px-2 py-0.5 font-mono text-[10px] dark:bg-ink-800">{l.event_type}</span></td>
                  <td className="px-5 py-3 text-xs">{l.message}</td>
                  <td className="px-5 py-3 text-xs text-ink-700/60 dark:text-mist-400">{new Date(l.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
