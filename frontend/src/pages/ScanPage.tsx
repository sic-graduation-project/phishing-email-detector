import { useEffect, useRef, useState } from "react";
import {
  Mail,
  Link2,
  FileText,
  Search,
  Lock,
  Sparkles,
  ShieldAlert,
  ShieldCheck,
  ShieldQuestion,
  Clock,
  Lightbulb,
  AlertCircle,
  CheckCircle2,
  ArrowRight,
  Loader2,
} from "lucide-react";
import { Link, useSearchParams } from "react-router-dom";
import { scanEmail, inputKindLabel } from "../api/client";
import { saveScanToHistory } from "../api/history";
import type { InputKind, ScanResult } from "../types";
import RiskGauge from "../components/RiskGauge";

const INPUT_TYPES: { kind: InputKind; label: string; icon: typeof Mail }[] = [
  { kind: "email", label: "Email", icon: Mail },
  { kind: "url", label: "URL", icon: Link2 },
  { kind: "text", label: "Text", icon: FileText },
];

const LIMITS = { subject: 200, body: 5000, url: 500 };

const SECURITY_TIPS: Record<InputKind, string> = {
  email:
    "Never share your personal information via email. Always verify the sender and avoid clicking on suspicious links.",
  url: "Check the domain name carefully before entering credentials. Look for HTTPS and avoid shortened links from unknown sources.",
  text: "Be cautious of messages urging immediate action. Verify requests through an official channel before responding.",
};

function relativeTime(iso: string) {
  const diffSec = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
  if (diffSec < 60) return "Analyzed just now";
  if (diffSec < 3600) return `Analyzed ${Math.floor(diffSec / 60)}m ago`;
  return `Analyzed at ${new Date(iso).toLocaleTimeString()}`;
}

export default function ScanPage() {
  const [inputKind, setInputKind] = useState<InputKind>("email");
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [url, setUrl] = useState("");
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const content = inputKind === "email" ? body : inputKind === "url" ? url : text;
  const canSubmit = content.trim().length > 0 && !loading;

  function switchKind(kind: InputKind) {
    setInputKind(kind);
    setResult(null);
    setError(null);
  }

  async function runAnalysis(kind: InputKind, value: string, subjectValue?: string) {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const scan = await scanEmail({
        kind,
        subject: kind === "email" ? subjectValue : undefined,
        body: value,
      });
      saveScanToHistory(scan);
      setResult(scan);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong while analyzing this content.");
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;
    await runAnalysis(inputKind, content, subject);
  }

  // Deep link from the Nexus Chrome extension ("View Full Analysis"):
  //   /?url=<scanned URL>   or   /?text=<scanned text>
  // Fills the matching input and runs the same analysis as the Analyze button.
  // The ref keeps React StrictMode's double effect run from analyzing twice.
  const [searchParams, setSearchParams] = useSearchParams();
  const handledQuery = useRef<string | null>(null);

  useEffect(() => {
    const query = searchParams.toString();
    if (!query || handledQuery.current === query) return;

    const urlParam = searchParams.get("url");
    const textParam = searchParams.get("text");
    const kind: InputKind | null = urlParam?.trim() ? "url" : textParam?.trim() ? "text" : null;
    if (!kind) return;
    const value = (kind === "url" ? urlParam : textParam) as string;

    handledQuery.current = query;
    // This effect intentionally synchronizes component state with an external URL deep link.
    // oxlint-disable-next-line react/set-state-in-effect
    setInputKind(kind);
    if (kind === "url") setUrl(value);
    else setText(value);
    void runAnalysis(kind, value);

    // Drop the consumed parameters so a reload does not analyze (and log) it again.
    const remaining = new URLSearchParams(searchParams);
    remaining.delete("url");
    remaining.delete("text");
    setSearchParams(remaining, { replace: true });
  }, [searchParams, setSearchParams]);

  const riskScore = result ? result.riskScore : 0;
  const riskColor = result?.verdict === "phishing" ? "#ef4444" : riskScore >= 40 ? "#f59e0b" : "#10b981";
  const riskLabel = result?.verdict === "phishing" ? "Phishing detected" : riskScore >= 40 ? "Medium risk" : "Low risk";
  const KindIcon = result ? INPUT_TYPES.find((t) => t.kind === result.kind)?.icon ?? FileText : FileText;

  return (
    <div>
      <div className="flex flex-wrap items-end justify-between gap-3 mb-6">
        <div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white">
            AI Phishing Detector
          </h1>
          <p className="mt-1.5 text-slate-500 dark:text-slate-400">
            Analyze emails, URLs, or text using AI to detect potential phishing threats.
          </p>
        </div>
        <p className="hidden md:block italic text-sm text-slate-400">
          Smarter Analysis for a Safer Tomorrow
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        <div className="lg:col-span-3 space-y-6">
          <form
            onSubmit={handleSubmit}
            className="rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 p-5 sm:p-6 shadow-sm space-y-5"
          >
            <div>
              <h2 className="font-bold text-slate-900 dark:text-white">Input Type</h2>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Choose the type of content you want to analyze.
              </p>
              <div className="mt-3 grid grid-cols-3 gap-3">
                {INPUT_TYPES.map(({ kind, label, icon: Icon }) => (
                  <button
                    key={kind}
                    type="button"
                    onClick={() => switchKind(kind)}
                    className={`flex flex-col items-center gap-2 rounded-xl border-2 py-4 transition-colors ${
                      inputKind === kind
                        ? "border-blue-500 bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400"
                        : "border-slate-200 dark:border-white/10 text-slate-500 dark:text-slate-400 hover:border-slate-300 dark:hover:border-white/20"
                    }`}
                  >
                    <Icon size={22} />
                    <span className="text-sm font-medium">{label}</span>
                  </button>
                ))}
              </div>
            </div>

            {inputKind === "email" && (
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold text-slate-800 dark:text-slate-100">Email Details</h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    Enter the email subject and body to analyze.
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-600 dark:text-slate-300 mb-1.5">
                    Subject
                  </label>
                  <div className="relative">
                    <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      type="text"
                      value={subject}
                      maxLength={LIMITS.subject}
                      onChange={(e) => setSubject(e.target.value)}
                      placeholder="e.g. Urgent: Verify your account"
                      className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 pl-10 pr-3.5 py-2.5 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                    />
                  </div>
                  <p className="mt-1 text-right text-xs text-slate-400">
                    {subject.length}/{LIMITS.subject}
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-600 dark:text-slate-300 mb-1.5">
                    Email Body
                  </label>
                  <div className="relative">
                    <FileText size={16} className="absolute left-3.5 top-3.5 text-slate-400" />
                    <textarea
                      value={body}
                      maxLength={LIMITS.body}
                      onChange={(e) => setBody(e.target.value)}
                      rows={8}
                      placeholder="Paste the email content here..."
                      className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 pl-10 pr-3.5 py-2.5 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 resize-y"
                    />
                  </div>
                  <p className="mt-1 text-right text-xs text-slate-400">
                    {body.length}/{LIMITS.body}
                  </p>
                </div>
              </div>
            )}

            {inputKind === "url" && (
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold text-slate-800 dark:text-slate-100">URL Details</h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    Enter the web link you want to check.
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-600 dark:text-slate-300 mb-1.5">
                    Website URL
                  </label>
                  <div className="relative">
                    <Link2 size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      type="text"
                      value={url}
                      maxLength={LIMITS.url}
                      onChange={(e) => setUrl(e.target.value)}
                      placeholder="e.g. https://example.com/login"
                      className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 pl-10 pr-3.5 py-2.5 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                    />
                  </div>
                  <p className="mt-1 text-right text-xs text-slate-400">
                    {url.length}/{LIMITS.url}
                  </p>
                </div>
              </div>
            )}

            {inputKind === "text" && (
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold text-slate-800 dark:text-slate-100">Text Details</h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    Paste any message or paragraph you want to check.
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-600 dark:text-slate-300 mb-1.5">
                    Text Content
                  </label>
                  <div className="relative">
                    <FileText size={16} className="absolute left-3.5 top-3.5 text-slate-400" />
                    <textarea
                      value={text}
                      maxLength={LIMITS.body}
                      onChange={(e) => setText(e.target.value)}
                      rows={8}
                      placeholder="Paste any text content here..."
                      className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 pl-10 pr-3.5 py-2.5 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 resize-y"
                    />
                  </div>
                  <p className="mt-1 text-right text-xs text-slate-400">
                    {text.length}/{LIMITS.body}
                  </p>
                </div>
              </div>
            )}

            <div>
              <button
                type="submit"
                disabled={!canSubmit}
                className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-600/25 transition-transform hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50 disabled:pointer-events-none"
              >
                {loading ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
                {loading ? "Analyzing..." : `Analyze ${inputKindLabel[inputKind]}`}
              </button>
              <p className="mt-2.5 flex items-center justify-center gap-1.5 text-xs text-slate-400">
                <Lock size={12} />
                Your data is processed securely and is not stored.
              </p>
            </div>

            {error && (
              <div className="flex items-center gap-2 rounded-xl bg-red-50 dark:bg-red-500/10 px-4 py-3 text-sm text-red-600 dark:text-red-400">
                <AlertCircle size={16} />
                {error}
              </div>
            )}
          </form>

          <div className="rounded-2xl border border-blue-100 dark:border-blue-500/10 bg-blue-50/60 dark:bg-blue-500/5 p-5 sm:p-6">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles size={16} className="text-blue-600" />
              <h3 className="font-bold text-slate-900 dark:text-white">Supported Input Types</h3>
            </div>
            <div className="grid sm:grid-cols-3 gap-4">
              <div>
                <p className="flex items-center gap-1.5 font-medium text-slate-700 dark:text-slate-200">
                  <Mail size={15} /> Email
                </p>
                <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                  Subject + body of the email
                </p>
              </div>
              <div>
                <p className="flex items-center gap-1.5 font-medium text-slate-700 dark:text-slate-200">
                  <Link2 size={15} /> URL
                </p>
                <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                  Any web link (URL)
                </p>
              </div>
              <div>
                <p className="flex items-center gap-1.5 font-medium text-slate-700 dark:text-slate-200">
                  <FileText size={15} /> Text
                </p>
                <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                  Any text content (for example, a message or paragraph)
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-2xl bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-500/10 dark:to-indigo-500/10 p-5 sm:p-6 flex flex-col sm:flex-row items-center gap-5">
            <div className="relative h-14 w-14 shrink-0">
              <FileText size={28} className="absolute -left-1 -top-1 text-blue-300 dark:text-blue-400/40" />
              <div className="absolute right-0 bottom-0 grid place-items-center h-8 w-8 rounded-full bg-blue-600 text-white ring-4 ring-blue-50 dark:ring-[#0b0f1a]">
                <ShieldCheck size={16} />
              </div>
            </div>
            <div className="flex-1 text-center sm:text-left">
              <h3 className="font-bold text-slate-900 dark:text-white">Together for a Safer Internet</h3>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Leverage AI to detect threats, protect your information, and stay one step ahead.
              </p>
            </div>
            <Link
              to="/help"
              className="inline-flex items-center gap-1.5 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 transition-colors whitespace-nowrap"
            >
              Learn More <ArrowRight size={15} />
            </Link>
          </div>
        </div>

        <div className="lg:col-span-2">
          <div className="lg:sticky lg:top-24 space-y-5">
            {!result && !loading && (
              <div className="rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 p-8 text-center shadow-sm">
                <ShieldQuestion size={30} className="mx-auto mb-3 text-slate-300 dark:text-slate-600" />
                <h2 className="font-bold text-slate-800 dark:text-slate-100">Analysis Result</h2>
                <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                  Run an analysis to see the result here.
                </p>
              </div>
            )}

            {loading && (
              <div className="rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 p-10 text-center shadow-sm">
                <Loader2 size={30} className="mx-auto mb-3 animate-spin text-blue-500" />
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  Analyzing {inputKindLabel[inputKind].toLowerCase()} content...
                </p>
              </div>
            )}

            {result && !loading && (
              <div
                className={`rounded-2xl border p-5 sm:p-6 shadow-sm animate-scale-in ${
                  result.verdict === "phishing"
                    ? "border-red-100 dark:border-red-500/20 bg-gradient-to-br from-red-50 to-red-100/30 dark:from-red-500/10 dark:to-transparent"
                    : "border-emerald-100 dark:border-emerald-500/20 bg-gradient-to-br from-emerald-50 to-emerald-100/30 dark:from-emerald-500/10 dark:to-transparent"
                }`}
              >
                <div className="flex items-center justify-between">
                  <h2 className="font-bold text-slate-900 dark:text-white">Analysis Result</h2>
                  <span className="flex items-center gap-1 text-xs text-slate-400">
                    <Clock size={12} />
                    {relativeTime(result.scannedAt)}
                  </span>
                </div>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  Here is the result of the analysis.
                </p>

                <div className="mt-4 flex items-center gap-4">
                  <div
                    className={`grid place-items-center h-16 w-16 shrink-0 rounded-full ${
                      result.verdict === "phishing"
                        ? "bg-red-100 dark:bg-red-500/15 text-red-600 dark:text-red-400"
                        : "bg-emerald-100 dark:bg-emerald-500/15 text-emerald-600 dark:text-emerald-400"
                    }`}
                  >
                    {result.verdict === "phishing" ? <ShieldAlert size={30} /> : <ShieldCheck size={30} />}
                  </div>
                  <div>
                    <p
                      className={`text-xl font-extrabold ${
                        result.verdict === "phishing"
                          ? "text-red-600 dark:text-red-400"
                          : "text-emerald-600 dark:text-emerald-400"
                      }`}
                    >
                      {result.verdict === "phishing" ? "Phishing" : "Safe"}
                    </p>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      {result.verdict === "phishing"
                        ? "This content shows strong signs of being a phishing attempt."
                        : "This content does not show notable signs of phishing."}
                    </p>
                  </div>
                </div>

                <div className="mt-5 grid grid-cols-2 gap-3">
                  <div className="rounded-xl bg-white dark:bg-white/5 border border-slate-100 dark:border-white/10 p-4">
                    <RiskGauge percent={riskScore} riskLabel={riskLabel} color={riskColor} />
                  </div>
                  <div className="rounded-xl bg-white dark:bg-white/5 border border-slate-100 dark:border-white/10 p-4 flex flex-col items-center justify-center gap-2 text-center">
                    <div className="grid place-items-center h-10 w-10 rounded-xl bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400">
                      <KindIcon size={20} />
                    </div>
                    <p className="text-sm font-semibold text-slate-700 dark:text-slate-200">Input Type</p>
                    <span className="rounded-full bg-blue-50 dark:bg-blue-500/10 px-3 py-1 text-xs font-medium text-blue-600 dark:text-blue-400">
                      {inputKindLabel[result.kind]}
                    </span>
                  </div>
                </div>

                <div className="mt-5">
                  <h3 className="font-semibold text-slate-800 dark:text-slate-100 mb-2">
                    Reasons / Indicators
                  </h3>
                  <ul className="space-y-2">
                    {result.reasons.map((reason, i) => (
                      <li
                        key={i}
                        className={`flex items-start gap-2 rounded-xl px-3.5 py-2.5 text-sm ${
                          result.verdict === "phishing"
                            ? "bg-red-50 dark:bg-red-500/10 text-slate-700 dark:text-slate-200"
                            : "bg-emerald-50 dark:bg-emerald-500/10 text-slate-700 dark:text-slate-200"
                        }`}
                      >
                        {result.verdict === "phishing" ? (
                          <AlertCircle size={16} className="mt-0.5 shrink-0 text-red-500" />
                        ) : (
                          <CheckCircle2 size={16} className="mt-0.5 shrink-0 text-emerald-500" />
                        )}
                        {reason}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="mt-5 rounded-2xl bg-blue-50 dark:bg-blue-500/10 p-4 flex gap-3">
                  <Lightbulb size={20} className="shrink-0 text-blue-600 dark:text-blue-400" />
                  <div>
                    <p className="font-semibold text-slate-800 dark:text-slate-100">Security Tip</p>
                    <p className="mt-0.5 text-sm text-slate-600 dark:text-slate-300">
                      {SECURITY_TIPS[result.kind]}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
