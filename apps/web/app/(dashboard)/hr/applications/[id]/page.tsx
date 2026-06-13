"use client";

import { use, useEffect, useState } from "react";
import { useAuth } from "../../../../context/AuthContext";
import { 
  ChevronLeft, 
  Briefcase, 
  User, 
  Mail, 
  FileText, 
  Sparkles, 
  AlertCircle, 
  CheckCircle2, 
  XCircle,
  Loader2,
  ExternalLink,
  Download,
  ClipboardCheck
} from "lucide-react";
import Link from "next/link";
import useSWR from "swr";
import { applicationStatusLabels } from "@talent-intelligence/shared";
import { HrSidebar } from "../../../../components/HrSidebar";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:4000";
const fetcher = (url: string) => fetch(url).then(res => res.json());

export default function HrApplicationDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { user } = useAuth();
  
  const { data: application, isLoading: appLoading } = useSWR(`${API_BASE}/applications/${id}`, fetcher);
  const { data: job, isLoading: jobLoading } = useSWR(
    application ? `${API_BASE}/jobs/${application.job_id}` : null, 
    fetcher
  );

  const [cvDownloadUrl, setCvDownloadUrl] = useState<string | null>(null);

  useEffect(() => {
    if (application?.cv_object_key) {
      // In a real app, we'd fetch a signed download URL from the API
      fetch(`${API_BASE}/uploads/download/${application.cv_object_key}`)
        .then(res => res.json())
        .then(data => setCvDownloadUrl(data.download_url))
        .catch(err => console.error("Failed to fetch CV download URL", err));
    }
  }, [application]);

  if (appLoading || jobLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#f3f5f0]">
        <Loader2 className="animate-spin text-[#e0563f]" size={40} />
      </div>
    );
  }

  if (!application || !job) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#f3f5f0]">
        <p className="font-bold text-[#607063]">Application not found.</p>
      </div>
    );
  }

  const isFailed = application.status.includes("failed");
  const isPassed = application.status === "cv_passed" || application.status.includes("test") || application.status === "accepted";

  return (
    <div className="flex min-h-screen bg-[#f3f5f0] text-[#18211d]">
      <HrSidebar />

      <main className="ml-64 flex-1 p-10">
        <header className="mb-8 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/hr" className="text-[#607063] hover:text-[#18211d]">
              <ChevronLeft size={24} />
            </Link>
            <div>
              <h1 className="text-2xl font-bold">{application.candidate_name || "New Candidate"}</h1>
              <p className="text-sm text-[#607063]">Applied for <span className="font-bold text-[#18211d]">{job.title}</span></p>
            </div>
          </div>
          
          <div className="flex gap-3">
             <button className="rounded-xl border border-[#d8ded5] bg-white px-5 py-2.5 text-sm font-bold text-[#607063] hover:bg-[#f3f5f0]">
                Reject Candidate
             </button>
             <button className="rounded-xl bg-[#e0563f] px-5 py-2.5 text-sm font-bold text-white shadow-lg shadow-[#e0563f]/20 hover:opacity-90">
                Advance to Interview
             </button>
          </div>
        </header>

        <div className="grid gap-8 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-8">
            {/* Candidate Identity */}
            <section className="rounded-3xl border border-black/5 bg-white p-8 shadow-sm">
              <h2 className="mb-6 text-lg font-bold flex items-center gap-2">
                <User size={20} className="text-[#e0563f]" />
                Candidate Profile
              </h2>
              <div className="grid gap-6 md:grid-cols-2">
                 <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#f3f5f0] text-[#607063]">
                       <Mail size={18} />
                    </div>
                    <div>
                       <p className="text-[10px] font-bold uppercase text-[#607063]">Email Address</p>
                       <p className="text-sm font-medium">{application.candidate_email || "N/A"}</p>
                    </div>
                 </div>
                 <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#f3f5f0] text-[#607063]">
                       <FileText size={18} />
                    </div>
                    <div>
                       <p className="text-[10px] font-bold uppercase text-[#607063]">Resume / CV</p>
                       {cvDownloadUrl ? (
                         <a href={cvDownloadUrl} target="_blank" className="text-sm font-bold text-[#e0563f] hover:underline flex items-center gap-1">
                            View Document <ExternalLink size={12} />
                         </a>
                       ) : (
                         <p className="text-sm text-[#607063] italic">Loading...</p>
                       )}
                    </div>
                 </div>
              </div>
            </section>

            {/* AI Screening Insight */}
            {application.cv_score !== null && (
              <section className="rounded-3xl border border-black/5 bg-white p-10 shadow-sm">
                <div className="mb-8 flex items-center justify-between">
                  <h2 className="flex items-center gap-2 text-xl font-bold">
                    <Sparkles size={22} className="text-[#e0563f]" />
                    AI Screening Report
                  </h2>
                  <div className={`flex items-center gap-2 rounded-2xl px-4 py-2 text-lg font-black ${
                      application.cv_score >= 80 ? "bg-green-50 text-green-700" :
                      application.cv_score >= 60 ? "bg-yellow-50 text-yellow-700" :
                      "bg-red-50 text-red-700"
                   }`}>
                      {application.cv_score}%
                      <span className="text-[10px] font-bold uppercase tracking-tight text-black/30 ml-1">Match Score</span>
                   </div>
                </div>

                <div className="space-y-6">
                  {application.detailed_score_json?.rationale && (
                    <div className="rounded-2xl bg-[#fbfcfa] p-6 border border-black/5">
                      <h3 className="text-sm font-bold uppercase tracking-wider text-[#607063] mb-3 flex items-center gap-2">
                        <ClipboardCheck size={16} />
                        AI Executive Summary
                      </h3>
                      <p className="text-sm leading-relaxed text-[#48604f]">
                        {application.detailed_score_json.rationale}
                      </p>
                    </div>
                  )}

                  {application.detailed_score_json?.gap_analysis && (
                    <div>
                      <h3 className="text-sm font-bold uppercase tracking-wider text-[#607063] mb-4 pl-1">Gap Analysis</h3>
                      <div className="space-y-3">
                        {Array.isArray(application.detailed_score_json.gap_analysis) ? (
                          application.detailed_score_json.gap_analysis.map((gap: string, idx: number) => (
                            <div key={idx} className="flex gap-3 items-start p-4 rounded-xl border border-black/5 bg-white">
                              <AlertCircle size={16} className="text-[#e0563f] mt-0.5 shrink-0" />
                              <p className="text-sm font-medium text-[#48604f]">{gap}</p>
                            </div>
                          ))
                        ) : (
                          <div className="flex gap-3 items-start p-4 rounded-xl border border-black/5 bg-white">
                            <AlertCircle size={16} className="text-[#e0563f] mt-0.5 shrink-0" />
                            <p className="text-sm font-medium text-[#48604f]">
                              {String(application.detailed_score_json.gap_analysis)}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </section>
            )}
          </div>

          <aside className="space-y-6">
            <section className="rounded-3xl border border-black/5 bg-white p-8 shadow-sm">
              <h3 className="text-lg font-bold mb-6">Application Status</h3>
              <div className="space-y-4">
                 <div className="flex items-center justify-between">
                    <span className="text-xs font-medium text-[#607063]">Current Stage</span>
                    <span className={`rounded-full px-3 py-1 text-[10px] font-bold uppercase tracking-wider ${
                        isFailed ? "bg-red-50 text-red-600" :
                        isPassed ? "bg-green-50 text-green-600" :
                        "bg-blue-50 text-blue-600"
                      }`}>
                        {applicationStatusLabels[application.status as keyof typeof applicationStatusLabels] || application.status}
                    </span>
                 </div>
                 <div className="flex items-center justify-between">
                    <span className="text-xs font-medium text-[#607063]">Days in Pipeline</span>
                    <span className="text-xs font-bold">2 days</span>
                 </div>
              </div>
            </section>

            <section className="rounded-3xl bg-[#18211d] p-8 text-white">
              <h3 className="text-lg font-bold italic tracking-tight mb-4">Recruiter Note</h3>
              <textarea 
                placeholder="Add a private note about this candidate..."
                className="w-full rounded-xl bg-white/5 border border-white/10 p-4 text-xs outline-none focus:border-[#e0563f] min-h-[120px]"
              />
              <button className="mt-4 w-full rounded-xl bg-white py-2.5 text-[10px] font-bold text-[#18211d] hover:bg-[#e0563f] hover:text-white transition-colors">
                Save Internal Note
              </button>
            </section>
          </aside>
        </div>
      </main>
    </div>
  );
}
