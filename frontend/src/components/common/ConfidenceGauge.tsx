import { motion } from "framer-motion";
import clsx from "clsx";
import type { Verdict } from "../../types";

/**
 * Signature visual element of the product: a circular "scan reticle"
 * gauge used on the hero, the analysis result screen, and dashboard
 * cards. Its sweeping arc animates in to evoke an active forensic scan
 * completing, tying the confidence number to the product's core metaphor.
 */
const COLOR_BY_VERDICT: Record<Verdict, string> = {
  "Likely Genuine": "#3ecf8e",
  "Needs Manual Review": "#f5a623",
  "Highly Suspicious": "#ef4a5f",
};

export default function ConfidenceGauge({
  score,
  verdict,
  size = 168,
  label,
}: {
  score: number;
  verdict?: Verdict;
  size?: number;
  label?: string;
}) {
  const radius = size / 2 - 10;
  const circumference = 2 * Math.PI * radius;
  const color = verdict ? COLOR_BY_VERDICT[verdict] : "#33d6c0";
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="relative grid place-items-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          className="text-mist-300 dark:text-ink-700"
          strokeWidth={8}
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={8}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.1, ease: "easeOut" }}
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className={clsx("font-display text-3xl font-bold")} style={{ color }}>
          {Math.round(score)}%
        </span>
        {label && <span className="mt-1 font-mono text-[10px] uppercase tracking-wider text-ink-700/70 dark:text-mist-400">{label}</span>}
      </div>
    </div>
  );
}
