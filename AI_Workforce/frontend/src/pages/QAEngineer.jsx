
import { useState } from "react";
import { useParams } from "react-router-dom";

const API_BASE = import.meta.env.VITE_API_URL || "";

export default function QAEngineer() {
  const { projectId } = useParams();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  async function runQA() {
    if (!projectId) {
      setError("No project selected. Open QA from a project page.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(
        `${API_BASE}/api/projects/${projectId}/qa/run`,
        {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "QA execution failed.");
      }

      setResult(data);
    } catch (err) {
      setError(err.message || "Unable to run QA.");
    } finally {
      setLoading(false);
    }
  }

  const report = result?.report;

  return (
    <main className="mx-auto max-w-6xl space-y-6 p-6">
      <header>
        <h1 className="text-3xl font-bold">QA Engineer</h1>
        <p className="mt-2 text-gray-500">
          Run project tests, review results, and inspect detected defects.
        </p>
      </header>

      <section className="rounded-xl border p-5">
        <p className="mb-4 text-sm text-gray-600">
          Project ID: {projectId || "Not selected"}
        </p>

        <button
          onClick={runQA}
          disabled={loading || !projectId}
          className="rounded-lg bg-blue-600 px-5 py-3 font-medium text-white disabled:opacity-50"
        >
          {loading ? "Running QA..." : "Run QA Tests"}
        </button>

        {error && (
          <p role="alert" className="mt-4 text-red-600">
            {error}
          </p>
        )}
      </section>

      {report && (
        <section className="rounded-xl border p-5">
          <h2 className="text-xl font-semibold">QA Summary</h2>

          <p className="mt-3">
            Status: <strong>{report.status}</strong>
          </p>

          <div className="mt-4 grid grid-cols-2 gap-4 md:grid-cols-4">
            <Metric label="Total" value={report.total} />
            <Metric label="Passed" value={report.passed} />
            <Metric label="Failed" value={report.failed} />
            <Metric label="Skipped" value={report.skipped} />
          </div>

          <p className="mt-4 text-gray-600">{report.summary}</p>

          {report.test_results?.map((test) => (
            <article key={test.test_id} className="mt-4 rounded-lg bg-gray-50 p-4">
              <h3 className="font-semibold">
                {test.test_id} — {test.status}
              </h3>
              <pre className="mt-2 whitespace-pre-wrap break-words text-sm">
                {test.actual_result}
              </pre>
              {test.error_message && (
                <p className="mt-2 text-red-600">{test.error_message}</p>
              )}
            </article>
          ))}
        </section>
      )}

      {result?.test_plan && (
        <section className="rounded-xl border p-5">
          <h2 className="text-xl font-semibold">Generated Test Plan</h2>
          <p className="mt-2 text-gray-600">
            {result.test_plan.summary}
          </p>

          <div className="mt-4 space-y-3">
            {result.test_plan.test_cases?.map((test) => (
              <article key={test.test_id} className="rounded-lg border p-4">
                <h3 className="font-semibold">
                  {test.test_id}: {test.title}
                </h3>
                <p className="mt-1 text-sm text-gray-500">
                  {test.category} · Priority: {test.priority}
                </p>
                <p className="mt-2">{test.description}</p>
                <p className="mt-2 text-sm">
                  <strong>Expected:</strong> {test.expected_result}
                </p>
              </article>
            ))}
          </div>
        </section>
      )}

      {result?.defect_analysis && (
        <section className="rounded-xl border p-5">
          <h2 className="text-xl font-semibold">Defect Analysis</h2>
          <p className="mt-2">{result.defect_analysis.summary}</p>

          {result.defect_analysis.defects?.length ? (
            result.defect_analysis.defects.map((defect, index) => (
              <article key={`${defect.title}-${index}`} className="mt-4 rounded-lg border p-4">
                <h3 className="font-semibold">{defect.title}</h3>
                <p className="mt-1 text-sm">
                  Severity: <strong>{defect.severity}</strong>
                </p>
                <p className="mt-2">{defect.description}</p>
                <p className="mt-2">
                  <strong>Likely cause:</strong> {defect.likely_root_cause}
                </p>
                <p className="mt-2">
                  <strong>Suggested fix:</strong> {defect.suggested_fix}
                </p>
              </article>
            ))
          ) : (
            <p className="mt-3 text-gray-500">No defects were reported.</p>
          )}
        </section>
      )}
    </main>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-lg bg-gray-50 p-4">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="mt-1 text-2xl font-bold">{value}</p>
    </div>
  );
}
