"use client";

import Header from "@/components/Header";
import Footer from "@/components/Footer";
import RecordForm from "@/components/RecordForm";
import { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { useSearchParams } from "next/navigation";
import { FaArrowLeft, FaArchive, FaDatabase, FaShareSquare } from "react-icons/fa";
import Link from "next/link";
import api from "@/app/api";
import { useRouter } from "next/navigation";

export default function CreateRecordPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { role } = useAuth();
  const [loading, setLoading] = useState(true);
  const [repository, setRepository] = useState({});

  const fetchRepository = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/repositories?_id=${searchParams.get("repository")}&select=name+version+data_ready+current_data_size+parameters`);
      setRepository(response.data.items[0] || {});
    } catch (error) {
      console.error("Error fetching repositories:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (role && role !== "admin") {
      router.push("/");
    } else {
      fetchRepository();
    }
  }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  , [role]);

  const handleCreate = (form) => {
    return api.post(`/records/${repository._id.$oid}`, form);
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 text-gray-800">
      <Header backgroundColor="bg-purple-500" title="Records" />
      <main className="flex-grow max-w-2xl mx-auto w-full px-4 py-8">
        <div className="flex justify-end items-center">
          <div>
            {repository && <Link
              title="Go Back"
              href={`/records?repository=${repository?._id?.$oid}`}
              className="inline-block bg-purple-500 text-white py-2 px-4 rounded-md hover:bg-purple-600 focus:outline-none focus:ring-2 focus:ring-purple-600 focus:ring-offset-2"
            >
              <FaArrowLeft className="w-4 h-4" />
            </Link>}
          </div>            
        </div>
        {!loading && repository && <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-bold mb-2">
            <FaArchive className="w-6 h-6 text-purple-500 inline" />
            <span className="inline">&nbsp;Repository Info</span>
          </h2>
          <div className="mb-2">
            <strong>Name:</strong>
            <a target="_blank" className="text-purple-500 inline" href={`/repositories/show/${repository._id.$oid}`}>&nbsp;{repository.name}</a>
          </div>
          <div className="mb-2"><strong>Version:</strong> {repository.version}</div>
        </div>}
        {!loading && repository && <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">
            <FaDatabase className="w-4 h-4 text-purple-500 inline" /> Create Record
          </h2>
          <RecordForm repository={repository} onSubmit={handleCreate} />
        </div>}
      </main>
      <Footer backgroundColor="bg-purple-500" />
    </div>
  );
}