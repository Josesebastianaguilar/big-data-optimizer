"use client";

import { useState, useEffect } from "react";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import Paginator from "@/components/Paginator";
import PageSize from "@/components/PageSize";
import ConfirmationModal from "@/components/ConfirmationModal";
import { FaArchive, FaSearch, FaEdit, FaTrash, FaList, FaPlus, FaShareSquare, FaProjectDiagram, FaSpinner } from "react-icons/fa";
import { useAuth } from "@/context/AuthContext";
import { useSnackbar } from "@/components/SnackbarContext";
import api from "@/app/api";
import Link from "next/link";

export default function RepositoriesPage() {
  const { showSnackbar } = useSnackbar();
  const { token, role, authLoading } = useAuth();
  const [loading, setLoading] = useState(true);
  const [repositories, setRepositories] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [limit, setLimit] = useState(10);
  const [totalItems, setTotalItems] = useState(0);
  
  const fetchRepositories = async (newPage = 1, newLimit = 1) => {
    try {
      setLoading(true);
      const response = await api.get(`/repositories/?page=${newPage}&limit=${newLimit}`);
      if (page > response.data.totalPages && response.data.items.length) {
        fetchRepositories(1, 10);
        showSnackbar("Current page exceeds total pages, resetting to page 1", "warning", true, "bottom-right");
      }
      else {
        setPage(newPage || 1);
        setLimit(newLimit || 10);
        setRepositories(response.data.items);
        setTotalPages(response.data.totalPages);
        setTotalItems(response.data.totalItems);

      }
    } catch (error) {
      showSnackbar("Error fetching repositories", "error", false, "bottom-right");
      console.error("Error fetching repositories:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (authLoading) return;
    fetchRepositories(1, 10); 
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authLoading]);
  

  const [showModal, setShowModal] = useState(false);
  const [repositoryToDelete, setRepositoryToDelete] = useState(null);

  const handleDeleteClick = (repo) => {
    setRepositoryToDelete(repo);
    setShowModal(true);
  };

  const confirmDelete = async() => {
    try {
      await api.delete(`/repositories/${repositoryToDelete._id.$oid}`);
      setRepositories(prev => prev.filter((repo) => repo._id.$oid !== repositoryToDelete._id.$oid));
      setShowModal(false);
      showSnackbar(`Repository "${repositoryToDelete.name}" deleted successfully`, "success", true, "bottom-right");
      showSnackbar(`The system will take some time to delete all records and processes of ${repositoryToDelete.name}.`, "info", false, "bottom-right");
      setRepositoryToDelete(null);
      setTotalItems(prev => prev - 1);
      
    } catch (error) {
      showSnackbar(`Error deleting repository ${repositoryToDelete?.name}`, "error", false, "bottom-right");
      console.error("Error deleting repository:", error);
    }
  };

  const cancelDelete = () => {
    setShowModal(false);
    setRepositoryToDelete(null);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-between bg-gray-50 text-gray-800">
      <Header backgroundColor="bg-sky-600" title="Repositories" />
      <main className="w-full max-w-6xl px-4">
        <div className="flex sm:mt-0 justify-between items-center mb-6 mt-6 sm:mt-4">
          {token && role === 'admin' && <Link
            href="/repositories/create"
            className="bg-sky-600 hover:bg-sky-700 text-white py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-700 focus:ring-offset-2"
          >
            <FaPlus className="mr-2 inline" />
            <span>New Repository</span>
          </Link>}
          <h1 className="text-3xl font-bold text-gray-800">
            <FaArchive className="w-8 h-8 text-sky-600 inline mr-2" />
            Repositories
          </h1>
        </div>
        {loading&& <div className="flex justify-center min-w-full"><FaSpinner className="text-center animate-spin inline mr-2 h-8 w-8" /></div>}
        {!loading && <div className="overflow-x-auto w-full mb-4 sm:mb-0">
          <div className="flex justify-end my-2">
            <PageSize page={page} value={limit} onChange={fetchRepositories}/>
          </div>
          <table className="min-w-full bg-white border border-gray-300 rounded-lg shadow-md">
            <thead>
              <tr className="bg-sky-600 text-white">
                <th className="px-6 py-3 text-center text-sm font-semibold">Name</th>
                <th className="px-6 py-3 text-center text-sm font-semibold">URL</th>
                <th className="px-6 py-3 text-center text-sm font-semibold">
                  Initial # of Records
                </th>
                <th className="px-6 py-3 text-center text-sm font-semibold">
                  Current # of Records
                </th>
                <th className="px-6 py-3 text-center text-sm font-semibold">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {repositories.map((repo, index) => (
                <tr
                  key={repo._id.$oid}
                  className={`${
                    index % 2 === 0 ? "bg-gray-50" : "bg-white"
                  } hover:bg-gray-100`}
                >
                  <td className="px-6 py-4 text-sm text-gray-800">{repo.name}</td>
                  <td className="text-center px-6 py-4 text-sm text-blue-600">
                    {repo.url && <a href={repo.url} target="_blank" rel="noopener noreferrer no-underline text-slate-600">
                      <FaShareSquare className="w-4 h-4 text-sky-600" />
                    </a>}
                    {!repo.url && <span className="text-gray-400">-</span>}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-800 text-center">
                    {repo.original_data_size}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-800 text-center">
                    {repo.current_data_size}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-800 space-x-2 text-center">
                    {token && repo.data_ready && <Link
                      title="Show Repository Processes"
                      href={`/processes?repository=${repo._id.$oid}`}
                      className="inline-block"
                    >
                      <FaProjectDiagram className="w-4 h-4 text-orange-500 hover:text-orange-600" />
                    </Link>}
                    {repo.data_ready && <Link
                      title="Show Repository Records"
                      href={`/records?repository=${repo._id.$oid}`}
                      className="inline-block"
                    >
                      <FaList className="w-4 h-4 text-purple-500 hover:text-purple-600" />
                    </Link>}
                    <Link
                      title="Show Repository"
                      href={`/repositories/show/${repo._id.$oid}`}
                      className="inline-block"
                    >
                      <FaSearch className="w-4 h-4 text-stone-700 hover:text-stone-800" />
                    </Link>
                    {token && role === 'admin' && <Link
                      title="Edit Repository"
                      href={`/repositories/edit/${repo._id.$oid}`}
                      className="inline-block"
                    >
                      <FaEdit className="w-4 h-4 text-green-500 hover:text-green-600" />
                    </Link>}
                    {token && role === 'admin' && <button
                      title="Delete Repository"
                      onClick={() => handleDeleteClick(repo)}
                      className="inline-block"
                    >
                      <FaTrash className="cursor-pointer w-4 h-4 text-red-500 hover:text-red-600" />
                    </button>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="flex justify-end my-2">
            <Paginator
              page={page}
              totalPages={totalPages}
              module="repositories"
              limit={limit}
              totalItems={totalItems}
              onPageChange={fetchRepositories}
              activeBackgroundColor="bg-sky-600"
            />
          </div>
        </div>}
      </main>

      {/* Confirmation Modal */}
      <ConfirmationModal
        isOpen={showModal}
        title="Confirm Deletion"
        message={`Are you sure you want to delete "${repositoryToDelete?.name}" with all its records and processes?`}
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />

      <Footer backgroundColor="bg-sky-600" />
    </div>
  );
}