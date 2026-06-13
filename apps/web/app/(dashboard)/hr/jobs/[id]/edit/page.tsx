"use client";

import { use, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useSWRConfig } from "swr";
import { useAuth } from "../../../../../../context/AuthContext";
import { 
  Briefcase, 
  ChevronLeft, 
  Trash2, 
  Settings2, 
  ClipboardList, 
  Loader2,
  Sparkles,
  Users,
  Eye,
  Edit3,
  Plus
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import useSWR from "swr";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:4000";
const fetcher = (url: string) => fetch(url).then(res => res.json());

interface Criterion {
  id: string;
  label: string;
  weight: number;
  signals: string[];
}

export default function EditJobPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  const { mutate } = useSWRConfig();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isPreview, setIsPreview] = useState(false);

  // Fetch initial data
  const { data: job, isLoading: isFetching } = useSWR(`${API_BASE}/jobs/${id}`, fetcher);

  // Form State
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [testDuration, setTestDuration] = useState(3);
  const [isActive, setIsActive] = useState(true);
  
  // Scorecard State
  const [criteria, setCriteria] = useState<Criterion[]>([]);

  // Test Config State
  const [mcCount, setMcCount] = useState(0);
  const [mcPoints, setMcPoints] = useState(0);
  const [essayCount, setEssayCount] = useState(0);
  const [essayPoints, setEssayPoints] = useState(0);

  // Hiring Quotas State
  const [cvPassQuota, setCvPassQuota] = useState<number | "">("");
  const [assessmentPassQuota, setAssessmentPassQuota] = useState<number | "">("");
  const [interviewPassQuota, setInterviewPassQuota] = useState<number | "">("");

  useEffect(() => {
    if (job) {
      setTitle(job.title || "");
      setDescription(job.description || "");
      setTestDuration(job.test_duration || 3);
      setIsActive(job.is_active ?? true);
      
      if (job.scorecard_json?.criteria) {
        setCriteria(job.scorecard_json.criteria);
      }
      
      if (job.dynamic_test_config?.distribution) {
        const dist = job.dynamic_test_config.distribution;
        setMcCount(dist.multiple_choice?.count || 0);
        setMcPoints(dist.multiple_choice?.total_category_points || 0);
        setEssayCount(dist.essay?.count || 0);
        setEssayPoints(dist.essay?.total_category_points || 0);
      }

      setCvPassQuota(job.cv_pass_quota ?? "");
      setAssessmentPassQuota(job.assessment_pass_quota ?? "");
      setInterviewPassQuota(job.interview_pass_quota ?? "");
    }
  }, [job]);

  const totalWeight = criteria.reduce((sum, c) => sum + c.weight, 0);

  const addCriterion = () => {
    const newId = `crit_${Date.now()}`;
    setCriteria([...criteria, { id: newId, label: "", weight: 0, signals: [] }]);
  };

  const removeCriterion = (cid: string) => {
    setCriteria(criteria.filter(c => c.id !== cid));
  };

  const updateCriterion = (cid: string, field: keyof Criterion, value: any) => {
    setCriteria(criteria.map(c => c.id === cid ? { ...c, [field]: value } : c));
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
      const payload = {
        company_id: job.company_id,
        title,
        description,
        is_active: isActive,
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

      const res = await fetch(`${API_BASE}/jobs/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error("Failed to update job");
      
      mutate(`${API_BASE}/jobs`);
      mutate(`${API_BASE}/jobs/${id}`);
      router.push("/hr/jobs");
    } catch (err) {
      console.error(err);
      alert("Error updating job.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this job? This action cannot be undone.")) return;

    setIsDeleting(true);
    try {
      const res = await fetch(`${API_BASE}/jobs/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Deletion failed");
      
      mutate(`${API_BASE}/jobs`);
      router.push("/hr/jobs");
    } catch (err) {
      console.error(err);
      alert("Error deleting job.");
    } finally {
      setIsDeleting(false);
    }
  };

  if (isFetching) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#f3f5f0]">
        <Loader2 className="animate-spin text-[#e0563f]" size={40} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f3f5f0] text-[#18211d]">
      <header className="border-b border-black/5 bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-4">
            <button onClick={() => router.back()} className="text-[#607063] hover:text-[#18211d]">
              <ChevronLeft size={24} />
            </button>
            <h1 className="text-xl font-bold">Edit Job Post</h1>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleDelete}
              disabled={isDeleting || isSubmitting}
              className="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-2.5 text-sm font-bold text-red-600 hover:bg-red-100 disabled:opacity-50"
            >
              {isDeleting ? <Loader2 className="animate-spin" size={18} /> : <Trash2 size={18} />}
              Delete
            </button>
            <button
              form="job-form"
              disabled={isSubmitting || isDeleting}
              className="flex items-center gap-2 rounded-xl bg-[#18211d] px-6 py-2.5 text-sm font-bold text-white shadow-lg hover:opacity-90 disabled:opacity-50"
            >
              {isSubmitting ? <Loader2 className="animate-spin" size={18} /> : "Save Changes"}
            </button>
          </div>
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
                  <label className="text-sm font-semibold">Description & Requirements</label>
                  {isPreview ? (
                    <div className="min-h-[300px] w-full rounded-lg border border-[#d8ded5] bg-[#fbfcfa] p-4 prose prose-slate max-w-none prose-p:mb-4 prose-headings:text-[#18211d] prose-li:list-disc prose-li:ml-4">
                      <ReactMarkdown>{description || "*No description provided yet.*"}</ReactMarkdown>
                    </div>
                  ) : (
                    <textarea
                      required
                      rows={12}
                      placeholder="Use Markdown..."
                      className="w-full rounded-lg border border-[#d8ded5] bg-[#fbfcfa] px-4 py-2.5 text-sm outline-none focus:border-[#e0563f] font-mono"
                      value={description}
                      onChange={e => setDescription(e.target.value)}
                    />
                  )}
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
                <span className={`text-xs font-bold px-2 py-1 rounded-md ${totalWeight === 100 ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
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
            {/* Status */}
            <section className="rounded-2xl border border-black/5 bg-white p-8">
              <h2 className="mb-6 text-lg font-bold">Publishing Status</h2>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-[#607063]">Job is {isActive ? "Active" : "Paused"}</span>
                <button
                  type="button"
                  onClick={() => setIsActive(!isActive)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${isActive ? "bg-green-600" : "bg-gray-200"}`}
                >
                  <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${isActive ? "translate-x-6" : "translate-x-1"}`} />
                </button>
              </div>
            </section>

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
                <div className="space-y-4 pt-4 border-t border-black/5">
                  <h3 className="text-xs font-bold uppercase text-[#607063]">Multiple Choice</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <Field label="Count" value={mcCount} onChange={setMcCount} />
                    <Field label="Total Pts" value={mcPoints} onChange={setMcPoints} />
                  </div>
                </div>
                <div className="space-y-4">
                  <h3 className="text-xs font-bold uppercase text-[#607063]">Essay</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <Field label="Count" value={essayCount} onChange={setEssayCount} />
                    <Field label="Total Pts" value={essayPoints} onChange={setEssayPoints} />
                  </div>
                </div>
              </div>
            </section>
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
