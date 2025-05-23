"use client";

import RepositoryForm from "@/components/RepositoryForm";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { useRouter, useParams } from "next/navigation";
import { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { FaArrowLeft, FaArchive, FaSpinner } from "react-icons/fa";
import Link from "next/link";
import api from "@/app/api";

export default function EditRepositoryPage() {
  const { id } = useParams();
  const { role } = useAuth();
  const router = useRouter();
  const [repository, setRepository] = useState({});
  const [loading, setLoading] = useState(false);

  const fetchRepository = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/repositories?_id=${id}`);
      setRepository(response.data.items[0] || {});
    } catch (error) {
      console.error("Error fetching repositories:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (role && role === "admin") {
      fetchRepository();
    } else if (role && role !== "admin") {
      router.push("/");
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [role]);

  const handleUpdate = (data) => {
    return api.put(`/repositories/${repository._id.$oid}`, data)
  };

  return (
     <div className="min-h-screen flex flex-col bg-gray-50 text-gray-800">
      <Header backgroundColor="bg-sky-600" title="Repositories"/>
      <main className="flex-grow my-4 flex items-center justify-center px-4">
        {loading && <FaSpinner className="animate-spin inline mr-2" />}
        {!loading && repository && <div className="max-w-2xl w-full bg-white p-6 shadow-md rounded-lg">
           <div className="flex justify-end items-center">
            <div>
              <Link
                title="Go Back"
                href="/repositories"
                className="inline-block bg-sky-600 text-white py-2 px-4 rounded-md hover:bg-sky-700 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2"
              >
                <FaArrowLeft className="w-4 h-4" />
              </Link>
            </div>            
          </div>
          <h1 className="text-3xl font-extrabold text-gray-900 text-center mb-6">
            <FaArchive className="w-8 h-8 text-sky-600 inline mr-2" /> Edit Repository
          </h1>
          <RepositoryForm type="edit" initialData={repository} onSubmit={handleUpdate} />
        </div>}
      </main>
      <Footer backgroundColor="bg-sky-600"/>
    </div>
  );
}
