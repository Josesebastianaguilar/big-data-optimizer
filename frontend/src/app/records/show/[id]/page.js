"use client";

import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { FaDatabase, FaArrowLeft, FaArchive, FaEdit } from "react-icons/fa";
import Link from "next/link";

// Mock repository and record data (replace with real fetch)
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
const record = { _id: 2, filter: "inactive", limit: 50, category: "B" };

export default function ShowRecordPage() {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50 text-gray-800">
      <Header backgroundColor="bg-purple-500" title="Records" />
      <main className="flex-grow max-w-2xl mx-auto w-full px-4 py-8">
        <div className="flex justify-end items-center mb-2">
          <Link
              title="Edit Record"
              href={`/records/edit/${record._id}?repository=${repository._id}`}
              className="inline-block bg-green-500 text-white py-2 px-4 mr-2 rounded-md hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-600 focus:ring-offset-2"
            >
            <FaEdit className="w-4 h-4"/>
          </Link>     
          <Link
            title="Go Back"
            href={`/records?repository=${repository._id}`}
            className="inline-block bg-purple-500 text-white py-2 px-4 rounded-md hover:bg-purple-600 focus:outline-none focus:ring-2 focus:ring-purple-600 focus:ring-offset-2"
          >
            <FaArrowLeft className="w-4 h-4"/>
          </Link>           
        </div>
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-bold mb-2">
            <FaArchive className="w-6 h-6 inline text-purple-500" /> Repository Info
          </h2>
          <div className="mb-2"><strong>Name:</strong> {repository.name}</div>
          <div className="mb-2"><strong>ID:</strong> {repository._id}</div>
          <div className="mb-2"><strong>Version:</strong> {repository.version}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">
            <FaDatabase className="w-4 h-4 inline text-purple-500" /> Record Details
          </h2>
          <ul>
            {repository.parameters.map((param) => (
              <li key={param.name} className="mb-2">
                <strong>{param.name}:</strong> {record[param.name]}
              </li>
            ))}
          </ul>
        </div>
      </main>
      <Footer backgroundColor="bg-purple-500" />
    </div>
  );
}
