"use client";

import Header from "@/components/Header";
import Footer from "@/components/Footer";
import RecordForm from "@/components/RecordForm";
import { FaArrowLeft, FaArchive, FaDatabase } from "react-icons/fa";
import Link from "next/link";

// Mock repository data (replace with real fetch)
const repository = {
  _id: 1,
  name: "Repository A",
  version: "1.0.0",
  parameters: [
    { name: "filter", type: "string" },
    { name: "limit", type: "number" },
    { name: "category", type: "string" },
  ],
};

export default function CreateRecordPage() {
  const handleCreate = (form) => {
    // TODO: Send to backend
    alert("Record created: " + JSON.stringify(form));
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 text-gray-800">
      <Header backgroundColor="bg-purple-500" title="Records" />
      <main className="flex-grow max-w-2xl mx-auto w-full px-4 py-8">
        <div className="flex justify-end items-center">
          <div>
            <Link
              title="Go Back"
              href={`/records?repository=${repository._id}`}
              className="inline-block bg-purple-500 text-white py-2 px-4 rounded-md hover:bg-purple-600 focus:outline-none focus:ring-2 focus:ring-purple-600 focus:ring-offset-2"
            >
              <FaArrowLeft className="w-4 h-4" />
            </Link>
          </div>            
        </div>
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-bold mb-2">
            <FaArchive className="w-6 h-6 text-purple-500 inline" /> Repository Info
            </h2>
          <div className="mb-2"><strong>Name:</strong> {repository.name}</div>
          <div className="mb-2"><strong>ID:</strong> {repository._id}</div>
          <div className="mb-2"><strong>Version:</strong> {repository.version}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">
            <FaDatabase className="w-4 h-4 text-purple-500 inline" /> Create Record
          </h2>
          <RecordForm repository={repository} onSubmit={handleCreate} />
        </div>
      </main>
      <Footer backgroundColor="bg-purple-500" />
    </div>
  );
}