"use client";

import { ChangeEvent, useEffect, useMemo, useState } from "react";
import {
  AlertCircle,
  BriefcaseBusiness,
  Building2,
  CheckCircle2,
  ClipboardList,
  Database,
  FileUp,
  Loader2,
  Play,
  RefreshCw,
  UserRound,
} from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:4000";

const DEFAULT_JD = `# Job Description: Backend AI Engineer - Talent Intelligence Platform

## Company
Northstar Talent Labs builds AI-assisted recruiting tools for HR teams. The product helps recruiters screen candidates, generate assessments, schedule interviews, and summarize interview evidence.

## Role Summary
We are hiring a Backend AI Engineer to build production-grade backend services and agent workflows for a multi-agent talent intelligence platform. The engineer will work on FastAPI services, PostgreSQL/pgvector storage, RabbitMQ/Celery workers, Cloudflare R2 file handling, and LangGraph-based agent orchestration.

## Responsibilities

- Build and maintain FastAPI backend endpoints for candidate, job, application, and agent workflows.
- Design asynchronous worker pipelines with RabbitMQ and Celery.
- Implement RAG pipelines using PostgreSQL, pgvector, and embedding models.
- Build LangGraph workflows for CV screening, assessment scoring, transcription, and interview summaries.
- Integrate Cloudflare R2 for secure file upload/download flows.
- Write clean SQLAlchemy models, Alembic migrations, and production-ready data access code.
- Package services with Docker and support deployment to EC2 or Kubernetes.
- Add structured logging, retries, and failure-handling patterns for background jobs.

## Required Skills

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- pgvector
- RabbitMQ
- Celery
- LangGraph
- RAG
- Docker
- Kubernetes
- AWS

## Nice To Have

- Next.js or React experience
- Cloudflare R2 or S3-compatible object storage
- OpenRouter or OpenAI API integration
- Tavily or other web search tools
- Experience with CI/CD and GitHub Actions

## Minimum Qualifications

- 2+ years backend engineering experience or strong project evidence.
- Experience building production APIs and asynchronous workers.
- Comfortable debugging distributed systems and reading logs.
- Can explain tradeoffs clearly and write maintainable code.

## Screening Rubric

- Backend API and ORM depth: 25%
- Async worker and queue experience: 20%
- RAG/vector database experience: 20%
- Agent orchestration experience: 15%
- Deployment/DevOps experience: 10%
- Communication and evidence quality: 10%
`;

const DEFAULT_SCORECARD = {
  criteria: [
    {
      id: "backend_api_orm",
      label: "Backend API and ORM depth",
      weight: 25,
      signals: ["FastAPI", "SQLAlchemy", "PostgreSQL", "Alembic"],
    },
    {
      id: "async_workers",
      label: "Async worker and queue experience",
      weight: 20,
      signals: ["RabbitMQ", "Celery", "retry", "DLQ"],
    },
    {
      id: "rag_vectors",
      label: "RAG and vector database experience",
      weight: 20,
      signals: ["RAG", "pgvector", "embeddings", "semantic search"],
    },
    {
      id: "agent_orchestration",
      label: "Agent orchestration experience",
      weight: 15,
      signals: ["LangGraph", "ReAct", "tool calling", "evidence review"],
    },
    {
      id: "deployment",
      label: "Deployment and DevOps experience",
      weight: 10,
      signals: ["Docker", "Kubernetes", "AWS", "GitHub Actions"],
    },
    {
      id: "communication",
      label: "Communication and evidence quality",
      weight: 10,
      signals: ["clear project evidence", "structured explanations"],
    },
  ],
};

type Entity = { id: string; [key: string]: unknown };
type Application = {
  id: string;
  candidate_id: string;
  job_id: string;
  status: string;
  cv_object_key?: string;
  cv_score?: number | null;
  detailed_score_json?: ScreeningOutput | null;
};

type ScreeningOutput = {
  cv_score?: number;
  decision?: string;
  decision_band?: string;
  reasons?: string[];
  gap_analysis?: string;
  criterion_scores?: Array<{
    criterion_id: string;
    label: string;
    raw_score: number;
    weighted_score: number;
    matched_signals: string[];
    missing_signals: string[];
    rationale: string;
  }>;
  evidence?: Array<{
    id: string;
    grade: string;
    source: string;
    claim: string;
    confidence: number;
    url?: string | null;
    notes?: string[];
  }>;
  tool_trace?: Array<{
    tool: string;
    input_summary: string;
    output_summary: string;
    error?: string | null;
  }>;
  errors?: string[];
};

type LogItem = { tone: "info" | "ok" | "error"; text: string };

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`${response.status} ${response.statusText}: ${body}`);
  }
  return response.json() as Promise<T>;
}

function uniqueEmail(prefix: string) {
  return `${prefix}.${Date.now()}@example.dev`;
}

export default function Home() {
  const [companyName, setCompanyName] = useState("Northstar Talent Labs");
  const [candidateName, setCandidateName] = useState("Daniel Pham");
  const [candidateEmail, setCandidateEmail] = useState(() => uniqueEmail("candidate"));
  const [jobTitle, setJobTitle] = useState("Backend AI Engineer - Talent Intelligence Platform");
  const [jdText, setJdText] = useState(DEFAULT_JD);
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [manualCvKey, setManualCvKey] = useState("");

  const [company, setCompany] = useState<Entity | null>(null);
  const [candidate, setCandidate] = useState<Entity | null>(null);
  const [job, setJob] = useState<Entity | null>(null);
  const [application, setApplication] = useState<Application | null>(null);
  const [logs, setLogs] = useState<LogItem[]>([]);
  const [busy, setBusy] = useState(false);
  const [polling, setPolling] = useState(false);

  const result = application?.detailed_score_json ?? null;
  const canRun = Boolean(company && candidate && job && (manualCvKey || cvFile));

  const summaryCards = useMemo(
    () => [
      { label: "Company", value: company?.id ? "created" : "empty", icon: Building2 },
      { label: "Candidate", value: candidate?.id ? "created" : "empty", icon: UserRound },
      { label: "Job", value: job?.id ? "created" : "empty", icon: BriefcaseBusiness },
      { label: "Screening", value: application?.status ?? "not started", icon: ClipboardList },
    ],
    [application?.status, candidate, company, job]
  );

  function addLog(text: string, tone: LogItem["tone"] = "info") {
    setLogs((items) => [{ text, tone }, ...items].slice(0, 12));
  }

  async function createCompany() {
    const created = await api<Entity>("/companies", {
      method: "POST",
      body: JSON.stringify({ name: companyName, logo_url: null, website: "https://northstar.example" }),
    });
    setCompany(created);
    addLog(`Company created: ${created.id}`, "ok");
    return created;
  }

  async function createCandidate() {
    const created = await api<Entity>("/users", {
      method: "POST",
      body: JSON.stringify({ name: candidateName, email: candidateEmail, role: "candidate" }),
    });
    setCandidate(created);
    addLog(`Candidate created: ${created.id}`, "ok");
    return created;
  }

  async function createJob(companyId = company?.id) {
    if (!companyId) throw new Error("Create a company first.");
    const created = await api<Entity>("/jobs", {
      method: "POST",
      body: JSON.stringify({
        company_id: companyId,
        title: jobTitle,
        description: jdText,
        test_content: null,
        test_object_url: null,
        scorecard_json: DEFAULT_SCORECARD,
        jd_object_url: null,
        is_active: true,
      }),
    });
    setJob(created);
    addLog(`Job created: ${created.id}`, "ok");
    return created;
  }

  async function uploadCv(): Promise<string> {
    if (manualCvKey.trim()) {
      addLog(`Using CV object key: ${manualCvKey.trim()}`, "info");
      return manualCvKey.trim();
    }
    if (!cvFile) throw new Error("Choose a CV file or paste an R2 object key.");
    const presign = await api<{ object_key: string; upload_url: string }>("/uploads/presign", {
      method: "POST",
      body: JSON.stringify({
        kind: "cv",
        file_name: cvFile.name,
        content_type: cvFile.type || "application/pdf",
      }),
    });
    const upload = await fetch(presign.upload_url, {
      method: "PUT",
      headers: { "Content-Type": cvFile.type || "application/pdf" },
      body: cvFile,
    });
    if (!upload.ok) throw new Error(`R2 upload failed: ${upload.status} ${upload.statusText}`);
    setManualCvKey(presign.object_key);
    addLog(`CV uploaded: ${presign.object_key}`, "ok");
    return presign.object_key;
  }

  async function createApplication(candidateId = candidate?.id, jobId = job?.id) {
    if (!candidateId || !jobId) throw new Error("Create candidate and job first.");
    const cvObjectKey = await uploadCv();
    const created = await api<Application>("/applications", {
      method: "POST",
      body: JSON.stringify({ candidate_id: candidateId, job_id: jobId, cv_object_key: cvObjectKey }),
    });
    setApplication(created);
    setPolling(true);
    addLog(`Application created and queued: ${created.id}`, "ok");
    return created;
  }

  async function runFullFlow() {
    setBusy(true);
    try {
      const companyRow = company ?? (await createCompany());
      const candidateRow = candidate ?? (await createCandidate());
      const jobRow = job ?? (await createJob(companyRow.id));
      await createApplication(candidateRow.id, jobRow.id);
    } catch (error) {
      addLog(error instanceof Error ? error.message : String(error), "error");
    } finally {
      setBusy(false);
    }
  }

  async function refreshApplication() {
    if (!application?.id) return;
    try {
      const fresh = await api<Application>(`/applications/${application.id}`);
      setApplication(fresh);
      if (fresh.detailed_score_json) {
        setPolling(false);
        addLog(`Screening finished: ${fresh.detailed_score_json.decision_band ?? fresh.status}`, "ok");
      }
    } catch (error) {
      addLog(error instanceof Error ? error.message : String(error), "error");
    }
  }

  useEffect(() => {
    if (!polling || !application?.id) return undefined;
    const timer = window.setInterval(refreshApplication, 2500);
    return () => window.clearInterval(timer);
  }, [polling, application?.id]);

  function onFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0] ?? null;
    setCvFile(file);
    if (file) addLog(`Selected ${file.name}`, "info");
  }

  return (
    <main className="min-h-screen bg-[#f3f5f0] text-[#18211d]">
      <header className="border-b border-black/10 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4">
          <div>
            <p className="text-sm font-semibold text-[#e0563f]">Talent Intelligence</p>
            <h1 className="text-2xl font-semibold tracking-normal">CV Screening Console</h1>
          </div>
          <div className="flex items-center gap-2 text-sm text-[#607063]">
            <Database size={17} /> {API_BASE}
          </div>
        </div>
      </header>

      <section className="mx-auto grid max-w-7xl gap-5 px-5 py-5 lg:grid-cols-4">
        {summaryCards.map((card) => (
          <div key={card.label} className="rounded-lg border border-black/10 bg-white p-4 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <card.icon size={20} className="text-[#e0563f]" />
              <span className="rounded-full bg-[#edf3ea] px-2 py-1 text-xs font-semibold text-[#48604f]">{card.value}</span>
            </div>
            <p className="text-sm font-semibold">{card.label}</p>
          </div>
        ))}
      </section>

      <section className="mx-auto grid max-w-7xl gap-5 px-5 pb-8 lg:grid-cols-[0.95fr_1.05fr]">
        <div className="space-y-5">
          <Panel title="Seed Records" icon={Building2}>
            <div className="grid gap-3 md:grid-cols-2">
              <Field label="Company name" value={companyName} onChange={setCompanyName} />
              <Field label="Candidate name" value={candidateName} onChange={setCandidateName} />
              <Field label="Candidate email" value={candidateEmail} onChange={setCandidateEmail} />
              <Field label="Job title" value={jobTitle} onChange={setJobTitle} />
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              <ActionButton onClick={() => createCompany().catch((error) => addLog(error.message, "error"))} disabled={busy} icon={Building2}>Company</ActionButton>
              <ActionButton onClick={() => createCandidate().catch((error) => addLog(error.message, "error"))} disabled={busy} icon={UserRound}>Candidate</ActionButton>
              <ActionButton onClick={() => createJob().catch((error) => addLog(error.message, "error"))} disabled={busy || !company} icon={BriefcaseBusiness}>Job</ActionButton>
            </div>
          </Panel>

          <Panel title="Job Description" icon={ClipboardList}>
            <textarea
              className="min-h-[260px] w-full resize-y rounded-md border border-[#d8ded5] bg-[#fbfcfa] p-3 font-mono text-xs leading-5 outline-none focus:border-[#e0563f]"
              value={jdText}
              onChange={(event) => setJdText(event.target.value)}
            />
          </Panel>

          <Panel title="CV Input" icon={FileUp}>
            <div className="grid gap-3 md:grid-cols-2">
              <label className="rounded-md border border-dashed border-[#c7d1c4] bg-[#fbfcfa] p-4">
                <span className="mb-2 block text-sm font-semibold">Upload PDF/DOCX</span>
                <input type="file" accept=".pdf,.docx,.txt" onChange={onFileChange} className="block w-full text-sm" />
                <span className="mt-2 block text-xs text-[#667368]">{cvFile?.name ?? "No file selected"}</span>
              </label>
              <div>
                <label className="mb-2 block text-sm font-semibold">Or paste R2 object key</label>
                <input
                  className="w-full rounded-md border border-[#d8ded5] bg-white px-3 py-2 text-sm outline-none focus:border-[#e0563f]"
                  placeholder="cv/<uuid>/resume.pdf"
                  value={manualCvKey}
                  onChange={(event) => setManualCvKey(event.target.value)}
                />
              </div>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              <button
                onClick={runFullFlow}
                disabled={busy || (!canRun && Boolean(company || candidate || job))}
                className="inline-flex items-center gap-2 rounded-md bg-[#e0563f] px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
              >
                {busy ? <Loader2 size={17} className="animate-spin" /> : <Play size={17} />} Create + Queue Screening
              </button>
              <button
                onClick={refreshApplication}
                disabled={!application?.id}
                className="inline-flex items-center gap-2 rounded-md border border-[#cbd5c8] bg-white px-4 py-2 text-sm font-semibold disabled:opacity-50"
              >
                <RefreshCw size={17} /> Refresh
              </button>
            </div>
          </Panel>
        </div>

        <div className="space-y-5">
          <Panel title="Run State" icon={CheckCircle2}>
            <div className="grid gap-3 md:grid-cols-2">
              <IdRow label="Company" value={company?.id as string | undefined} />
              <IdRow label="Candidate" value={candidate?.id as string | undefined} />
              <IdRow label="Job" value={job?.id as string | undefined} />
              <IdRow label="Application" value={application?.id} />
            </div>
            {polling && (
              <div className="mt-4 flex items-center gap-2 rounded-md bg-[#fff7ed] px-3 py-2 text-sm font-medium text-[#9a4d12]">
                <Loader2 size={16} className="animate-spin" /> Waiting for worker result
              </div>
            )}
          </Panel>

          <Panel title="Screening Result" icon={ClipboardList}>
            {!result ? (
              <EmptyState />
            ) : (
              <div className="space-y-4">
                <div className="grid gap-3 md:grid-cols-3">
                  <Metric label="Score" value={String(result.cv_score ?? "-")} />
                  <Metric label="Decision" value={result.decision_band ?? result.decision ?? "-"} />
                  <Metric label="Errors" value={String(result.errors?.length ?? 0)} />
                </div>
                <ResultSection title="Criterion Scores">
                  <div className="space-y-2">
                    {result.criterion_scores?.map((item) => (
                      <div key={item.criterion_id} className="rounded-md border border-[#e0e6dd] bg-[#fbfcfa] p-3">
                        <div className="flex items-center justify-between gap-3">
                          <p className="text-sm font-semibold">{item.label}</p>
                          <span className="rounded-full bg-[#17201b] px-2 py-1 text-xs font-semibold text-white">{item.raw_score}/100</span>
                        </div>
                        <p className="mt-2 text-xs leading-5 text-[#667368]">{item.rationale}</p>
                      </div>
                    ))}
                  </div>
                </ResultSection>
                <ResultSection title="Evidence Grades">
                  <div className="grid gap-2 md:grid-cols-2">
                    {result.evidence?.slice(0, 8).map((item) => (
                      <div key={item.id} className="rounded-md border border-[#e0e6dd] bg-white p-3">
                        <div className="mb-2 flex items-center justify-between">
                          <span className="text-xs font-semibold uppercase text-[#e0563f]">{item.grade}</span>
                          <span className="text-xs text-[#667368]">{item.source}</span>
                        </div>
                        <p className="text-sm font-medium leading-5">{item.claim}</p>
                        {item.url && <p className="mt-2 break-all text-xs text-[#48604f]">{item.url}</p>}
                      </div>
                    ))}
                  </div>
                </ResultSection>
                <ResultSection title="Trace">
                  <div className="space-y-2">
                    {result.tool_trace?.map((item) => (
                      <div key={`${item.tool}-${item.output_summary}`} className="rounded-md bg-[#f4f6f2] px-3 py-2 text-xs">
                        <span className="font-semibold">{item.tool}</span> - {item.output_summary}
                        {item.error && <span className="ml-2 text-[#b42318]">{item.error}</span>}
                      </div>
                    ))}
                  </div>
                </ResultSection>
              </div>
            )}
          </Panel>

          <Panel title="Event Log" icon={AlertCircle}>
            <div className="space-y-2">
              {logs.length === 0 && <p className="text-sm text-[#667368]">No events yet.</p>}
              {logs.map((item, index) => (
                <div key={`${item.text}-${index}`} className={`rounded-md px-3 py-2 text-xs ${item.tone === "error" ? "bg-[#fef2f2] text-[#b42318]" : item.tone === "ok" ? "bg-[#ecfdf3] text-[#067647]" : "bg-[#f4f6f2] text-[#4f5f54]"}`}>
                  {item.text}
                </div>
              ))}
            </div>
          </Panel>
        </div>
      </section>
    </main>
  );
}

function Panel({ title, icon: Icon, children }: { title: string; icon: typeof Building2; children: React.ReactNode }) {
  return (
    <section className="rounded-lg border border-black/10 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center gap-3">
        <div className="grid size-9 place-items-center rounded-md bg-[#17201b] text-white"><Icon size={18} /></div>
        <h2 className="text-base font-semibold">{title}</h2>
      </div>
      {children}
    </section>
  );
}

function Field({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <label>
      <span className="mb-1 block text-xs font-semibold uppercase tracking-wide text-[#607063]">{label}</span>
      <input className="w-full rounded-md border border-[#d8ded5] bg-white px-3 py-2 text-sm outline-none focus:border-[#e0563f]" value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function ActionButton({ children, icon: Icon, disabled, onClick }: { children: React.ReactNode; icon: typeof Building2; disabled?: boolean; onClick: () => void }) {
  return <button onClick={onClick} disabled={disabled} className="inline-flex items-center gap-2 rounded-md border border-[#cbd5c8] bg-white px-3 py-2 text-sm font-semibold disabled:opacity-50"><Icon size={16} />{children}</button>;
}

function IdRow({ label, value }: { label: string; value?: string }) {
  return <div className="rounded-md bg-[#f6f7f4] p-3"><p className="text-xs font-semibold text-[#607063]">{label}</p><p className="mt-1 break-all font-mono text-xs">{value ?? "-"}</p></div>;
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div className="rounded-md bg-[#17201b] p-3 text-white"><p className="text-xs text-white/60">{label}</p><p className="mt-1 text-xl font-semibold">{value}</p></div>;
}

function ResultSection({ title, children }: { title: string; children: React.ReactNode }) {
  return <section><h3 className="mb-2 text-sm font-semibold">{title}</h3>{children}</section>;
}

function EmptyState() {
  return <div className="rounded-md border border-dashed border-[#cbd5c8] bg-[#fbfcfa] p-6 text-center text-sm text-[#667368]">Create an application and wait for the worker result.</div>;
}
