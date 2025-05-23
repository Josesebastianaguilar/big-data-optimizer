"use client";

import Header from "@/components/Header";
import Footer from "@/components/Footer";
import RecordForm from "@/components/RecordForm";
import { FaArrowLeft, FaDatabase, FaArchive } from "react-icons/fa";
import Link from "next/link";
import { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { useParams, useSearchParams } from "next/navigation";
import api from "@/app/api";


export default function EditRecordPage() {
  const { role } = useAuth();
  const [loading, setLoading] = useState(true);
  const [repository, setRepository] = useState(null);
  const [record, setRecord] = useState(null);
  const searchParams = useSearchParams();
  const { id } = useParams();
  const fetchRepository = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/repositories?_id=${searchParams.get("repository")}&select=name+version+data_ready+current_data_size+parameters`);
      const response2 = await api.get(`/records/${searchParams.get("repository")}?_id=${id}`);
      setRecord(response2.data.items[0] || {});
      setRepository(response.data.items[0] || {});
    } catch (error) {
      console.error("Error fetching repositories:", error);
    } finally {
      setLoading(false);
    }
  };
  
  const fetchRecord = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/records/${searchParams.get("repository")}?_id=${id}`);
      setRecord(response.data.items[0] || {});
    } catch (error) {
      console.error("Error fetching repositories:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (role && role === "admin") {
      fetchRepository();
      fetchRecord();
    } else if (role && role !== "admin") {
      router.push("/");
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [role]);

  const handleEdit = (form) => {
    return api.put(`/records/${record._id.$oid}`, form)
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 text-gray-800">
      <Header backgroundColor="bg-purple-500" title="Records" />
      <main className="flex-grow max-w-2xl mx-auto w-full px-4 py-8">
        <div className="flex justify-end items-center mb-2">    
          {!loading && repository && <Link
            title="Go Back"
            href={`/records?repository=${repository?._id?.$oid}`}
            className="inline-block bg-purple-500 text-white py-2 px-4 rounded-md hover:bg-purple-600 focus:outline-none focus:ring-2 focus:ring-purple-600 focus:ring-offset-2"
          >
            <FaArrowLeft className="w-4 h-4" />
          </Link>}
        </div>
        {!loading && repository && <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-bold mb-2">
            <FaArchive className="w-6 h-6 text-purple-500 inline" /> Repository Info
          </h2>
          <div className="mb-2">
            <strong>Name:</strong>
            <a target="_blank" className="text-purple-500 inline" href={`/repositories/show/${repository?._id?.$oid}`}>&nbsp;{repository.name}</a>
          </div>
          <div className="mb-2"><strong>Version:</strong> {repository.version}</div>
        </div>}
        {!loading && repository && record && <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">
            <FaDatabase className="w-4 h-4 text-purple-500 inline" /> Edit Record
          </h2>
          <RecordForm repository={repository} record={record} onSubmit={handleEdit} isEdit />
        </div>}
      </main>
      <Footer backgroundColor="bg-purple-500" />
    </div>
  );
}
