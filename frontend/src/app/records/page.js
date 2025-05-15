"use client";

import { useState } from "react";
import Link from "next/link";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import ConfirmationModal from "@/components/ConfirmationModal";
import { FaArrowLeft, FaPlus, FaSearch, FaEdit, FaTrash, FaDatabase } from "react-icons/fa";

// Mock repository and records data
const repository = {
  _id: 1,
  name: "Repository A",
  parameters: [
    { name: "filter", type: "string" },
    { name: "limit", type: "number" },
    { name: "category", type: "string" },
  ],
};

const mockRecords = [
  { _id: 1, filter: "active", limit: 100, category: "A" },
  { _id: 2, filter: "inactive", limit: 50, category: "B" },
  { _id: 3, filter: "pending", limit: 75, category: "C" },
];

export default function RecordsListPage() {
  const [records, setRecords] = useState(mockRecords);
  const [showModal, setShowModal] = useState(false);
  const [recordToDelete, setRecordToDelete] = useState(null);

  const handleDeleteClick = (record) => {
    setRecordToDelete(record);
    setShowModal(true);
  };

  const confirmDelete = () => {
    setRecords((prev) => prev.filter((r) => r._id !== recordToDelete._id));
    setShowModal(false);
    setRecordToDelete(null);
  };

  const cancelDelete = () => {
    setShowModal(false);
    setRecordToDelete(null);
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 text-gray-800">
      <Header backgroundColor="bg-purple-500" title="Records"/>
      <main className="flex-grow max-w-6xl mx-auto w-full px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <Link
            href={`/records/create?repository=${repository._id}`}
            className="bg-purple-500 hover:bg-purple-600 text-white py-2 px-4 rounded-md flex items-center focus:outline-none focus:ring-2 focus:ring-purple-600 focus:ring-offset-2"
          >
            <FaPlus className="mr-2" /> New Record
          </Link>
          <div>
            <FaDatabase className="w-6 h-6 inline text-purple-500 mr-2" />
            <span className="text-2xl font-bold">{repository.name} Records</span>
          </div>
          <Link
              title="Go Back"
              href={`/repositories/`}
              className="inline-block bg-purple-500 text-white py-2 px-4 rounded-md hover:bg-purple-600 mr-2 focus:outline-none focus:ring-2 focus:ring-purple-600 focus:ring-offset-2"
            >
            <FaArrowLeft />
          </Link>
        </div>
        <div className="overflow-x-auto w-full">
          <table className="min-w-full bg-white border border-gray-300 rounded-lg shadow-md">
            <thead>
              <tr className="bg-purple-500 text-white">
                {repository.parameters.map((param) => (
                  <th key={param.name} className="px-4 py-3 text-left text-sm font-semibold">
                    {param.name}
                  </th>
                ))}
                <th className="px-4 py-3 text-left text-sm font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              {records.map((record) => (
                <tr key={record._id} className="hover:bg-gray-100">
                  {repository.parameters.map((param) => (
                    <td key={param.name} className="px-4 py-2 text-sm text-gray-800">
                      {record[param.name]}
                    </td>
                  ))}
                  <td className="px-4 py-2 text-sm text-gray-800 space-x-2">
                    <Link
                      href={`/records/show/${record._id}?repository=${repository._id}`}
                      className="inline-block"
                    >
                      <FaSearch className="w-4 h-4 text-stone-700 hover:text-stone-800" title="Show Record"/>
                    </Link>
                    <Link
                      href={`/records/edit/${record._id}?repository=${repository._id}`}
                      className="inline-block"
                    >
                      <FaEdit className="w-4 h-4 text-green-500 hover:text-green-600" title="Edit Record"/>
                    </Link>
                    <button
                      onClick={() => handleDeleteClick(record)}
                      className="inline-block"
                    >
                      <FaTrash className="cursor-pointer w-4 h-4 text-red-500 hover:text-red-600" title="Delete Record"/>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {/* Confirmation Modal */}
        <ConfirmationModal
          isOpen={showModal}
          title="Confirm Deletion"
          message={`Are you sure you want to delete record "${recordToDelete?._id}" from ${repository.name}?`}
          onConfirm={confirmDelete}
          onCancel={cancelDelete}
        />
      </main>
      <Footer backgroundColor="bg-purple-500"/>
    </div>
  );
}