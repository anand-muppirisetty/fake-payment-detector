import clsx from "clsx";
import { AlertTriangle, CheckCircle2, HelpCircle } from "lucide-react";
import type { Verdict } from "../../types";

const CONFIG: Record<Verdict, { icon: JSX.Element; classes: string }> = {
  "Likely Genuine": {
    icon: <CheckCircle2 size={14} />,
    classes: "bg-signal-green/10 text-signal-green border-signal-green/30",
  },
  "Needs Manual Review": {
    icon: <HelpCircle size={14} />,
    classes: "bg-signal-amber/10 text-signal-amber border-signal-amber/30",
  },
  "Highly Suspicious": {
    icon: <AlertTriangle size={14} />,
    classes: "bg-signal-red/10 text-signal-red border-signal-red/30",
  },
};

export default function VerdictBadge({ verdict, className }: { verdict: Verdict; className?: string }) {
  const cfg = CONFIG[verdict];
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1.5 rounded-full border px-3 py-1 font-mono text-xs font-medium",
        cfg.classes,
        className
      )}
    >
      {cfg.icon}
      {verdict}
    </span>
  );
}
