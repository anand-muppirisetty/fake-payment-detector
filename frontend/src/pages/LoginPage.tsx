import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ScanSearch, Eye, EyeOff } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Login failed. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid min-h-screen place-items-center bg-mist-100 px-4 dark:bg-ink-950">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="card w-full max-w-md p-8"
      >
        <Link to="/" className="flex items-center justify-center gap-2">
          <ScanSearch className="text-signal-cyan" size={22} />
          <span className="font-display text-lg font-bold">Fake Payment Detector AI</span>
        </Link>
        <h1 className="mt-6 text-center font-display text-2xl font-bold">Welcome back</h1>
        <p className="mt-1 text-center text-sm text-ink-700/70 dark:text-mist-400">
          Sign in to run a new forensic analysis.
        </p>

        <form onSubmit={handleSubmit} className="mt-8 space-y-4">
          <div>
            <label className="mb-1.5 block text-xs font-medium text-ink-700 dark:text-mist-300">Email</label>
            <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
                   className="input-field" placeholder="you@example.com" />
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-medium text-ink-700 dark:text-mist-300">Password</label>
            <div className="relative">
              <input type={showPassword ? "text" : "password"} required value={password}
                     onChange={(e) => setPassword(e.target.value)} className="input-field pr-11" placeholder="••••••••" />
              <button type="button" onClick={() => setShowPassword((s) => !s)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-ink-700/50 dark:text-mist-400">
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
            <div className="mt-2 text-right">
              <Link to="/forgot-password" className="font-mono text-xs text-signal-cyanDim hover:text-signal-cyan">
                Forgot password?
              </Link>
            </div>
          </div>
          {error && <p className="rounded-lg bg-signal-red/10 px-3 py-2 text-xs text-signal-red">{error}</p>}
          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-ink-700/70 dark:text-mist-400">
          Don't have an account?{" "}
          <Link to="/register" className="font-semibold text-signal-cyanDim hover:text-signal-cyan">
            Create one
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
