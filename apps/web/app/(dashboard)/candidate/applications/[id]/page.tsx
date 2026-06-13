"use client";

import { use, useEffect, useState } from "react";
import { useAuth } from "../../../../context/AuthContext";
import { 
  ChevronLeft, 
  Briefcase, 
  CheckCircle2, 
  Clock, 
  AlertCircle, 
  Loader2,
  Sparkles,
  FileText,
  MessageSquare,
  ArrowRight
} from "lucide-react";
import Link from "next/link";
import useSWR from "swr";
import { applicationStatusLabels } from "@talent-intelligence/shared";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:4000";
const fetcher = (url: string) => fetch(url).then(res => res.json());

export default function CandidateApplicationDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { user } = useAuth();
  
  const { data: application, isLoading: appLoading, mutate } = useSWR(`${API_BASE}/applications/${id}`, fetcher, {
    refreshInterval: (app) => (app?.status === "pending_cv" ? 3000 : 0) // Poll while screening
  });
  
  const { data: job, isLoading: jobLoading } = useSWR(
    application ? `${API_BASE}/jobs/${application.job_id}` : null, 
    fetcher
  );

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

  const isPending = application.status === "pending_cv";
  const isFailed = application.status.includes("failed");
  const isPassed = application.status === "cv_passed" || application.status.includes("test") || application.status === "accepted";

  return (
    <div className="min-h-screen bg-[#f3f5f0] text-[#18211d]">
      <header className="border-b border-black/5 bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <Link href="/candidate" className="flex items-center gap-2 text-sm font-bold text-[#607063] hover:text-[#18211d]">
            <ChevronLeft size={18} />
            Back to Dashboard
          </Link>
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-bold uppercase tracking-wider text-[#607063]">Tracking ID:</span>
            <code className="rounded bg-[#f3f5f0] px-1.5 py-0.5 text-[10px] font-bold text-[#18211d]">{id.slice(0, 8)}...</code>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-6 py-10">
        <div className="grid gap-8 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-8">
            {/* Status Hero */}
            <section className="rounded-3xl border border-black/5 bg-white p-10 shadow-sm">
              <div className="flex items-start justify-between">
                <div className="flex gap-5">
                  <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-[#f3f5f0] text-[#e0563f]">
                    <Briefcase size={32} />
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold tracking-tight">{job.title}</h1>
                    <p className="text-sm font-medium text-[#607063]">Applied on {new Date(application.created_at || Date.now()).toLocaleDateString()}</p>
                    
                    <div className="mt-6 flex items-center gap-3">
                      <span className={`inline-flex items-center gap-1.5 rounded-full px-4 py-1.5 text-xs font-bold uppercase tracking-wider ${
                        isFailed ? "bg-red-50 text-red-600" :
                        isPassed ? "bg-green-50 text-green-600" :
                        "bg-blue-50 text-blue-600"
                      }`}>
                        {applicationStatusLabels[application.status as keyof typeof applicationStatusLabels] || application.status}
                      </span>
                      {isPending && <Loader2 className="animate-spin text-[#607063]" size={16} />}
                    </div>
                  </div>
                </div>
              </div>

              {/* Progress Stepper */}
              <div className="mt-12 relative">
                <div className="absolute top-5 left-0 w-full h-0.5 bg-[#f3f5f0]" />
                <div className="relative flex justify-between">
                   <Step icon={CheckCircle2} label="CV Received" active />
                   <Step 
                    icon={Sparkles} 
                    label="AI Screening" 
                    active={isPassed || isFailed || isPending} 
                    loading={isPending}
                    completed={isPassed || isFailed}
                   />
                   <Step 
                    icon={FileText} 
                    label="Assessment" 
                    active={isPassed && application.status !== "cv_passed"} 
                    completed={application.status === "test_submitted" || application.status === "test_scored" || application.status === "accepted"}
                   />
                   <Step icon={MessageSquare} label="Interview" active={application.status === "accepted"} />
                </div>
              </div>
            </section>

            {/* AI Feedback Section */}
            {(application.cv_score || application.detailed_score_json) && (
              <section className="rounded-3xl border border-black/5 bg-white p-10 shadow-sm">
                <div className="mb-8 flex items-center justify-between">
                   <h2 className="flex items-center gap-2 text-xl font-bold">
                    <Sparkles size={22} className="text-[#e0563f]" />
                    AI Screening Feedback
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

                {application.detailed_score_json?.rationale && (
                  <div className="rounded-2xl bg-[#fbfcfa] p-6 border border-black/5">
                    <h3 className="text-sm font-bold uppercase tracking-wider text-[#607063] mb-3">AI Rationale</h3>
                    <p className="text-sm leading-relaxed text-[#48604f]">
                      {application.detailed_score_json.rationale}
                    </p>
                  </div>
                )}

                {application.detailed_score_json?.gap_analysis && (
                  <div className="mt-6">
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
              </section>
            )}
          </div>

          <aside className="space-y-6">
            {/* Action Card */}
            <section className="rounded-3xl border border-black/5 bg-[#18211d] p-8 text-white shadow-xl shadow-black/10">
              <h3 className="text-xl font-bold italic tracking-tight mb-4">Next Steps</h3>
              
              {isPending ? (
                <div className="space-y-4">
                  <p className="text-sm text-white/60 leading-relaxed">
                    Our AI agent is currently analyzing your background against the job requirements. This usually takes 30-60 seconds.
                  </p>
                  <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden">
                    <div className="h-full bg-[#e0563f] animate-progress" style={{ width: '60%' }} />
                  </div>
                </div>
              ) : application.status === "cv_passed" ? (
                <div className="space-y-6">
                  <p className="text-sm text-white/60 leading-relaxed">
                    Congratulations! Your profile is a great match. You have been invited to complete a technical assessment.
                  </p>
                  <Link 
                    href={`/candidate/assessment/${application.id}`}
                    className="flex w-full items-center justify-center gap-2 rounded-2xl bg-[#e0563f] py-4 text-sm font-bold text-white transition-transform hover:scale-[1.02] active:scale-[0.98]"
                  >
                    Start Assessment
                    <ArrowRight size={18} />
                  </Link>
                </div>
              ) : isFailed ? (
                <p className="text-sm text-white/40 italic leading-relaxed">
                  Thank you for your interest. Unfortunately, we've decided not to move forward with your application at this time.
                </p>
              ) : (
                <p className="text-sm text-white/60 leading-relaxed">
                  Please wait for further instructions from our recruiting team.
                </p>
              )}
            </section>

            <div className="rounded-3xl border border-black/5 bg-white p-8">
              <h4 className="font-bold mb-4">Need Help?</h4>
              <p className="text-xs text-[#607063] leading-relaxed">
                If you encounter any issues during the screening process, please reach out to our support team.
              </p>
            </div>
          </aside>
        </div>
      </main>

      <style jsx global>{`
        @keyframes progress {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        .animate-progress {
          animation: progress 2s infinite linear;
        }
      `}</style>
    </div>
  );
}

function Step({ icon: Icon, label, active, completed, loading }: { 
  icon: any, 
  label: string, 
  active?: boolean, 
  completed?: boolean,
  loading?: boolean 
}) {
  return (
    <div className="flex flex-col items-center gap-2 z-10">
      <div className={`flex h-10 w-10 items-center justify-center rounded-full border-2 transition-all ${
        completed ? "bg-[#e0563f] border-[#e0563f] text-white" :
        active ? "bg-white border-[#e0563f] text-[#e0563f]" :
        "bg-white border-[#f3f5f0] text-[#607063]"
      }`}>
        {loading ? <Loader2 className="animate-spin" size={18} /> : <Icon size={18} />}
      </div>
      <span className={`text-[10px] font-bold uppercase tracking-wider ${
        active || completed ? "text-[#18211d]" : "text-[#607063]"
      }`}>{label}</span>
    </div>
  );
}
