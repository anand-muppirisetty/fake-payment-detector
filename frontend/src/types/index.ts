// Shared TypeScript types mirroring the backend Pydantic schemas.

export interface User {
  id: number;
  full_name: string;
  email: string;
  role: "user" | "admin";
  is_active: boolean;
  created_at: string;
}

export interface OCRFields {
  amount?: string | null;
  date?: string | null;
  time?: string | null;
  utr?: string | null;
  bank_name?: string | null;
  sender_upi?: string | null;
  receiver_upi?: string | null;
  payment_status?: string | null;
  raw_text?: string | null;
}

export interface ForensicFinding {
  code: string;
  label: string;
  detected: boolean;
  severity: "low" | "medium" | "high";
  detail: string;
  score_impact: number;
}

export interface ExplanationReason {
  text: string;
  passed: boolean;
  detail?: string;
}

export type Verdict = "Likely Genuine" | "Needs Manual Review" | "Highly Suspicious";

export interface AnalysisResult {
  id: number;
  original_filename: string;
  stored_filename: string;
  file_size_bytes: number;
  ocr: OCRFields;
  forensic_findings: ForensicFinding[];
  forensic_flags_count: number;
  confidence_score: number;
  verdict: Verdict;
  is_suspicious: boolean;
  explanation_reasons: ExplanationReason[];
  created_at: string;
}

export interface AnalysisListItem {
  id: number;
  original_filename: string;
  confidence_score: number;
  verdict: Verdict;
  is_suspicious: boolean;
  ocr_amount?: string | null;
  created_at: string;
}

export interface DashboardStats {
  total_analyses: number;
  suspicious_count: number;
  genuine_count: number;
  needs_review_count: number;
  average_confidence: number;
  verdict_breakdown: Record<string, number>;
  daily_timeline: { date: string; count: number }[];
}

export interface AdminUser {
  id: number;
  full_name: string;
  email: string;
  role: "user" | "admin";
  is_active: boolean;
  created_at: string;
  total_analyses: number;
}

export interface AdminStats {
  total_users: number;
  active_users: number;
  total_analyses: number;
  suspicious_rate_percent: number;
  analyses_last_7_days: number;
}

export interface SystemLog {
  id: number;
  event_type: string;
  message: string;
  user_id?: number | null;
  ip_address?: string | null;
  created_at: string;
}
