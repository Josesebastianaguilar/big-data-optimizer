"use client";

import { useState, useEffect } from "react";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import Paginator from "@/components/Paginator";
import PageSize from "@/components/PageSize";
import { useSearchParams, useRouter } from "next/navigation";
import { FaChevronDown, FaChevronRight, FaSearch, FaCheckCircle, FaWindowClose, FaRedo, FaArrowLeft, FaPlus, FaProjectDiagram, FaArchive } from "react-icons/fa"; 
import { useAuth } from "@/context/AuthContext";
import api from "@/app/api";
import Link from "next/link";

export default function ProcessesListPage() {
  const { token, role, authLoading } = useAuth();
  const [performance_types] = useState(['optimized', 'non_optimized']);
  const [triggers] = useState(['user', 'system']);
  const [groupedProcesses, setGroupedProcesses] = useState(null);
  const [openGroups, setOpenGroups] = useState({});
  const [loading, setLoading] = useState(true);
  const [processes, setProcesses] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [limit, setLimit] = useState(10);
  const [totalItems, setTotalItems] = useState(0);
  const [repository, setRepository] = useState({});
  const searchParams = useSearchParams();
  const router = useRouter();
  const [validated, setValidated] = useState(false);

  const groupProcesses = (processes) => {
    const grouped = { user: {}, system: {} };
    processes.forEach(proc => {
      const trigger = proc.trigger_type;
      if (!grouped[trigger][proc.process_id.$oid]) {
        grouped[trigger][proc.process_id.$oid] = { optimized: [], non_optimized: [] };
      }
      if (proc.optimized) {
        grouped[trigger][proc.process_id.$oid].optimized.push(proc);
      } else {
        grouped[trigger][proc.process_id.$oid].non_optimized.push(proc);
      }
    });
    return grouped;
  }

  const fetchRepository = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/repositories?_id=${searchParams.get("repository")}`);
      setRepository(response.data.items[0]);
    } catch (error) {
      console.error("Error fetching repositories:", error);
    } finally {
      setLoading(false);
    }
  };
  
  const fetchProcesses = async (newPage = 1, newLimit = 1) => {
    try {
      setLoading(true);
      const response = await api.get(`/processes/${searchParams.get("repository")}?page=${newPage}&limit=${newLimit}&select=process_id+trigger_type+task_process+actions+status+duration+input_data_size+output_data_size+errors+validated+valid+created_at+updated_at+iteration+repository_version+optimized`);
      if (page > response.data.totalPages && response.data.items.length) {
        fetchProcesses(1, 10);
      } else {
        setPage(newPage || 1);
        setLimit(newLimit || 10);
        setProcesses(response.data.items);
        setValidated(!response.data.items.some(proc => proc.validated === false));
        setGroupedProcesses(response.data.items.length ? groupProcesses(response.data.items) : null);
        setTotalPages(response.data.totalPages);
        setTotalItems(response.data.totalItems);
      }
    } catch (error) {
      console.error("Error fetching processes:", error);
    } finally {
      setLoading(false);
    }
  };

  const validate = async () => {
    try {
      setLoading(true);
      const response = await api.put("/processes/validate/");
      fetchProcesses(page, limit);
    } catch (error) {
      console.error("Error validating process:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (authLoading) return;
    if (!token) {
      router.push("/login");
      return;
    }
    if (!searchParams.get("repository")) {
      router.push("/repositories");
      return;
    }
    if (token) {
      fetchRepository(); 
      fetchProcesses(1, 10);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, authLoading]);

  const iterate = async (process_id) => {
    try {
      setLoading(true);
      const response = await api.post(`/processes/iterate/${process_id}`);
      fetchProcesses(page, limit);
    } catch (error) {
      console.log(`Error iterating process_id ${process_id}`)
    } finally {
      setLoading(false);
    }
  };

  // Accordion toggle handler
  const toggleGroup = (trigger, process_id, performance_type) => {
    const key = [trigger, process_id, performance_type].filter(Boolean).join("-");
    setOpenGroups(prev => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const formatDuration = (seconds) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) % 60);
    const s = Math.floor(seconds % 60);
    const ms = Math.floor((seconds - Math.floor(seconds)) * 1000);
    return `${h}h ${m}m ${s}s ${ms}ms`;
  };

  const matchVersions = (process_id) => {
    const processes_id = processes.filter(proc => proc.process_id.$oid === process_id);
    
    return processes_id.every(proc => proc.repository_version === repository.version);
  };


  return (
    <div className="min-h-screen flex flex-col bg-gray-50 text-gray-800">
      <Header backgroundColor="bg-orange-500" title="Processes"/>
      <main className="flex-grow">
        <div className="max-w-8xl mx-auto w-full px-4">
          <div className="flex justify-between items-center mt-4">
            <div>
              {role === 'admin' && repository && <Link
                href={`/processes/create?repository=${repository?._id?.$oid}`}
                className="bg-orange-500 hover:bg-orange-600  text-white py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-600 focus:ring-offset-2"
              >
                <FaPlus className="mr-2 inline" />
                New Process
              </Link>}
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
        <div className="max-w-8xl mx-auto w-full px-4 pt-2 pb-4">
          {/* Repository Info */}
          {!loading && repository && <div className="mb-8 p-6 bg-white rounded-lg shadow">
            <h2 className="text-2xl font-bold mb-2">
              <FaArchive className="w-8 h-8 text-orange-500 inline mr-2" /> 
              <a target="_blank" className="text-orange-500 inline" href={`/repositories/show/${repository?._id?.$oid}`}>&nbsp;{repository.name}</a>
            </h2>
            <p>
              <strong>Version:</strong> {repository.version}
            </p>
          </div>}

          {/* Processes Table with Accordions */}
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-xl font-bold mb-4"><FaProjectDiagram className="w-4 h-4 inline text-orange-500" /> Processes</h3>
            {processes?.length > 0 && <div className="flex justify-end my-2">
              <button className={`text-white fonrt-bold py-2 px-4 rounded-md mb-2 ${validated ? 'bg-orange-300 ' : 'cursor-pointer bg-orange-500 hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-orange-600 focus:ring-offset-2'}`} disabled={validated} onClick={() => validate()}>
                <FaCheckCircle className="inline mr-2 white text-white-500 mr-2" />
                Validate Processes
              </button>
            </div>}
            {processes?.length > 0 && <div className="flex justify-end my-2">
              <PageSize page={page} value={limit} onChange={fetchProcesses}/>
            </div>}
            {processes?.length === 0 && (
              <p className="text-gray-500">No processes found.</p>
            )}
            {!loading && processes?.length > 0 && groupedProcesses && (triggers.map(trigger => (
              <div key={trigger} className={"mb-4 border rounded" + (Object.keys((groupedProcesses)[trigger]).length ? "" : " hidden")}>
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
                  {Object.keys((groupedProcesses)[trigger]).length === 0 && (
                    <p className="text-gray-500 px-4 py-2">No processes for this trigger.</p>
                  )}
                  {Object.keys((groupedProcesses)[trigger]).map(process_id => (
                    <div key={process_id} className={"ml-4 mb-2 border-l" + ((groupedProcesses)[trigger][process_id].optimized.length || (groupedProcesses)[trigger][process_id].non_optimized.length ? "" : " hidden")}>
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
                        {trigger === 'user' && matchVersions(process_id) && (
                          <span className="flex-end items-center inline">
                              <FaRedo title="Re-run process" className="cursor-pointer text-orange-500" onClick={() => iterate(process_id)}/>
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
                                <div className="overflow-x-auto w-full px-2">
                                  <table className="min-w-full bg-white border border-gray-300 rounded-lg shadow-md mt-2">
                                    <thead>
                                      <tr className="bg-orange-500 text-white">
                                        <th className="px-2 py-2 text-xs min-w-auto">Task Process</th>
                                        <th className="px-2 py-2 text-xs min-w-auto">All process tasks</th>
                                        <th className="px-2 py-2 text-xs min-w-auto">Status</th>
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
                                        <tr key={proc._id.$oid} className="hover:bg-gray-100">
                                          <td className="text-center px-2 py-2 text-xs">{proc.task_process}</td>
                                          <td className="text-center px-2 py-2 text-xs">
                                            {proc.actions.map((action) => (
                                              <div key={`${process_id}-${proc._id.$oid}-${action}`} className="px-2 py-2 text-sm block">{action}</div>
                                            ))}
                                          </td>
                                          <td className="text-center px-2 py-2 text-sm">{proc.status}</td>
                                          <td className="text-center px-2 py-2 text-sm">{formatDuration(proc.duration)}</td>
                                          <td className="text-center px-2 py-2 text-sm">{proc.input_data_size}</td>
                                          <td className="text-center px-2 py-2 text-sm">
                                            {proc.task_process === 'filter' && <span>{proc.output_data_size || '-'}</span>}
                                            {proc.task_process !== 'filter' && <span>N/A</span>}
                                          </td>
                                          <td className="text-center px-2 py-2 text-sm">
                                            {!proc.errors && <div className="text-green-800">
                                              <FaCheckCircle className="block w-full"/>
                                              <div className="text-xs w-full">No errors</div>
                                            </div>}
                                            {proc.errors && <div className="text-red-800">
                                              <FaWindowClose className="block"/>
                                              <div className="text-xs">Has errors</div>
                                            </div>}
                                          </td>
                                          <td className="text-center align-center px-2 py-2 text-sm">{proc.validated ? <FaCheckCircle className="text-center text-green-800"/> : <FaWindowClose className="text-center rounded-full  text-red-600"/>}</td>
                                          <td className="text-center px-2 py-2 text-sm">{proc.valid ? <FaCheckCircle className="text-center text-green-800"/> : <FaWindowClose className="text-center rounded-full text-red-600"/>}</td>
                                          <td className="text-center px-2 py-2 text-sm">{new Date(proc.created_at.$date).toString()}</td>
                                          <td className="text-center px-2 py-2 text-sm">{new Date(proc.updated_at.$date).toString()}</td>
                                          <td className="text-center px-2 py-2 text-sm">{proc.iteration}</td>
                                          <td className="text-center px-2 py-2 text-sm">{proc.repository_version}</td>
                                          <td className="text-center px-2 py-2 text-sm space-x-1">
                                            <Link
                                              href={`/processes/show/${proc._id.$oid}?repository=${repository?._id?.$oid}`}
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
            )))}
            {processes?.length > 0 && <div className="flex justify-end my-2">
              <Paginator
                page={page}
                totalPages={totalPages}
                onPageChange={fetchProcesses}
                module="processes"
                showTotals={true}
                limit={limit}
                totalItems={totalItems}
                activeBackgroundColor="bg-orange-500"
              />
            </div>}
          </div>
        </div>
      </main>
      <Footer backgroundColor="bg-orange-500"/>
    </div>
  );
}
