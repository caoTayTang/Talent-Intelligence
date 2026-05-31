import {
  ArrowRight,
  Bot,
  CalendarClock,
  CheckCircle2,
  FileText,
  MessageSquareText,
  Search,
  Sparkles,
  UploadCloud,
  Video
} from "lucide-react";

const candidates = [
  { name: "Ana Nguyen", role: "Backend Engineer", cv: 92, test: 88, status: "Ready to invite" },
  { name: "Minh Tran", role: "AI Engineer", cv: 86, test: 91, status: "Top match" },
  { name: "Linh Pham", role: "Product Analyst", cv: 78, test: 82, status: "Review" }
];

const steps = [
  { label: "CV Screening", value: "pending_cv", icon: FileText },
  { label: "Take-home Test", value: "cv_passed", icon: UploadCloud },
  { label: "AI Assessment", value: "test_submitted", icon: Bot },
  { label: "Interview", value: "interviewing", icon: Video }
];

export default function Home() {
  return (
    <main className="min-h-screen bg-[#f6f7f4] text-[#17201b]">
      <header className="sticky top-0 z-10 border-b border-black/10 bg-[#f6f7f4]/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4">
          <div className="flex items-center gap-3">
            <div className="grid size-9 place-items-center rounded-md bg-[#17201b] text-white">
              <Sparkles size={18} />
            </div>
            <div>
              <p className="text-sm font-semibold leading-none">Talent Intelligence</p>
              <p className="text-xs text-[#607063]">Multi-agent ATS</p>
            </div>
          </div>
          <nav className="hidden items-center gap-6 text-sm text-[#4c5b50] md:flex">
            <a href="#pipeline">Pipeline</a>
            <a href="#jobs">Jobs</a>
            <a href="#agents">Agents</a>
          </nav>
          <button className="inline-flex items-center gap-2 rounded-md bg-[#17201b] px-4 py-2 text-sm font-medium text-white">
            Open dashboard <ArrowRight size={16} />
          </button>
        </div>
      </header>

      <section className="mx-auto grid max-w-7xl gap-8 px-5 pb-10 pt-8 lg:grid-cols-[0.9fr_1.1fr] lg:pt-12">
        <div className="flex flex-col justify-center">
          <div className="mb-5 inline-flex w-fit items-center gap-2 rounded-full border border-[#cbd7c9] bg-white px-3 py-1 text-xs font-medium text-[#42604b]">
            <Bot size={14} /> Agent-gated hiring workflow
          </div>
          <h1 className="max-w-2xl text-5xl font-semibold tracking-normal text-[#17201b] md:text-7xl">
            Recruit with structured AI checkpoints.
          </h1>
          <p className="mt-5 max-w-xl text-lg leading-8 text-[#4f5f54]">
            A scaffolded ATS where candidates move through CV review, take-home assessment, interview scheduling, and transcripts through explicit application states.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <button className="inline-flex items-center gap-2 rounded-md bg-[#e0563f] px-5 py-3 text-sm font-semibold text-white">
              Create job <ArrowRight size={17} />
            </button>
            <button className="inline-flex items-center gap-2 rounded-md border border-[#c8d3c7] bg-white px-5 py-3 text-sm font-semibold text-[#17201b]">
              Browse roles <Search size={17} />
            </button>
          </div>
        </div>

        <div className="grid gap-4">
          <section className="rounded-lg border border-black/10 bg-white p-4 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold">AI Engineer</p>
                <p className="text-xs text-[#667368]">42 applicants · 11 tests unlocked</p>
              </div>
              <span className="rounded-full bg-[#eaf3e7] px-3 py-1 text-xs font-semibold text-[#376142]">Active</span>
            </div>
            <div className="grid gap-3 md:grid-cols-4">
              {steps.map((step, index) => (
                <div key={step.value} className="rounded-md border border-[#dbe3d8] bg-[#fafbf8] p-3">
                  <div className="mb-4 flex items-center justify-between">
                    <step.icon size={18} className="text-[#e0563f]" />
                    <span className="text-xs text-[#7c887e]">0{index + 1}</span>
                  </div>
                  <p className="text-sm font-semibold">{step.label}</p>
                  <p className="mt-1 text-xs text-[#667368]">{step.value}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
            <div className="rounded-lg border border-black/10 bg-white p-4 shadow-sm">
              <div className="mb-4 flex items-center justify-between">
                <p className="text-sm font-semibold">Ranked Candidates</p>
                <button className="rounded-md border border-[#d8e0d5] px-3 py-1.5 text-xs font-semibold">View all</button>
              </div>
              <div className="space-y-3">
                {candidates.map((candidate) => (
                  <div key={candidate.name} className="grid grid-cols-[1fr_auto] gap-3 rounded-md border border-[#edf0eb] p-3">
                    <div>
                      <p className="text-sm font-semibold">{candidate.name}</p>
                      <p className="text-xs text-[#69766c]">{candidate.role}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold">{candidate.test}</p>
                      <p className="text-xs text-[#69766c]">{candidate.status}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-lg border border-black/10 bg-[#17201b] p-4 text-white shadow-sm">
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold">Job Assistant</p>
                <MessageSquareText size={18} />
              </div>
              <div className="mt-5 space-y-3 text-sm">
                <div className="rounded-md bg-white/10 p-3 text-white/80">
                  Does this role require production LLM experience?
                </div>
                <div className="rounded-md bg-[#dcebd9] p-3 text-[#17201b]">
                  Yes. The JD emphasizes evaluation, retrieval, and agent workflow experience.
                </div>
              </div>
            </div>
          </section>
        </div>
      </section>

      <section id="pipeline" className="border-y border-black/10 bg-white">
        <div className="mx-auto grid max-w-7xl gap-5 px-5 py-8 md:grid-cols-3">
          <Metric label="Applications" value="128" />
          <Metric label="Agent runs" value="342" />
          <Metric label="Avg. review time" value="4m 12s" />
        </div>
      </section>

      <section id="agents" className="mx-auto grid max-w-7xl gap-4 px-5 py-10 md:grid-cols-2 lg:grid-cols-4">
        {["Manager Agent", "CV Screener", "Assessor Agent", "Transcriber"].map((agent) => (
          <div key={agent} className="rounded-lg border border-black/10 bg-white p-5">
            <CheckCircle2 className="mb-5 text-[#3c7a4b]" size={22} />
            <h2 className="text-base font-semibold">{agent}</h2>
            <p className="mt-2 text-sm leading-6 text-[#5d6b60]">
              Scaffolded behind queue workers with structured JSON outputs and auditable runs.
            </p>
          </div>
        ))}
      </section>

      <section id="jobs" className="mx-auto max-w-7xl px-5 pb-12">
        <div className="rounded-lg border border-black/10 bg-white p-5">
          <div className="mb-4 flex items-center gap-3">
            <CalendarClock className="text-[#e0563f]" size={22} />
            <h2 className="text-lg font-semibold">Next scaffold targets</h2>
          </div>
          <div className="grid gap-3 md:grid-cols-3">
            <Todo text="Wire real API endpoints into this UI" />
            <Todo text="Add presigned R2 upload flow" />
            <Todo text="Replace mocked agents with LLM calls" />
          </div>
        </div>
      </section>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-3xl font-semibold">{value}</p>
      <p className="mt-1 text-sm text-[#627066]">{label}</p>
    </div>
  );
}

function Todo({ text }: { text: string }) {
  return (
    <div className="flex items-center gap-3 rounded-md bg-[#f6f7f4] p-3 text-sm font-medium">
      <CheckCircle2 size={17} className="text-[#3c7a4b]" />
      {text}
    </div>
  );
}
