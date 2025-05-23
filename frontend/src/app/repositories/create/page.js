"use client";

import RepositoryForm from "@/components/RepositoryForm";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { FaArrowLeft, FaArchive } from "react-icons/fa";
import Link from "next/link";
import api from "@/app/api";

export default function CreateRepositoryPage() {
  const router = useRouter();
  const { role } = useAuth();
  useEffect(() => {
    if (role && role !== "admin") {
      router.push("/");
    }
  }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  , [role]);

  const handleCreate = (data) => {
    return api.post("/repositories", data)
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 text-gray-800">
      <Header backgroundColor="bg-sky-600" title="Repositories"/>
      <main className="flex-grow my-4 flex items-center justify-center px-4">
        <div className="max-w-2xl w-full bg-white p-6 shadow-md rounded-lg">
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
            <FaArchive className="w-8 h-8 text-sky-600 inline mr-2" /> New Repository
          </h1>
          <RepositoryForm type="create" onSubmit={handleCreate} />
        </div>
      </main>
      <Footer backgroundColor="bg-sky-600"/>
    </div>
  );
}
