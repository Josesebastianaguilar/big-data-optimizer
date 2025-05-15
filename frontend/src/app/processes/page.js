"use client";

import { useState } from "react";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { FaChevronDown, FaChevronRight, FaSearch, FaCheckCircle, FaWindowClose, FaRedo, FaArrowLeft, FaPlus, FaProjectDiagram, FaArchive, FaShareSquare } from "react-icons/fa"; 
import Link from "next/link";

// Mock repository info
const repository = {
  id: 1,
  name: "Repository A",
  description: "Sample repository for demonstration.",
  url: "https://example.com/repo-a",
  version: "1.0.0",
};

// Mock processes data
const mockProcesses = [
  {
    task_process: "Import Data",
    actions: ["FILTER", "GROUP"],
    status: "Completed",
    process_id: "P-001",
    optimized: true,
    trigger_type: "SYSTEM",
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
    _id: 1,
  },
  {
    task_process: "Optimize Data",
    actions: ["Optimize"],
    status: "Failed",
    process_id: "P-001",
    optimized: false,
    trigger_type: "USER",
    start_time: "2024-05-01 10:35",
    end_time: "2024-05-01 10:45",
    duration: "10m",
    input_data_size: "300 MB",
    output_data_size: "0 MB",
    errors: "Out of memory",
    validated: false,
    valid: false,
    created_at: "2024-05-01 10:34",
    updated_at: "2024-05-01 10:46",
    iteration: 1,
    repository_version: "1.0.0",
    _id: 2,
  },
];

// Helper to group processes
function groupProcesses(processes) {
  const grouped = { USER: {}, SYSTEM: {} };
  processes.forEach(proc => {
    const trigger = proc.trigger_type;
    if (!grouped[trigger][proc.process_id]) {
      grouped[trigger][proc.process_id] = { optimized: [], non_optimized: [] };
    }
    if (proc.optimized) {
      grouped[trigger][proc.process_id].optimized.push(proc);
    } else {
      grouped[trigger][proc.process_id].non_optimized.push(proc);
    }
  });
  return grouped;
}

export default function ProcessesListPage() {
  const [performance_types] = useState(['optimized', 'non_optimized']);
  const [triggers] = useState(['USER', 'SYSTEM']);
  const [groupedProcesses] = useState(() => groupProcesses(mockProcesses));
  const [openGroups, setOpenGroups] = useState({});

  // Accordion toggle handler
  const toggleGroup = (trigger, process_id, performance_type) => {
    const key = [trigger, process_id, performance_type].filter(Boolean).join("-");
    setOpenGroups(prev => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 text-gray-800">
      <Header backgroundColor="bg-orange-500" title="Processes"/>
      <main className="flex-grow">
        <div className="max-w-7xl mx-auto w-full px-4">
          <div className="flex justify-between items-center mt-4">
            <div>
              <Link
                href={`/processes/create?repository=${repository.id}`}
                className="bg-orange-500 hover:bg-orange-600  text-white py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-600 focus:ring-offset-2"
              >
                <FaPlus className="mr-2 inline" />
                New Process
              </Link>
            </div>
            <div>
              <Link
                title="Go Back"
                href="/repositories"
                className="inline-block bg-orange-500 text-white py-2 px-4 rounded-md hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-orange-600 focus:ring-offset-2"
              >
                <FaArrowLeft className="w-4 h-4" />
              </Link>
            </div>            
          </div>
        </div>
        <div className="max-w-7xl mx-auto w-full px-4 pt-2 pb-4">
          {/* Repository Info */}
          <div className="mb-8 p-6 bg-white rounded-lg shadow">
            <h2 className="text-2xl font-bold mb-2"><FaArchive className="w-8 h-8 text-orange-500 inline mr-2" /> {repository.name}</h2>
            <p className="mb-1">{repository.description}</p>
            {repository.url && <p className="mb-1">
              <strong>URL:</strong>{" "}
              <a href={repository.url} className="no-underline" target="_blank" rel="noopener noreferrer">
                <FaShareSquare title="Open repository url in another tab" className="w-4 h-4 text-orange-500 inline" />
              </a>
            </p>}
            <p>
              <strong>Version:</strong> {repository.version}
            </p>
          </div>

          {/* Processes Table with Accordions */}
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-xl font-bold mb-4"><FaProjectDiagram className="w-4 h-4 inline text-orange-500" /> Processes</h3>
            {mockProcesses.length === 0 && (
              <p className="text-gray-500">No processes found.</p>
            )}
            {triggers.map(trigger => (
              <div key={trigger} className={"mb-4 border rounded" + (Object.keys(groupedProcesses[trigger]).length ? "" : " hidden")}>
                {/* Trigger Type Accordion */}
                <button
                  type="button"
                  className=" cursor-pointer w-full text-left px-4 py-2 bg-orange-100 font-semibold flex items-center"
                  onClick={() => toggleGroup(trigger)}
                >
                  <span className="mr-2">
                    {openGroups[`${trigger}`] ? <FaChevronDown /> : <FaChevronRight />}
                  </span>
                  {trigger} triggered processes
                </button>
                <div className={openGroups[`${trigger}`] ? "block" : "hidden"}>
                  {Object.keys(groupedProcesses[trigger]).length === 0 && (
                    <p className="text-gray-500 px-4 py-2">No processes for this trigger.</p>
                  )}
                  {Object.keys(groupedProcesses[trigger]).map(process_id => (
                    <div key={process_id} className={"ml-4 mb-2 border-l" + (groupedProcesses[trigger][process_id].optimized.length || groupedProcesses[trigger][process_id].non_optimized.length ? "" : " hidden")}>
                      <button
                        type="button"
                        className="cursor-pointer w-full text-left px-4 py-2 bg-orange-50 font-semibold flex items-center"
                        
                      >
                        <span className="mr-2"  onClick={() => toggleGroup(trigger, process_id)}>
                          {openGroups[`${trigger}-${process_id}`] ? <FaChevronDown /> : <FaChevronRight />}
                        </span>
                        <span className="mr-auto" onClick={() => toggleGroup(trigger, process_id)}>
                          Process ID: {process_id}
                        </span>
                        {trigger === 'USER' && (
                          <span className="flex-end items-center inline">
                              <FaRedo title="Re-run process" className="text-orange-500"/>
                          </span>
                        )}
                      </button>
                      <div className={openGroups[`${trigger}-${process_id}`] ? "block" : "hidden"}>
                        {performance_types.map(performance_type => (
                          <div key={`${process_id}-${performance_type}`} className={"ml-4 mb-2 border-l" + (groupedProcesses[trigger][process_id][performance_type].length ? "" : " hidden")}>
                            <button
                              type="button"
                              onClick={() => toggleGroup(trigger, process_id, performance_type)}
                              className="cursor-pointer w-full text-left px-4 py-2 bg-orange-200 font-semibold flex items-center"
                            >
                              <span className="mr-2">
                                {openGroups[`${trigger}-${process_id}-${performance_type}`] ? <FaChevronDown /> : <FaChevronRight />}
                              </span>
                              {performance_type === 'optimized' ? "Optimized" : "Non Optimized"}
                            </button>
                            <div className={openGroups[`${trigger}-${process_id}-${performance_type}`] ? "block" : "hidden"}>
                              {groupedProcesses[trigger][process_id][performance_type].length === 0 ? (
                                <p className="text-gray-500 px-4 py-2">No processes.</p>
                              ) : (
                                <div className="overflow-x-auto w-full">
                                <table className="min-w-full bg-white border border-gray-300 rounded-lg shadow-md mt-2">
                                  <thead>
                                    <tr className="bg-orange-500 text-white">
                                      <th className="px-2 py-2 text-xs min-w-auto">Task Process</th>
                                      <th className="px-2 py-2 text-xs min-w-auto">All process tasks</th>
                                      <th className="px-2 py-2 text-xs min-w-auto">Status</th>
                                      <th className="px-2 py-2 text-xs min-w-auto">Start Time</th>
                                      <th className="px-2 py-2 text-xs min-w-auto">End Time</th>
                                      <th className="px-2 py-2 text-xs min-w-auto">Duration</th>
                                      <th className="px-2 py-2 text-xs min-w-auto">Input Size</th>
                                      <th className="px-2 py-2 text-xs min-w-auto">Output Size</th>
                                      <th className="px-2 py-2 text-xs min-w-auto">Errors</th>
                                      <th className="px-2 py-2 text-xs min-w-auto">Validated</th>
                                      <th className="px-2 py-2 text-xs min-w-auto">Valid</th>
                                      <th className="px-2 py-2 text-xs min-w-auto">Created At</th>
                                      <th className="px-2 py-2 text-xs min-w-auto">Updated At</th>
                                      <th className="px-2 py-2 text-xs min-w-auto">Iteration</th>
                                      <th className="px-2 py-2 text-xs min-w-auto">Repo Version</th>
                                      <th className="px-2 py-2 text-xs min-w-auto">Actions</th>
                                    </tr>
                                  </thead>
                                  <tbody>
                                    {groupedProcesses[trigger][process_id][performance_type].map((proc) => (
                                      <tr key={proc._id} className="hover:bg-gray-100">
                                        <td className="px-2 py-2 text-xs">{proc.task_process}</td>
                                        <td className="px-2 py-2 text-xs">
                                          {proc.actions.map((action) => (
                                            <div key={`${process_id}-${proc.__id}-${action}`} className="px-2 py-2 text-sm block">{action}</div>
                                          ))}
                                        </td>
                                        <td className="px-2 py-2 text-sm">{proc.status}</td>
                                        <td className="px-2 py-2 text-sm">{proc.start_time}</td>
                                        <td className="px-2 py-2 text-sm">{proc.end_time}</td>
                                        <td className="px-2 py-2 text-sm">{proc.duration}</td>
                                        <td className="px-2 py-2 text-sm">{proc.input_data_size}</td>
                                        <td className="px-2 py-2 text-sm">{proc.output_data_size}</td>
                                        <td className="px-2 py-2 text-sm">
                                          {proc.errors && <span className="text-green-800"><FaCheckCircle/> Sin errores</span>}
                                          {!proc.errors && <span className="text-red-800"><FaWindowClose/> Con errores</span>}
                                        </td>
                                        <td className="px-2 py-2 text-sm">{proc.validated ? <FaCheckCircle className="text-green-800"/> : <FaWindowClose className="text-red-800"/>}</td>
                                        <td className="px-2 py-2 text-sm">{proc.valid ? <FaCheckCircle className="text-green-800"/> : <FaWindowClose className="text-red-800"/>}</td>
                                        <td className="px-2 py-2 text-sm">{proc.created_at}</td>
                                        <td className="px-2 py-2 text-sm">{proc.updated_at}</td>
                                        <td className="px-2 py-2 text-sm">{proc.iteration}</td>
                                        <td className="px-2 py-2 text-sm">{proc.repository_version}</td>
                                        <td className="px-2 py-2 text-sm space-x-1">
                                          <Link
                                            href={`/processes/show/${proc._id}`}
                                            className="inline-block"
                                          >
                                            <FaSearch title="Show Process" className="w-3 h-3 text-stone-700 hover:text-stone-800" />
                                          </Link>
                                        </td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
      <Footer backgroundColor="bg-orange-500"/>
    </div>
  );
}
