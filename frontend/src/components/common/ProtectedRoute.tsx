import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export function ProtectedRoute() {
  const { user, isLoading } = useAuth();
  if (isLoading) return <div className="grid h-screen place-items-center font-mono text-sm text-ink-700 dark:text-mist-400">Loading…</div>;
  if (!user) return <Navigate to="/login" replace />;
  return <Outlet />;
}

export function AdminRoute() {
  const { user, isLoading } = useAuth();
  if (isLoading) return <div className="grid h-screen place-items-center font-mono text-sm">Loading…</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== "admin") return <Navigate to="/dashboard" replace />;
  return <Outlet />;
}
