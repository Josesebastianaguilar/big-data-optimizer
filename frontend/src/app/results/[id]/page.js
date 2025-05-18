"use client";

import Link from "next/link";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { FaArrowLeft } from "react-icons/fa";

// Mock process and results data (replace with real fetch)
const process = {
  _id: 1,
  task_process: "filter", // "filter" | "group" | "aggregation"
  process_id: "P-001",
  status: "Completed",
  repository: {
    _id: 1,
    name: "Repository A",
    version: "1.0.0",
    parameters: [
      { name: "filter", type: "string" },
      { name: "limit", type: "number" },
      { name: "category", type: "string" },
    ],
  },
  // Example results for each type:
  results: [
    // For "filter":
    { _id: 1, filter: "active", limit: 100, category: "A" }
    // For "group":
    // "A": [{ _id: 1, filter: "active", limit: 100, category: "A" }],
    // "B": [{ _id: 2, filter: "active", limit: 100, category: "A" }]
    // For "aggregation":
    // { parameter: "limit", metric: "sum", value: 225 },
    // { parameter: "limit", metric: "mean", value: 75 },
    // { parameter: "limit", metric: "max", value: 100 },
    // { parameter: "limit", metric: "min", value: 50 },
    // { parameter: "limit", metric: "count", value: 3 },
    // { parameter: "category", metric: "unique", value: 3 },
  ],
};

export default function ProcessResultsView() {
  const { task_process, repository, results } = process;

  // Helper: render records table
  const renderRecordsTable = (records) => (
    <table className="min-w-full bg-white border border-gray-300 rounded-lg shadow-md mb-6">
      <thead>
        <tr className="bg-slate-500 text-white">
          {repository.parameters.map((param) => (
            <th key={param.name} className="px-4 py-2 text-left text-sm font-semibold">
              {param.name}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {records.map((record) => (
          <tr key={record._id} className="hover:bg-gray-100">
            {repository.parameters.map((param) => (
              <td key={param.name} className="px-4 py-2 text-sm text-gray-800">
                {record[param.name]}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );

  // Helper: render aggregation table
  const renderAggregationTable = () => (
    <table className="min-w-full bg-white border border-gray-300 rounded-lg shadow-md mb-6">
      <thead>
        <tr className="bg-slate-500 text-white">
          <th className="px-4 py-2 text-left text-sm font-semibold">Parameter</th>
          <th className="px-4 py-2 text-left text-sm font-semibold">Metric</th>
          <th className="px-4 py-2 text-left text-sm font-semibold">Value</th>
        </tr>
      </thead>
      <tbody>
        {results.map((agg, idx) => (
          <tr key={idx} className="hover:bg-gray-100">
            <td className="px-4 py-2 text-sm text-gray-800">{agg.parameter}</td>
            <td className="px-4 py-2 text-sm text-gray-800">{agg.metric}</td>
            <td className="px-4 py-2 text-sm text-gray-800">{agg.value}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );

  // Helper: render group results
  const renderGroupResults = () => (
    <div className="space-y-8">
      {Object.keys(results).map((group_key, index) => (
        <div key={`${group_key}_${index}`} className="border rounded-lg p-4 bg-orange-50">
          <div className="font-semibold mb-2">
            {group_key}
          </div>
          {renderRecordsTable(results[group_key])}
        </div>
      ))}
    </div>
  );

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 text-gray-800">
      <Header backgroundColor="bg-slate-500" title="Process Results" />
      <main className="flex-grow max-w-4xl mx-auto w-full px-4 py-8">
        <div className="flex justify-end items-center mb-6">
          <Link
              title="Go Back"
              href={`/processes/${process._id}`}
              className="inline-block bg-slate-500 text-white py-2 px-4 rounded-md hover:bg-slate-600 mr-2 focus:outline-none focus:ring-2 focus:ring-slate-600 focus:ring-offset-2"
            >
            <FaArrowLeft />
          </Link>
        </div>
        {/* <div className="mb-6">
          <Link
            href={`/processes/show/${process._id}`}
            className="bg-gray-600 text-white py-2 px-4 rounded hover:bg-gray-700"
          >
            <FaArrowLeft className="inline mr-2" />
          </Link>
        </div> */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-bold mb-2">Process Info</h2>
          <div className="mb-2"><strong>Task:</strong> {process.task_process}</div>
          <div className="mb-2"><strong>Process ID:</strong> {process.process_id}</div>
          <div className="mb-2"><strong>Status:</strong> {process.status}</div>
          <div className="mb-2"><strong>Repository:</strong> {repository.name} (ID: {repository._id}, Version: {repository.version})</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Results</h2>
          {task_process === "filter" && renderRecordsTable(results)}
          {task_process === "group" && renderGroupResults()}
          {task_process === "aggregation" && (
            <>
              {renderAggregationTable()}
              {/* Optionally, add a chart here for numeric metrics */}
              {/* For example, use react-chartjs-2 to show a bar chart of numeric aggregations */}
            </>
          )}
        </div>
      </main>
      <Footer backgroundColor="bg-slate-500" />
    </div>
  );
}