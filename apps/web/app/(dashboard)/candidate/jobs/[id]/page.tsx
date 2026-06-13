"use client";

import { use, useState } from "react";
import { useAuth } from "../../../../context/AuthContext";
import { 
  ChevronLeft, 
  Briefcase, 
  MapPin, 
  Clock, 
  Sparkles, 
  Loader2, 
  FileUp, 
  CheckCircle2,
  AlertCircle
} from "lucide-react";
import Link from "next/link";
import useSWR from "swr";
import { useRouter } from "next/navigation";
import ReactMarkdown from "react-markdown";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:4000";
const fetcher = (url: string) => fetch(url).then(res => res.json());

export default function CandidateJobDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  const { user } = useAuth();
  
  const { data: job, isLoading } = useSWR(`${API_BASE}/jobs/${id}`, fetcher);
  
  // Application State
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [isApplying, setIsApplying] = useState(false);
  const [applySuccess, setApplySuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showConflictDialog, setShowConflictDialog] = useState(false);
  const [existingAppId, setExistingAppId] = useState<string | null>(null);

  const handleApply = async (isUpdate = false) => {
    if (!cvFile || !user) return;
    
    setIsApplying(true);
    setError(null);
    setShowConflictDialog(false);
    
    try {
      // 1. Get presigned URL
      const presignRes = await fetch(`${API_BASE}/uploads/presign`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          kind: "cv",
          file_name: cvFile.name,
          content_type: cvFile.type || "application/pdf",
        }),
      });
      
      if (!presignRes.ok) throw new Error("Failed to get upload authorization.");
      const { object_key, upload_url } = await presignRes.json();

      // 2. Upload to R2
      const uploadRes = await fetch(upload_url, {
        method: "PUT",
        headers: { "Content-Type": cvFile.type || "application/pdf" },
        body: cvFile,
      });
      
      if (!uploadRes.ok) throw new Error("File upload failed.");

      // 3. Create or Update Application
      const url = isUpdate ? `${API_BASE}/applications/${existingAppId}` : `${API_BASE}/applications`;
      const method = isUpdate ? "PATCH" : "POST";

      const applyRes = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          candidate_id: user.id,
          job_id: id,
          cv_object_key: object_key,
        }),
      });

      if (applyRes.status === 409) {
        // Handle existing application conflict
        // Try getting ID from custom header X-Existing-ID
        let existingId = applyRes.headers.get("X-Existing-ID") || applyRes.headers.get("x-existing-id");
        
        if (!existingId) {
          // Fallback: fetch from body if API returned it there
          try {
            const body = await applyRes.json();
            existingId = body.existing_id;
          } catch (e) {
            console.error("Could not parse error body", e);
          }
        }

        if (existingId) {
          setExistingAppId(existingId);
          setShowConflictDialog(true);
        } else {
          setError("You have already applied for this job, but we couldn't retrieve your application ID. Please refresh the page.");
        }
        setIsApplying(false);
        return;
      }

      if (!applyRes.ok) throw new Error("Application submission failed.");
      
      const appData = await applyRes.json();
      setApplySuccess(true);
      setTimeout(() => router.push(`/candidate/applications/${appData.id}`), 2000);
      
    } catch (err: any) {
      setError(err.message);
    } finally {
      if (!showConflictDialog) {
        setIsApplying(false);
      }
    }
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#f3f5f0]">
        <Loader2 className="animate-spin text-[#e0563f]" size={40} />
      </div>
    );
  }

  if (!job) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#f3f5f0]">
        <p className="font-bold text-[#607063]">Job not found.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f3f5f0] text-[#18211d]">
      <header className="border-b border-black/5 bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <Link href="/candidate" className="flex items-center gap-2 text-sm font-bold text-[#607063] hover:text-[#18211d]">
            <ChevronLeft size={18} />
            Back to Job Board
          </Link>
          <div className="flex items-center gap-4">
             <div className="hidden md:block text-right text-[10px] font-bold uppercase tracking-wider text-[#607063]">
                Candidate Portal
             </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-6 py-10">
        <div className="grid gap-8 lg:grid-cols-3">
          {/* JD Content */}
          <div className="lg:col-span-2 space-y-8">
            <section className="rounded-3xl border border-black/5 bg-white p-10 shadow-sm">
              <div className="flex items-center gap-4 mb-6">
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-[#f3f5f0] text-[#e0563f]">
                  <Briefcase size={32} />
                </div>
                <div>
                  <h1 className="text-3xl font-bold tracking-tight">{job.title}</h1>
                  <div className="mt-2 flex items-center gap-4 text-sm font-medium text-[#607063]">
                    <span className="flex items-center gap-1.5"><MapPin size={16} /> Remote / Office</span>
                    <span>•</span>
                    <span className="flex items-center gap-1.5"><Clock size={16} /> Full-time</span>
                  </div>
                </div>
              </div>

              <div className="mt-10 max-w-none text-[#18211d]">
                <h3 className="text-lg font-bold mb-4">Role Description</h3>
                <div className="prose prose-slate max-w-none leading-relaxed text-[#48604f] prose-p:mb-4 prose-headings:text-[#18211d] prose-li:list-disc prose-li:ml-4">
                  <ReactMarkdown>{job.description}</ReactMarkdown>
                </div>
              </div>

              <div className="mt-10 border-t border-black/5 pt-8">
                <h3 className="text-lg font-bold mb-4">AI Screening Focus</h3>
                <div className="flex flex-wrap gap-3">
                  {job.scorecard_json?.criteria?.map((c: any) => (
                    <div key={c.id} className="rounded-xl bg-[#edf3ea] p-4 border border-black/5 w-full md:w-[calc(50%-0.75rem)]">
                      <p className="text-xs font-bold text-[#48604f] uppercase tracking-wider mb-1">{c.label}</p>
                      <p className="text-xs text-[#607063]">Keywords: {c.signals?.join(", ")}</p>
                    </div>
                  ))}
                </div>
              </div>
            </section>
          </div>

          {/* Application Sidebar */}
          <aside className="space-y-6">
            <section className="rounded-3xl border border-black/5 bg-white p-8 shadow-xl shadow-black/5">
              <h3 className="text-xl font-bold mb-6 italic tracking-tight">Apply Now</h3>
              
              {applySuccess ? (
                <div className="flex flex-col items-center justify-center py-6 text-center">
                  <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100 text-green-600">
                    <CheckCircle2 size={32} />
                  </div>
                  <h4 className="font-bold text-green-700">Application Submitted!</h4>
                  <p className="mt-2 text-xs text-[#607063]">Our AI is now screening your CV. You will be redirected shortly.</p>
                </div>
              ) : (
                <div className="space-y-6">
                  <div className="space-y-4">
                    <label className="group relative flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-[#d8ded5] bg-[#fbfcfa] py-10 px-4 transition-all hover:border-[#e0563f] cursor-pointer">
                      <input 
                        type="file" 
                        className="hidden" 
                        accept=".pdf,.docx" 
                        onChange={(e) => setCvFile(e.target.files?.[0] || null)}
                      />
                      <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-white shadow-sm text-[#e0563f]">
                        <FileUp size={24} />
                      </div>
                      <p className="text-sm font-bold text-center">
                        {cvFile ? cvFile.name : "Upload your CV"}
                      </p>
                      <p className="mt-1 text-[10px] text-[#607063]">PDF or DOCX (Max 5MB)</p>
                    </label>

                    {error && (
                      <div className="flex items-center gap-2 rounded-xl bg-red-50 p-3 text-[10px] font-bold text-red-600">
                        <AlertCircle size={14} />
                        {error}
                      </div>
                    )}
                  </div>

                  {showConflictDialog ? (
                    <div className="rounded-2xl border border-[#e0563f]/20 bg-[#fdf6f4] p-4">
                      <p className="text-xs font-bold text-[#e0563f] mb-3">You have already applied for this role.</p>
                      <p className="text-[10px] text-[#607063] mb-4">Would you like to replace your old CV with this new one and restart the AI screening?</p>
                      <div className="flex gap-2">
                        <button 
                          onClick={() => handleApply(true)}
                          className="flex-1 rounded-lg bg-[#e0563f] py-2 text-[10px] font-bold text-white hover:opacity-90"
                        >
                          Yes, Update CV
                        </button>
                        <button 
                          onClick={() => setShowConflictDialog(false)}
                          className="flex-1 rounded-lg border border-[#d8ded5] bg-white py-2 text-[10px] font-bold text-[#607063]"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <button
                      onClick={() => handleApply(false)}
                      disabled={!cvFile || isApplying}
                      className="w-full flex items-center justify-center gap-2 rounded-2xl bg-[#18211d] py-4 text-sm font-bold text-white shadow-lg transition-all hover:bg-[#e0563f] disabled:opacity-30 disabled:cursor-not-allowed active:scale-[0.98]"
                    >
                      {isApplying ? (
                        <Loader2 className="animate-spin" size={18} />
                      ) : (
                        <>
                          Submit Application
                          <Sparkles size={16} />
                        </>
                      )}
                    </button>
                  )}
                </div>
              )}
            </section>

            <div className="rounded-3xl bg-[#18211d] p-8 text-white">
              <h4 className="flex items-center gap-2 text-sm font-bold mb-4">
                <Sparkles size={16} className="text-[#e0563f]" />
                AI Priority Check
              </h4>
              <p className="text-xs leading-relaxed text-white/60">
                Your CV will be analyzed against the specific criteria defined for this role. Ensure your skills are clearly listed for the best match score.
              </p>
            </div>
          </aside>
        </div>
      </main>
    </div>
  );
}
