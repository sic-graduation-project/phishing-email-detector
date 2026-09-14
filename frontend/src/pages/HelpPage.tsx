import { Mail, Link2, FileText, ShieldQuestion, Lightbulb } from "lucide-react";

const FAQS = [
  {
    q: "How does PhishGuard analyze my content?",
    a: "You paste in an email, URL, or block of text, and it's checked against known phishing patterns and risk signals to produce a verdict and risk score.",
  },
  {
    q: "Is my data stored anywhere?",
    a: "No. Content you submit is analyzed in the moment and is not stored on any server. Your scan history is kept only in your browser, on this device.",
  },
  {
    q: "Do I need an account to use PhishGuard?",
    a: "No sign-up is required. PhishGuard is fully open and accessible without logging in.",
  },
  {
    q: "What should I do if a result is flagged as phishing?",
    a: "Don't click any links or reply. Verify the sender through an official channel, and report or delete the message.",
  },
];

export default function HelpPage() {
  return (
    <div className="max-w-3xl">
      <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
        Help & Support
      </h1>
      <p className="mt-1.5 text-slate-500 dark:text-slate-400">
        Everything you need to get the most out of PhishGuard.
      </p>

      <div className="mt-6 rounded-2xl border border-blue-100 dark:border-blue-500/10 bg-blue-50/60 dark:bg-blue-500/5 p-5 sm:p-6">
        <div className="flex items-center gap-2 mb-4">
          <ShieldQuestion size={18} className="text-blue-600" />
          <h2 className="font-bold text-slate-900 dark:text-white">What can you analyze?</h2>
        </div>
        <div className="grid sm:grid-cols-3 gap-4">
          <div>
            <p className="flex items-center gap-1.5 font-medium text-slate-700 dark:text-slate-200">
              <Mail size={15} /> Email
            </p>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
              Paste a subject and body to check for phishing language and links.
            </p>
          </div>
          <div>
            <p className="flex items-center gap-1.5 font-medium text-slate-700 dark:text-slate-200">
              <Link2 size={15} /> URL
            </p>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
              Check a single link for suspicious domains or structure.
            </p>
          </div>
          <div>
            <p className="flex items-center gap-1.5 font-medium text-slate-700 dark:text-slate-200">
              <FileText size={15} /> Text
            </p>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
              Paste any message to scan for social-engineering red flags.
            </p>
          </div>
        </div>
      </div>

      <div className="mt-6 space-y-3">
        <h2 className="font-bold text-slate-900 dark:text-white">Frequently asked questions</h2>
        {FAQS.map((item) => (
          <div
            key={item.q}
            className="rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 p-4"
          >
            <p className="font-medium text-slate-800 dark:text-slate-100">{item.q}</p>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{item.a}</p>
          </div>
        ))}
      </div>

      <div className="mt-6 rounded-2xl bg-blue-50 dark:bg-blue-500/10 p-5 flex gap-3">
        <Lightbulb size={20} className="shrink-0 text-blue-600 dark:text-blue-400" />
        <div>
          <p className="font-semibold text-slate-800 dark:text-slate-100">Still need help?</p>
          <p className="mt-0.5 text-sm text-slate-600 dark:text-slate-300">
            Reach out to the PhishGuard team through your organization's usual support channel.
          </p>
        </div>
      </div>
    </div>
  );
}
