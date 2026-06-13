"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useSWRConfig } from "swr";
import { useAuth } from "../../../../context/AuthContext";
import { 
  Briefcase, 
  ChevronLeft, 
  Plus, 
  Trash2, 
  Settings2, 
  ClipboardList, 
  Loader2,
  Sparkles,
  Users,
  Eye,
  Edit3
} from "lucide-react";
import ReactMarkdown from "react-markdown";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:4000";

interface Criterion {
  id: string;
  label: string;
  weight: number;
  signals: string[];
}

export default function CreateJobPage() {
  const router = useRouter();
  const { user } = useAuth();
  const { mutate } = useSWRConfig();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isPreview, setIsPreview] = useState(false);

  // Form State
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [testDuration, setTestDuration] = useState(3);
  
  // Scorecard State
  const [criteria, setCriteria] = useState<Criterion[]>([
    { id: "tech_depth", label: "Technical Depth", weight: 40, signals: ["Python", "FastAPI"] },
    { id: "experience", label: "Relevant Experience", weight: 40, signals: ["Backend", "AI"] },
    { id: "comm", label: "Communication", weight: 20, signals: ["Clear", "Concise"] },
  ]);

  // Test Config State
  const [mcCount, setMcCount] = useState(5);
  const [mcPoints, setMcPoints] = useState(50);
  const [essayCount, setEssayCount] = useState(2);
  const [essayPoints, setEssayPoints] = useState(50);

  // Hiring Quotas State
  const [cvPassQuota, setCvPassQuota] = useState<number | "">("");
  const [assessmentPassQuota, setAssessmentPassQuota] = useState<number | "">("");
  const [interviewPassQuota, setInterviewPassQuota] = useState<number | "">("");

  const totalWeight = criteria.reduce((sum, c) => sum + c.weight, 0);

  const addCriterion = () => {
    const id = `crit_${Date.now()}`;
    setCriteria([...criteria, { id, label: "", weight: 0, signals: [] }]);
  };

  const removeCriterion = (id: string) => {
    setCriteria(criteria.filter(c => c.id !== id));
  };

  const updateCriterion = (id: string, field: keyof Criterion, value: any) => {
    setCriteria(criteria.map(c => c.id === id ? { ...c, [field]: value } : c));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (totalWeight !== 100) {
      alert("Total criteria weight must equal 100%");
      return;
    }
    if ((mcPoints + essayPoints) !== 100) {
      alert("Total test points must equal 100");
      return;
    }

    setIsSubmitting(true);
    try {
      const companyRes = await fetch(`${API_BASE}/companies`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: `${user?.name}'s Company`, website: "https://example.com" }),
      });
      const company = await companyRes.json();
      const companyId = companyRes.status === 409 ? "00000000-0000-0000-0000-000000000000" : company.id;

      const payload = {
        company_id: companyId || "00000000-0000-0000-0000-000000000000",
        title,
        description,
        is_active: true,
        test_duration: testDuration,
        cv_pass_quota: cvPassQuota === "" ? null : cvPassQuota,
        assessment_pass_quota: assessmentPassQuota === "" ? null : assessmentPassQuota,
        interview_pass_quota: interviewPassQuota === "" ? null : interviewPassQuota,
        scorecard_json: { criteria },
        dynamic_test_config: {
          total_points: 100,
          distribution: {
            multiple_choice: { count: mcCount, total_category_points: mcPoints },
            essay: { count: essayCount, total_category_points: essayPoints }
          }
        }
      };

      const res = await fetch(`${API_BASE}/jobs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error("Failed to create job");
      
      mutate(`${API_BASE}/jobs`);
      router.push("/hr");
    } catch (err) {
      console.error(err);
      alert("Error creating job. Ensure API is running.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f3f5f0] text-[#18211d]">
      <header className="border-b border-black/5 bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-4">
            <button onClick={() => router.back()} className="text-[#607063] hover:text-[#18211d]">
              <ChevronLeft size={24} />
            </button>
            <h1 className="text-xl font-bold">Create New Job</h1>
          </div>
          <button
            form="job-form"
            disabled={isSubmitting}
            className="flex items-center gap-2 rounded-xl bg-[#e0563f] px-6 py-2.5 text-sm font-bold text-white shadow-lg shadow-[#e0563f]/20 hover:opacity-90 disabled:opacity-50"
          >
            {isSubmitting ? <Loader2 className="animate-spin" size={18} /> : "Publish Job"}
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-6 py-10">
        <form id="job-form" onSubmit={handleSubmit} className="grid gap-8 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-8">
            {/* Basic Info */}
            <section className="rounded-2xl border border-black/5 bg-white p-8">
              <div className="mb-6 flex items-center justify-between">
                <h2 className="flex items-center gap-2 text-lg font-bold">
                  <Briefcase size={20} className="text-[#e0563f]" />
                  Job Details
                </h2>
                <button
                  type="button"
                  onClick={() => setIsPreview(!isPreview)}
                  className="flex items-center gap-2 rounded-lg bg-[#f3f5f0] px-3 py-1.5 text-xs font-bold text-[#18211d] hover:bg-[#e0563f] hover:text-white transition-colors"
                >
                  {isPreview ? <Edit3 size={14} /> : <Eye size={14} />}
                  {isPreview ? "Edit" : "Preview"}
                </button>
              </div>

              <div className="space-y-6">
                <div className="space-y-1.5">
                  <label className="text-sm font-semibold">Job Title</label>
                  <input
                    required
                    placeholder="e.g. Senior Backend Engineer"
                    className="w-full rounded-lg border border-[#d8ded5] bg-[#fbfcfa] px-4 py-2.5 text-sm outline-none focus:border-[#e0563f]"
                    value={title}
                    onChange={e => setTitle(e.target.value)}
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-semibold">Description & Requirements (Markdown)</label>
                  {isPreview ? (
                    <div className="min-h-[300px] w-full rounded-lg border border-[#d8ded5] bg-[#fbfcfa] p-4 prose prose-slate max-w-none prose-p:mb-4 prose-headings:text-[#18211d] prose-li:list-disc prose-li:ml-4">
                      <ReactMarkdown>{description || "*No description provided yet.*"}</ReactMarkdown>
                    </div>
                  ) : (
                    <textarea
                      required
                      rows={12}
                      placeholder="Use Markdown for bold, lists, and headings..."
                      className="w-full rounded-lg border border-[#d8ded5] bg-[#fbfcfa] px-4 py-2.5 text-sm outline-none focus:border-[#e0563f] font-mono"
                      value={description}
                      onChange={e => setDescription(e.target.value)}
                    />
                  )}
                  <p className="text-[10px] text-[#607063] italic mt-1">
                    Pro tip: Use # for headings, * for lists, and **bold** for emphasis.
                  </p>
                </div>
              </div>
            </section>

            {/* AI Scorecard */}
            <section className="rounded-2xl border border-black/5 bg-white p-8">
              <div className="mb-6 flex items-center justify-between">
                <h2 className="flex items-center gap-2 text-lg font-bold">
                  <Sparkles size={20} className="text-[#e0563f]" />
                  AI Screening Rubric
                </h2>
                <span className={cn(
                  "text-xs font-bold px-2 py-1 rounded-md",
                  totalWeight === 100 ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
                )}>
                  Total Weight: {totalWeight}%
                </span>
              </div>
              
              <div className="space-y-4">
                {criteria.map((c) => (
                  <div key={c.id} className="group relative rounded-xl border border-[#d8ded5] p-4 bg-[#fbfcfa]">
                    <button 
                      type="button"
                      onClick={() => removeCriterion(c.id)}
                      className="absolute right-2 top-2 text-[#607063] hover:text-red-600 opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <Trash2 size={16} />
                    </button>
                    <div className="space-y-4">
                      <div className="grid gap-4 md:grid-cols-4">
                        <div className="md:col-span-3 space-y-1">
                          <label className="text-[10px] font-bold uppercase text-[#607063]">Criterion Name</label>
                          <input
                            required
                            placeholder="e.g. Technical Depth"
                            className="w-full border-b border-[#d8ded5] bg-transparent py-1 text-sm outline-none focus:border-[#e0563f]"
                            value={c.label}
                            onChange={e => updateCriterion(c.id, "label", e.target.value)}
                          />
                        </div>
                        <div className="space-y-1">
                          <label className="text-[10px] font-bold uppercase text-[#607063]">Weight (%)</label>
                          <input
                            type="number"
                            required
                            className="w-full border-b border-[#d8ded5] bg-transparent py-1 text-sm outline-none focus:border-[#e0563f]"
                            value={c.weight}
                            onChange={e => updateCriterion(c.id, "weight", parseInt(e.target.value) || 0)}
                          />
                        </div>
                      </div>
                      <div className="space-y-1">
                        <label className="text-[10px] font-bold uppercase text-[#607063]">Keywords & Signals (CSV)</label>
                        <textarea
                          placeholder="Python, FastAPI, Docker, Microservices..."
                          rows={2}
                          className="w-full rounded-md border border-[#d8ded5] bg-white p-2 text-sm outline-none focus:border-[#e0563f]"
                          value={c.signals.join(", ")}
                          onChange={e => updateCriterion(c.id, "signals", e.target.value.split(",").map(s => s.trim()))}
                        />
                        <p className="text-[9px] text-[#607063] italic">Separate skills with commas. The AI uses these to calculate the score.</p>
                      </div>
                    </div>
                  </div>
                ))}
                <button
                  type="button"
                  onClick={addCriterion}
                  className="flex w-full items-center justify-center gap-2 rounded-xl border border-dashed border-[#d8ded5] py-4 text-sm font-medium text-[#607063] hover:bg-[#f3f5f0] hover:text-[#18211d]"
                >
                  <Plus size={18} />
                  Add Criterion
                </button>
              </div>
            </section>
          </div>

          <aside className="space-y-8">
            {/* Hiring Targets */}
            <section className="rounded-2xl border border-black/5 bg-white p-8">
              <h2 className="mb-6 flex items-center gap-2 text-lg font-bold">
                <Users size={20} className="text-[#e0563f]" />
                Hiring Targets
              </h2>
              <div className="space-y-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-bold uppercase text-[#607063]">Pass CV Target</label>
                  <input
                    type="number"
                    placeholder="Unlimited"
                    className="w-full rounded-lg border border-[#d8ded5] bg-[#fbfcfa] px-4 py-2 text-sm outline-none focus:border-[#e0563f]"
                    value={cvPassQuota}
                    onChange={e => setCvPassQuota(e.target.value === "" ? "" : parseInt(e.target.value))}
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-bold uppercase text-[#607063]">Pass Assessment Target</label>
                  <input
                    type="number"
                    placeholder="Unlimited"
                    className="w-full rounded-lg border border-[#d8ded5] bg-[#fbfcfa] px-4 py-2 text-sm outline-none focus:border-[#e0563f]"
                    value={assessmentPassQuota}
                    onChange={e => setAssessmentPassQuota(e.target.value === "" ? "" : parseInt(e.target.value))}
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-bold uppercase text-[#607063]">Hire Target</label>
                  <input
                    type="number"
                    placeholder="Unlimited"
                    className="w-full rounded-lg border border-[#d8ded5] bg-[#fbfcfa] px-4 py-2 text-sm outline-none focus:border-[#e0563f]"
                    value={interviewPassQuota}
                    onChange={e => setInterviewPassQuota(e.target.value === "" ? "" : parseInt(e.target.value))}
                  />
                </div>
                <p className="text-[10px] text-[#607063] mt-2 italic">
                  * Quotas help the AI agents prioritize candidates when resources are limited.
                </p>
              </div>
            </section>

            {/* Test Configuration */}
            <section className="rounded-2xl border border-black/5 bg-white p-8">
              <h2 className="mb-6 flex items-center gap-2 text-lg font-bold">
                <Settings2 size={20} className="text-[#e0563f]" />
                Test Config
              </h2>
              <div className="space-y-6">
                <div className="space-y-1.5">
                  <label className="text-sm font-semibold text-[#607063]">Deadline (Days)</label>
                  <input
                    type="number"
                    className="w-full rounded-lg border border-[#d8ded5] bg-[#fbfcfa] px-4 py-2 text-sm outline-none focus:border-[#e0563f]"
                    value={testDuration}
                    onChange={e => setTestDuration(parseInt(e.target.value) || 0)}
                  />
                </div>
                <hr className="border-black/5" />
                <div className="space-y-4">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-[#607063]">Multiple Choice</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <Field label="Count" value={mcCount} onChange={setMcCount} />
                    <Field label="Total Pts" value={mcPoints} onChange={setMcPoints} />
                  </div>
                </div>
                <div className="space-y-4">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-[#607063]">Essay</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <Field label="Count" value={essayCount} onChange={setEssayCount} />
                    <Field label="Total Pts" value={essayPoints} onChange={setEssayPoints} />
                  </div>
                </div>
              </div>
            </section>

            {/* Help / Tips */}
            <div className="rounded-2xl bg-[#18211d] p-6 text-white">
              <h3 className="mb-3 flex items-center gap-2 text-sm font-bold">
                <ClipboardList size={16} />
                Pro Tip
              </h3>
              <p className="text-xs leading-relaxed text-white/70">
                Be specific in your JD. The AI uses it to extract hidden criteria if your rubric is too vague.
              </p>
            </div>
          </aside>
        </form>
      </main>
    </div>
  );
}

function Field({ label, value, onChange }: { label: string, value: number, onChange: (v: number) => void }) {
  return (
    <div className="space-y-1">
      <label className="text-[10px] font-bold text-[#607063]">{label}</label>
      <input
        type="number"
        className="w-full rounded-md border border-[#d8ded5] bg-[#fbfcfa] px-3 py-1.5 text-xs outline-none focus:border-[#e0563f]"
        value={value}
        onChange={e => onChange(parseInt(e.target.value) || 0)}
      />
    </div>
  );
}

function cn(...inputs: any[]) {
  return inputs.filter(Boolean).join(" ");
}
