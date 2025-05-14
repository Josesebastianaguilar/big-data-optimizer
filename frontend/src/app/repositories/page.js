"use client";

import { useState } from "react";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import ConfirmationModal from "@/components/ConfirmationModal";
import { FaArchive, FaCogs, FaSearch, FaEdit, FaTrash, FaList, FaPlus, FaShareSquare, FaProjectDiagram } from "react-icons/fa";
import Link from "next/link";

export default function RepositoriesPage() {
  const [repositories, setRepositories] = useState([
    {
      _id: 1,
      name: "Repository A",
      url: "https://example.com/repo-a",
      original_data_size: "500 MB",
      current_data_size: "300 MB",
      parameters: "filter=active",
    },
    {
      _id: 2,
      name: "Repository B",
      url: "https://example.com/repo-b",
      original_data_size: "1 GB",
      current_data_size: "800 MB",
      parameters: "group=region",
    },
    {
      _id: 3,
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
      prev.filter((repo) => repo._id !== repositoryToDelete._id)
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
      <Header backgroundColor="bg-sky-600" />
      <div className="w-full max-w-6xl px-4">
        <div className="flex mt-4 sm:mt-0 justify-between items-center mb-6">
          <Link
            href="/repositories/create"
            className="bg-sky-600 hover:bg-sky-700 text-white py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-700 focus:ring-offset-2"
          >
            <FaPlus className="mr-2 inline" />
            <span>New Repository</span>
          </Link>
          <h1 className="text-3xl font-bold text-gray-800">
            <FaArchive className="w-8 h-8 text-sky-600 inline mr-2" />
            Repositories
          </h1>
        </div>
        <div className="overflow-x-auto w-full mb-4 sm:mb-0">
          <table className="min-w-full bg-white border border-gray-300 rounded-lg shadow-md">
            <thead>
              <tr className="bg-sky-600 text-white">
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
                  key={repo._id}
                  className={`${
                    index % 2 === 0 ? "bg-gray-50" : "bg-white"
                  } hover:bg-gray-100`}
                >
                  <td className="px-6 py-4 text-sm text-gray-800">{repo.name}</td>
                  <td className="px-6 py-4 text-sm text-blue-600">
                    {repo.url && <a href={repo.url} target="_blank" rel="noopener noreferrer no-underline text-slate-600">
                      <FaShareSquare className="w-4 h-4 text-sky-600" />
                    </a>}
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
                      href={`/processes?repository=${repo._id}`}
                      className="inline-block"
                    >
                      <FaProjectDiagram className="w-4 h-4 text-orange-500 hover:text-orange-600" />
                    </Link>
                    <Link
                      href={`/records?repository${repo._id}`}
                      className="inline-block"
                    >
                      <FaList className="w-4 h-4 text-purple-500 hover:text-purple-600" />
                    </Link>
                    <Link
                      href={`/repositories/show/${repo._id}`}
                      className="inline-block"
                    >
                      <FaSearch className="w-4 h-4 text-stone-700 hover:text-stone-800" />
                    </Link>
                    <Link
                      href={`/repositories/edit/${repo._id}`}
                      className="inline-block"
                    >
                      <FaEdit className="w-4 h-4 text-green-500 hover:text-green-600" />
                    </Link>
                    <Link
                      href=""
                      onClick={() => handleDeleteClick(repo)}
                      className="inline-block"
                    >
                      <FaTrash className="w-4 h-4 text-red-500 hover:text-red-600" />
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

      <Footer backgroundColor="bg-sky-600" />
    </div>
  );
}