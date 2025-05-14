"use client";

import { useState } from "react";
import Link from "next/link";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import ConfirmationModal from "@/components/ConfirmationModal";
import { FaArrowLeft, FaPlus, FaSearch, FaEdit, FaTrash, FaArchive } from "react-icons/fa";

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
      <Header />
      <div className="max-w-6xl mx-auto w-full px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <Link
            href={`/records/create?repository=${repository._id}`}
            className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md flex items-center"
          >
            <FaPlus className="mr-2" /> New Record
          </Link>
          <div>
            <FaArchive className="w-8 h-8 text-blue-600 inline mr-2" />
            <span className="text-2xl font-bold">{repository.name} Records</span>
          </div>
          <Link
              href={`/repositories/`}
              className="inline-block bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 mr-2"
            >
            <FaArrowLeft />
          </Link>
        </div>
        <div className="overflow-x-auto w-full">
          <table className="min-w-full bg-white border border-gray-300 rounded-lg shadow-md">
            <thead>
              <tr className="bg-blue-600 text-white">
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
                      className="inline-block bg-blue-500 text-white py-1 px-3 rounded-md hover:bg-blue-600"
                    >
                      <FaSearch className="w-4 h-4" />
                    </Link>
                    <Link
                      href={`/records/edit/${record._id}?repository=${repository._id}`}
                      className="inline-block bg-green-500 text-white py-1 px-3 rounded-md hover:bg-green-600"
                    >
                      <FaEdit className="w-4 h-4" />
                    </Link>
                    <Link
                      href=""
                      onClick={() => handleDeleteClick(record)}
                      className="inline-block bg-red-500 text-white py-1 px-3 rounded-md hover:bg-red-600"
                    >
                      <FaTrash className="w-4 h-4" />
                    </Link>
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
      </div>
      <Footer />
    </div>
  );
}