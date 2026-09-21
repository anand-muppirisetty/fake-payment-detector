import { useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ScanSearch } from "lucide-react";
import api from "../services/api";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await api.post("/auth/forgot-password", { email });
      setSent(true);
    } catch {
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid min-h-screen place-items-center bg-mist-100 px-4 dark:bg-ink-950">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="card w-full max-w-md p-8">
        <Link to="/" className="flex items-center justify-center gap-2">
          <ScanSearch className="text-signal-cyan" size={22} />
          <span className="font-display text-lg font-bold">Fake Payment Detector AI</span>
        </Link>
        <h1 className="mt-6 text-center font-display text-2xl font-bold">Reset your password</h1>
        <p className="mt-1 text-center text-sm text-ink-700/70 dark:text-mist-400">
          We'll send a reset link if that email is registered.
        </p>

        {sent ? (
          <div className="mt-8 rounded-xl bg-signal-green/10 px-4 py-4 text-center text-sm text-signal-green">
            If that email exists in our system, a reset link is on its way. Check your inbox.
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="mt-8 space-y-4">
            <div>
              <label className="mb-1.5 block text-xs font-medium text-ink-700 dark:text-mist-300">Email</label>
              <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} className="input-field" placeholder="you@example.com" />
            </div>
            {error && <p className="rounded-lg bg-signal-red/10 px-3 py-2 text-xs text-signal-red">{error}</p>}
            <button type="submit" disabled={loading} className="btn-primary w-full">
              {loading ? "Sending…" : "Send reset link"}
            </button>
          </form>
        )}

        <p className="mt-6 text-center text-sm text-ink-700/70 dark:text-mist-400">
          <Link to="/login" className="font-semibold text-signal-cyanDim hover:text-signal-cyan">Back to sign in</Link>
        </p>
      </motion.div>
    </div>
  );
}
