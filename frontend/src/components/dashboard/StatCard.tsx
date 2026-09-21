import { motion } from "framer-motion";
import type { LucideIcon } from "lucide-react";

export default function StatCard({
  icon: Icon, label, value, accent,
}: { icon: LucideIcon; label: string; value: string | number; accent: string }) {
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="card p-5">
      <div className="flex items-center justify-between">
        <span className="label-eyebrow">{label}</span>
        <div className="grid h-8 w-8 place-items-center rounded-full" style={{ backgroundColor: `${accent}1a` }}>
          <Icon size={15} style={{ color: accent }} />
        </div>
      </div>
      <p className="mt-3 font-display text-3xl font-bold">{value}</p>
    </motion.div>
  );
}
