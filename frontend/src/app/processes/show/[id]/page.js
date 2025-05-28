"use client";

import Link from "next/link";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { FaArrowLeft, FaRedo, FaSearch, FaChartBar, FaPlus, FaArchive, FaCheckCircle, FaWindowClose } from "react-icons/fa";
import { useEffect, useState } from "react";
import { Line, Doughnut } from "react-chartjs-2";
import { useParams, useSearchParams, useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import api from "@/app/api";
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

export default function ProcessShowView() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { token, authLoading } = useAuth();
  const [loading, setLoading] = useState(false);
  const [repository, setRepository] = useState(null);
  const [process, setProcess] = useState(null);
  const { id } = useParams();
  const [lineChartData, setLineChartData] = useState(null);
  const [doughnutData, setDoughnutData] = useState(null);
  const formatTimestamp = (seconds) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) % 60);
    const s = Math.floor(seconds % 60);
    const ms = Math.floor((seconds - Math.floor(seconds)) * 1000);
    return `${h}h ${m}m ${s}s ${ms}ms`;
  };

  const fetchRepository = async () => {
      try {
        setLoading(true);
        const response = await api.get(`/repositories/?_id=${searchParams.get("repository")}`);
        setRepository(response.data.items[0]);
      } catch (error) {
        console.error("Error fetching repositories:", error);
      } finally {
        setLoading(false);
      }
    };
    
  const fetchProcess = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/processes/${searchParams.get("repository")}?_id=${id}`);
      setProcess(() => response.data.items[0] || null);
      setLineChartData(() => {
        const metrics = response.data.items[0].metrics || [];
        if (!metrics.length) return null;

        const cpuArr = metrics.map(m => m.cpu);
        const memoryArr = metrics.map(m => m.memory);
        const timestampsArr = metrics.map(m => formatTimestamp(m.timestamp));

        return {
          labels: timestampsArr,
          datasets: [
            {
              label: "CPU (%)",
              data: cpuArr,
              borderColor: "#2563eb",
              backgroundColor: "rgba(37,99,235,0.2)",
              yAxisID: "y",
            },
            {
              label: "Memory (MB)",
              data: memoryArr,
              borderColor: "#22c55e",
              backgroundColor: "rgba(34,197,94,0.2)",
              yAxisID: "y1",
            },
          ],
        };
      });
      setDoughnutData(() => {
        const metrics = response.data.items[0].metrics || [];
        if (!metrics.length) return null;
        const cpuArr = metrics.map(m => m.cpu);
        const memoryArr = metrics.map(m => m.memory);

        return {
          labels: ["Avg CPU (%)", "Avg Memory (MB)"],
          datasets: [
            {
              data: [
                cpuArr.reduce((a, b) => a + b, 0) / cpuArr.length,
                memoryArr.reduce((a, b) => a + b, 0) / memoryArr.length,
              ],
              backgroundColor: ["#2563eb", "#22c55e"],
              hoverBackgroundColor: ["#1d4ed8", "#16a34a"],
            },
          ],
        };
      });
    } catch (error) {
      console.error("Error fetching processes:", error);
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
      fetchProcess();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, authLoading]);

  const iterate = async (process_id) => {
    try {
      setLoading(true);
      await api.post(`/processes/iterate/${process_id}`);
    } catch (error) {
      console.log(`Error iterating process_id ${process_id}`)
    } finally {
      setLoading(false);
    }
  };
  
  const capitalize = (string) => {
    return string.charAt(0).toUpperCase() + string.slice(1)
  };

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

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 text-gray-800">
      <Header backgroundColor="bg-orange-500" title="Processes"/>
      <div className="max-w-3xl mx-auto w-full px-4 py-8">

        {!loading && repository && <div className="mb-8 p-6 bg-white rounded-lg shadow">
                    <h2 className="text-2xl font-bold mb-2">
                      <FaArchive className="w-8 h-8 text-orange-500 inline mr-2" /> 
                      <a target="_blank" className="text-orange-500 inline" href={`/repositories/show/${repository?._id?.$oid}`}>&nbsp;{repository.name}</a>
                    </h2>
                    <p>
                      <strong>Version:</strong> {repository.version}
                    </p>
                  </div>}
        {process && <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-end items-center mb-2">
            <Link
              title="New Process"
              href={`/processes/create?repository=${process.repository.$oid}`}
              className="bg-blue-500  hover:bg-blue-600 text-white mr-2 py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2"
            >
              <FaPlus className="w-4 h-4" />
            </Link>
            {process.results.length && false && (<Link
              title="Show Results"
              href={`/processes/results/${process._id}`}
              className="bg-slate-500  hover:bg-slate-600 text-white mr-2 py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-600 focus:ring-offset-2"
            >
              <FaChartBar className="w-4 h-4" />
            </Link>)}
            {process.trigger_type === 'user' && <div onClick={() => iterate(process.process_id.$oid)}
                title="Re-run Process"
                className="text-white py-2 px-4 rounded-md cursor-pointer bg-orange-500 mr-2 hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2">
                  <FaRedo className="w-4 h-4" />
            </div>}          
            <Link
              title="Go Back"
              href={`/processes?repository=${process.repository.$oid}`}
              className="inline-block bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
            >
              <FaArrowLeft className="w-4 h-4" />
            </Link>
          </div>
          <h2 className="text-2xl w-full font-bold mb-4">Process Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-2 mb-6">
            <div><strong>Task Process:</strong> {capitalize(process.task_process)}</div>
            <div><strong>Actions:</strong> {process.actions.map(action => capitalize(action)).join(", ")}</div>
            <div><strong>Status:</strong> {capitalize(process.status)}</div>
            <div><strong>Process ID:</strong> {process.process_id.$oid}</div>
            <div><strong>Optimized:</strong> {process.optimized ? <FaCheckCircle className="text-center text-green-800 inline"/> : <FaWindowClose className="text-center inline rounded-full  text-red-600"/>}</div>
            <div><strong>Trigger Type:</strong> {capitalize(process.trigger_type)}</div>
            <div><strong>Start Time:</strong> {formatTimestamp(process.start_time)}</div>
            <div><strong>End Time:</strong> {formatTimestamp(process.end_time)}</div>
            <div><strong>Duration:</strong> {formatTimestamp(process.duration)}</div>
            <div><strong>Input # of records:</strong> {process.input_data_size}</div>
            {process.task_process !== 'aggregation' && <div><strong>Output # number of records:</strong> {process.output_data_size}</div>}
            <div><strong>Errors:</strong> {process.errors ? process.errors : <span className="text-green-600">None</span>}</div>
            <div><strong>Validated:</strong> {process.valid ? <FaCheckCircle className="text-center text-green-800 inline"/> : <FaWindowClose className="text-center rounded-full inline text-red-600"/>}</div>
            <div><strong>Valid:</strong> {process.validated ? <FaCheckCircle className="text-center text-green-800 inline"/> : <FaWindowClose className="text-center rounded-full inline text-red-600"/>}</div>
            <div><strong>Created At:</strong> {new Date(process.created_at.$date).toString()}</div>
            <div><strong>Updated At:</strong> {new Date(process.updated_at.$date).toString()}</div>
            <div><strong>Iteration:</strong> {process.iteration}</div>
            <div><strong>Repository Version:</strong> {process.repository_version}</div>
            {process.task_process === 'group' && <div><strong>Parameters:</strong> {process.parameters.map(param => capitalize(param)).join(', ')}</div>}
          </div>
          {process.task_process !== 'group' && <div className="mb-2"><strong>Parameters:</strong></div>}
          {process.task_process !== 'group' && <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-2 mb-6">
            {process.parameters.map((parameter, index) =>(
              <div key={`parameter_${index}`} className="mb-2">
                { Object.keys(parameter).map((key, keyIndex) => (
                  <div key={key}>
                    {keyIndex === 0 && <span className="inline font-bold">{index + 1}</span>}. <strong>{capitalize(key)}:</strong> {key === 'operations' ? parameter[key].join(', ') : parameter[key]}
                  </div>
                ))}
              </div>
            ))}
          </div>}

          {/* Metrics Charts */}
          {process.metrics.length && (
            <div className="mb-8">
              <h3 className="text-lg font-bold mb-2">Metrics</h3>
              {lineChartData && <div className="mb-4 bg-gray-50 rounded p-4">
                <Line data={lineChartData} options={lineChartOptions} />
              </div>}
              {doughnutData && <div className="mb-4 w-1/2 mx-auto">
                <Doughnut data={doughnutData} />
              </div>}
            </div>
          )}
        </div>}
      </div>
      <Footer backgroundColor="bg-orange-500"/>
    </div>
  );
}
