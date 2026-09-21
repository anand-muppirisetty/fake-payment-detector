import { Link } from "react-router-dom";
import { ScanSearch } from "lucide-react";
import ThemeToggle from "../common/ThemeToggle";

export default function LandingNavbar() {
  return (
    <header className="sticky top-0 z-40 border-b border-white/5 bg-ink-950/70 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <Link to="/" className="flex items-center gap-2">
          <ScanSearch className="text-signal-cyan" size={22} />
          <span className="font-display text-lg font-bold text-mist-100">Fake Payment Detector AI</span>
        </Link>
        <nav className="hidden items-center gap-8 font-mono text-sm text-mist-300 md:flex">
          <a href="#features" className="hover:text-signal-cyan">Features</a>
          <a href="#architecture" className="hover:text-signal-cyan">Architecture</a>
          <a href="#about-ai" className="hover:text-signal-cyan">About the AI</a>
          <a href="#future" className="hover:text-signal-cyan">Future Scope</a>
        </nav>
        <div className="flex items-center gap-3">
          <ThemeToggle />
          <Link to="/login" className="hidden font-mono text-sm text-mist-300 hover:text-signal-cyan sm:block">
            Sign in
          </Link>
          <Link to="/register" className="btn-primary !px-5 !py-2 !text-sm">
            Get Started
          </Link>
        </div>
      </div>
    </header>
  );
}
