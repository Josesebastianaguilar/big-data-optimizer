"use client";

import { useState } from "react";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import ConfirmationModal from "@/components/ConfirmationModal";
import { FaArchive, FaChartBar, FaSearch, FaEdit, FaTrash } from "react-icons/fa";
import Link from "next/link";

export default function RepositoriesPage() {
  const [repositories, setRepositories] = useState([
    {
      id: 1,
      name: "Repository A",
      url: "https://example.com/repo-a",
      original_data_size: "500 MB",
      current_data_size: "300 MB",
      parameters: "filter=active",
    },
    {
      id: 2,
      name: "Repository B",
      url: "https://example.com/repo-b",
      original_data_size: "1 GB",
      current_data_size: "800 MB",
      parameters: "group=region",
    },
    {
      id: 3,
      name: "Repository C",
      url: "https://example.com/repo-c",
      original_data_size: "2 GB",
      current_data_size: "1.5 GB",
      parameters: "aggregate=sum",
    },
  ]);

  const [showModal, setShowModal] = useState(false);
  const [repositoryToDelete, setRepositoryToDelete] = useState(null);

  const handleDeleteClick = (repo) => {
    setRepositoryToDelete(repo);
    setShowModal(true);
  };

  const confirmDelete = () => {
    setRepositories((prev) =>
      prev.filter((repo) => repo.id !== repositoryToDelete.id)
    );
    setShowModal(false);
    setRepositoryToDelete(null);
  };

  const cancelDelete = () => {
    setShowModal(false);
    setRepositoryToDelete(null);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-between bg-gray-50 text-gray-800">
      <Header />
      <div className="w-full max-w-6xl px-4">
        <div className="flex mt-4 sm:mt-0 justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800">
            <FaArchive className="w-8 h-8 text-blue-600 inline mr-2" />
            Repositories
          </h1>
          <Link
            href="/repositories/create"
            className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
          >
            Create Repository
          </Link>
        </div>
        <div className="overflow-x-auto w-full mb-4 sm:mb-0">
          <table className="min-w-full bg-white border border-gray-300 rounded-lg shadow-md">
            <thead>
              <tr className="bg-blue-600 text-white">
                <th className="px-6 py-3 text-left text-sm font-semibold">Name</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">URL</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">
                  Original Data Size
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold">
                  Current Data Size
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold">
                  Parameters
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {repositories.map((repo, index) => (
                <tr
                  key={repo.id}
                  className={`${
                    index % 2 === 0 ? "bg-gray-50" : "bg-white"
                  } hover:bg-gray-100`}
                >
                  <td className="px-6 py-4 text-sm text-gray-800">{repo.name}</td>
                  <td className="px-6 py-4 text-sm text-blue-600">
                    <a href={repo.url} target="_blank" rel="noopener noreferrer">
                      {repo.url}
                    </a>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-800">
                    {repo.original_data_size}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-800">
                    {repo.current_data_size}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-800">
                    {repo.parameters}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-800 space-x-2">
                    <Link
                      href={`/processes/repository/${repo.id}`}
                      className="inline-block bg-gray-500 text-white py-1 px-3 rounded-md hover:bg-gray-600"
                    >
                      <FaChartBar className="w-4 h-4" />
                    </Link>
                    <Link
                      href={`/repositories/show/${repo.id}`}
                      className="inline-block bg-blue-500 text-white py-1 px-3 rounded-md hover:bg-blue-600"
                    >
                      <FaSearch className="w-4 h-4" />
                    </Link>
                    <Link
                      href={`/repositories/edit/${repo.id}`}
                      className="inline-block bg-green-500 text-white py-1 px-3 rounded-md hover:bg-green-600"
                    >
                      <FaEdit className="w-4 h-4" />
                    </Link>
                    <Link
                      href=""
                      onClick={() => handleDeleteClick(repo)}
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
      </div>

      {/* Confirmation Modal */}
      <ConfirmationModal
        isOpen={showModal}
        title="Confirm Deletion"
        message={`Are you sure you want to delete "${repositoryToDelete?.name}"?`}
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />

      <Footer />
    </div>
  );
}