"use client";

import Link from "next/link";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { FaArrowLeft, FaRedo, FaSearch, FaChartBar, FaPlus } from "react-icons/fa";
import { Line, Doughnut } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, ArcElement, Tooltip, Legend);

// Mock process data (replace with real fetch or prop)
const process = {
  _id: 1,
  task_process: "Import Data",
  actions: ["FILTER", "GROUP"],
  status: "Completed",
  process_id: "P-001",
  optimized: true,
  repository: 1,
  trigger_type: "USER",
  start_time: "2024-05-01 10:00",
  end_time: "2024-05-01 10:30",
  duration: "30m",
  input_data_size: "500 MB",
  output_data_size: "300 MB",
  errors: "",
  validated: true,
  valid: true,
  created_at: "2024-05-01 09:55",
  updated_at: "2024-05-01 10:31",
  iteration: 1,
  repository_version: "1.0.0",
  results: [
    { timestamp: "2024-05-01 10:05", cpu: 30, memory: 200 },
    { timestamp: "2024-05-01 10:10", cpu: 40, memory: 220 },
    { timestamp: "2024-05-01 10:15", cpu: 35, memory: 210 },
    { timestamp: "2024-05-01 10:20", cpu: 50, memory: 250 },
    { timestamp: "2024-05-01 10:25", cpu: 45, memory: 230 },
    { timestamp: "2024-05-01 10:30", cpu: 38, memory: 215 },
  ],
  metrics: {
    cpu: [30, 40, 35, 50, 45, 38],
    memory: [200, 220, 210, 250, 230, 215],
    timestamps: [
      "2024-05-01 10:05",
      "2024-05-01 10:10",
      "2024-05-01 10:15",
      "2024-05-01 10:20",
      "2024-05-01 10:25",
      "2024-05-01 10:30",
    ],
  },
};

export default function ProcessShowView() {
  // Prepare chart data if metrics exist and no errors
  const hasMetrics = !process.errors && process.metrics && process.metrics.cpu && process.metrics.memory;
  const hasResults = !process.errors && process.results && process.results.length > 0;

  const lineChartData = hasMetrics
    ? {
        labels: process.metrics.timestamps,
        datasets: [
          {
            label: "CPU (%)",
            data: process.metrics.cpu,
            borderColor: "#2563eb",
            backgroundColor: "rgba(37,99,235,0.2)",
            yAxisID: "y",
          },
          {
            label: "Memory (MB)",
            data: process.metrics.memory,
            borderColor: "#22c55e",
            backgroundColor: "rgba(34,197,94,0.2)",
            yAxisID: "y1",
          },
        ],
      }
    : null;

  const lineChartOptions = {
    responsive: true,
    plugins: {
      legend: { position: "top" },
      title: { display: true, text: "Process Metrics Over Time" },
    },
    scales: {
      y: {
        type: "linear",
        display: true,
        position: "left",
        title: { display: true, text: "CPU (%)" },
      },
      y1: {
        type: "linear",
        display: true,
        position: "right",
        grid: { drawOnChartArea: false },
        title: { display: true, text: "Memory (MB)" },
      },
    },
  };

  // Example doughnut chart for average CPU/Memory
  const doughnutData = hasMetrics
    ? {
        labels: ["Avg CPU (%)", "Avg Memory (MB)"],
        datasets: [
          {
            data: [
              process.metrics.cpu.reduce((a, b) => a + b, 0) / process.metrics.cpu.length,
              process.metrics.memory.reduce((a, b) => a + b, 0) / process.metrics.memory.length,
            ],
            backgroundColor: ["#2563eb", "#22c55e"],
            hoverBackgroundColor: ["#1d4ed8", "#16a34a"],
          },
        ],
      }
    : null;

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 text-gray-800">
      <Header backgroundColor="bg-orange-500" title="Processes"/>
      <div className="max-w-3xl mx-auto w-full px-4 py-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-end items-center mb-2">
            <Link
              title="New Process"
              href={`/processes/create?repository=${process.repository}`}
              className="bg-blue-500  hover:bg-blue-600 text-white mr-2 py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2"
            >
              <FaPlus className="w-4 h-4" />
            </Link>
            {hasResults && (<Link
              title="Show Results"
              href={`/results/${process._id}`}
              className="bg-slate-500  hover:bg-slate-600 text-white mr-2 py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-600 focus:ring-offset-2"
            >
              <FaChartBar className="w-4 h-4" />
            </Link>)}
            {process.trigger_type === 'USER' && <div
                title="Re-run Process"
                className="cursor-pointer bg-orange-500 mr-2 hover:bg-orange-600  text-white py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2">
                  <FaRedo className="w-4 h-4" />
            </div>}          
            <Link
              title="Go Back"
              href={`/processes?repository=${process.repository}`}
              className="inline-block bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
            >
              <FaArrowLeft className="w-4 h-4" />
            </Link>
          </div>
          <h2 className="text-2xl w-full font-bold mb-4">Process Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-2 mb-6">
            <div><strong>Task Process:</strong> {process.task_process}</div>
            <div><strong>Actions:</strong> {process.actions.join(", ")}</div>
            <div><strong>Status:</strong> {process.status}</div>
            <div><strong>Process ID:</strong> {process.process_id}</div>
            <div><strong>Optimized:</strong> {process.optimized ? "Yes" : "No"}</div>
            <div><strong>Trigger Type:</strong> {process.trigger_type}</div>
            <div><strong>Start Time:</strong> {process.start_time}</div>
            <div><strong>End Time:</strong> {process.end_time}</div>
            <div><strong>Duration:</strong> {process.duration}</div>
            <div><strong>Input Data Size:</strong> {process.input_data_size}</div>
            <div><strong>Output Data Size:</strong> {process.output_data_size}</div>
            <div><strong>Errors:</strong> {process.errors ? process.errors : <span className="text-green-600">None</span>}</div>
            <div><strong>Validated:</strong> {process.valid ? "Yes" : "No"}</div>
            <div><strong>Valid:</strong> {process.validated ? "Yes" : "No"}</div>
            <div><strong>Created At:</strong> {process.created_at}</div>
            <div><strong>Updated At:</strong> {process.updated_at}</div>
            <div><strong>Iteration:</strong> {process.iteration}</div>
            <div><strong>Repository Version:</strong> {process.repository_version}</div>
          </div>

          {/* Metrics Charts */}
          {hasMetrics && (
            <div className="mb-8">
              <h3 className="text-lg font-bold mb-2">Metrics</h3>
              <div className="mb-4 bg-gray-50 rounded p-4">
                <Line data={lineChartData} options={lineChartOptions} />
              </div>
              <div className="mb-4 w-1/2 mx-auto">
                <Doughnut data={doughnutData} />
              </div>
            </div>
          )}
        </div>
      </div>
      <Footer backgroundColor="bg-orange-500"/>
    </div>
  );
}
