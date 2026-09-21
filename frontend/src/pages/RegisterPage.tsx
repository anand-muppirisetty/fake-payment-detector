import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ScanSearch } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    setLoading(true);
    try {
      await register(fullName, email, password);
      navigate("/dashboard");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Registration failed.");
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
        <h1 className="mt-6 text-center font-display text-2xl font-bold">Create your account</h1>
        <p className="mt-1 text-center text-sm text-ink-700/70 dark:text-mist-400">
          Start analyzing payment screenshots in minutes.
        </p>

        <form onSubmit={handleSubmit} className="mt-8 space-y-4">
          <div>
            <label className="mb-1.5 block text-xs font-medium text-ink-700 dark:text-mist-300">Full name</label>
            <input required value={fullName} onChange={(e) => setFullName(e.target.value)} className="input-field" placeholder="Jane Doe" />
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-medium text-ink-700 dark:text-mist-300">Email</label>
            <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} className="input-field" placeholder="you@example.com" />
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-medium text-ink-700 dark:text-mist-300">Password</label>
            <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} className="input-field" placeholder="At least 8 characters" />
          </div>
          {error && <p className="rounded-lg bg-signal-red/10 px-3 py-2 text-xs text-signal-red">{error}</p>}
          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? "Creating account…" : "Create account"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-ink-700/70 dark:text-mist-400">
          Already have an account?{" "}
          <Link to="/login" className="font-semibold text-signal-cyanDim hover:text-signal-cyan">Sign in</Link>
        </p>
      </motion.div>
    </div>
  );
}
