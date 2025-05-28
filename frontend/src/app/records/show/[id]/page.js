"use client";

import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { FaDatabase, FaArrowLeft, FaArchive, FaEdit } from "react-icons/fa";
import Link from "next/link";
import { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { useParams, useSearchParams } from "next/navigation";
import api from "@/app/api";


export default function ShowRecordPage() {
  const { role } = useAuth();
  const [loading, setLoading] = useState(true);
  const [repository, setRepository] = useState(null);
  const [record, setRecord] = useState(null);
  const searchParams = useSearchParams();
  const { id } = useParams();
  const fetchRepository = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/repositories/?_id=${searchParams.get("repository")}&select=name+version+data_ready+current_data_size+parameters`);
      setRecord(response2.data.items[0] || {});
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
    fetchRepository();
    fetchRecord();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 text-gray-800">
      <Header backgroundColor="bg-purple-500" title="Records" />
      <main className="flex-grow max-w-2xl mx-auto w-full px-4 py-8">
        <div className="flex justify-end items-center mb-4">
          {!loading && repository && role === 'admin' && <Link
              title="Edit Record"
              href={`/records/edit/${record._id.$oid}?repository=${repository?._id?.$oid}`}
              className="inline-block bg-green-500 text-white py-2 px-4 mr-2 rounded-md hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-600 focus:ring-offset-2"
            >
            <FaEdit className="w-4 h-4"/>
          </Link>}     
          {!loading && repository?.data_ready && <Link
            title="Go Back"
            href={`/records?repository=${repository._id.$oid}`}
            className="inline-block bg-purple-500 text-white py-2 px-4 rounded-md hover:bg-purple-600 focus:outline-none focus:ring-2 focus:ring-purple-600 focus:ring-offset-2"
          >
            <FaArrowLeft className="w-4 h-4"/>
          </Link> }          
        </div>
        {!loading && repository && <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-bold mb-2">
            <FaArchive className="w-6 h-6 inline text-purple-500" /> Repository Info
          </h2>
          <div className="mb-2">
            <strong>Name:</strong>
            <a target="_blank" className="text-purple-500 inline" href={`/repositories/show/${repository?._id?.$oid}`}>&nbsp;{repository.name}</a>
          </div>
          <div className="mb-2"><strong>Version:</strong> {repository.version}</div>
        </div>}
        {!loading && record && repository && <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">
            <FaDatabase className="w-4 h-4 inline text-purple-500" /> Record Details
          </h2>
          <ul>
            {repository.parameters.map((param) => (
              <li key={param.name} className="mb-2">
                <strong>{param.name}:</strong> {record.data[param.name]}
              </li>
            ))}
              <li key="record_created_at" className="mb-2">
                <strong>Created at:</strong> {new Date(record.created_at).toString()}
              </li>
              <li key="record_updated_at" className="mb-2">
                <strong>Updated at:</strong> {new Date(record.updated_at).toString()}
              </li>
              <li key="record_version" className="mb-2">
                <strong>Version:</strong> {record.version}
              </li>
          </ul>
        </div>}
      </main>
      <Footer backgroundColor="bg-purple-500" />
    </div>
  );
}
