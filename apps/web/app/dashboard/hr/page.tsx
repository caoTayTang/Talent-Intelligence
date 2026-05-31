import { applicationStatusLabels } from "@talent-intelligence/shared";

const rows = [
  { name: "Minh Tran", cv: 86, test: 91, status: "test_scored" },
  { name: "Ana Nguyen", cv: 92, test: 88, status: "test_scored" },
  { name: "Linh Pham", cv: 78, test: 82, status: "test_scored" },
  { name: "Nam Le", cv: 64, test: null, status: "cv_failed" }
] as const;

export default function HrDashboardPage() {
  return (
    <main className="min-h-screen bg-[#f6f7f4] p-6 text-[#17201b]">
      <div className="mx-auto max-w-6xl">
        <h1 className="text-3xl font-semibold">HR Dashboard</h1>
        <p className="mt-2 text-[#5d6b60]">Ranked applicants and current gate status.</p>
        <div className="mt-6 overflow-hidden rounded-lg border border-black/10 bg-white">
          <table className="w-full border-collapse text-left text-sm">
            <thead className="bg-[#17201b] text-white">
              <tr>
                <th className="p-4">Candidate</th>
                <th className="p-4">CV</th>
                <th className="p-4">Test</th>
                <th className="p-4">Status</th>
                <th className="p-4">Action</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.name} className="border-t border-black/10">
                  <td className="p-4 font-medium">{row.name}</td>
                  <td className="p-4">{row.cv}</td>
                  <td className="p-4">{row.test ?? "-"}</td>
                  <td className="p-4">{applicationStatusLabels[row.status]}</td>
                  <td className="p-4">
                    <button className="rounded-md bg-[#e0563f] px-3 py-2 text-xs font-semibold text-white">
                      Invite
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  );
}
