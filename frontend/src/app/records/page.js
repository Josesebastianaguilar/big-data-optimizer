"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import Header from "@/components/Header";
import Paginator from "@/components/Paginator";
import PageSize from "@/components/PageSize";
import Footer from "@/components/Footer";
import ConfirmationModal from "@/components/ConfirmationModal";
import { FaArrowLeft, FaPlus, FaSearch, FaEdit, FaTrash, FaDatabase, FaSpinner } from "react-icons/fa";
import { useSnackbar } from "@/components/SnackbarContext";
import api from "@/app/api";

export default function RecordsListPage() {
  const { showSnackbar } = useSnackbar();
  const searchParams = useSearchParams();
  const { role, authLoading } = useAuth();
  const [showModal, setShowModal] = useState(false);
  const [recordToDelete, setRecordToDelete] = useState(null);
  const [loading, setLoading] = useState(true);
  const [records, setRecords] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [repository, setRepository] = useState({});
  const [limit, setLimit] = useState(10);
  const [totalItems, setTotalItems] = useState(0);

  const fetchRepository = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/repositories/?_id=${searchParams.get("repository")}`);
      setRepository(response.data.items[0] || {});
    } catch (error) {
      showSnackbar("Error fetching repository details", "error", false, "bottom-right");
      console.error("Error fetching repositories:", error);
    } finally {
      setLoading(false);
    }
  };
  
  const fetchRecords = async (newPage = 1, newLimit = 1) => {
    try {
      setLoading(true);
      const response = await api.get(`/records/${searchParams.get("repository")}?page=${newPage}&limit=${newLimit}`);
      if (page > response.data.totalPages) {
        fetchRecords(1, 10);
        showSnackbar("Current page exceeds total pages, resetting to page 1", "warning", true, "bottom-right");
      } else {
        setPage(newPage || 1);
        setLimit(newLimit || 10);
        setRecords(response.data.items);
        setTotalPages(response.data.totalPages);
        setTotalItems(response.data.totalItems);
      }
    } catch (error) {
      showSnackbar("Error fetching records", "error", false, "bottom-right");
      console.error("Error fetching repositories:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (authLoading) return;
    if (!searchParams.get("repository")) {
      router.push("/");
      return;
    }
    fetchRepository(); 
    fetchRecords(1, 10);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authLoading]);

  const handleDeleteClick = (record) => {
    setRecordToDelete(record);
    setShowModal(true);
  };

  const confirmDelete = async () => {
    try {
      await api.delete(`/records/${recordToDelete._id.$oid}`);
      showSnackbar(`Record "${recordToDelete._id.$oid}" deleted successfully`, "success", true, "bottom-right");
      setRecords(prev => prev.filter((repo) => repo._id.$oid !== recordToDelete._id.$oid));
      setRepository(prev => ({
        ...prev,
        current_data_size: prev.current_data_size - 1,
      }));
      setTotalItems(prev => prev - 1);
      setShowModal(false);
      setRecordToDelete(null);
    } catch (error) {
      showSnackbar(`Error deleting record ${recordToDelete?._id.$oid}`, "error", false, "bottom-right");
      console.error("Error deleting repository:", error);
    }
  };

  const cancelDelete = () => {
    setShowModal(false);
    setRecordToDelete(null);
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 text-gray-800">
      <Header backgroundColor="bg-purple-500" title="Records"/>
      <main className="flex-grow max-w-8xl mx-auto w-full px-4 py-8">
        <div className="flex justify-between items-center mb-6 mt-6 sm:mt-0">
          {role && role === 'admin' && <Link
            href={`/records/create?repository=${repository?._id?.$oid}`}
            className="mr-2 bg-purple-500 hover:bg-purple-600 text-white py-2 px-4 rounded-md flex items-center focus:outline-none focus:ring-2 focus:ring-purple-600 focus:ring-offset-2"
          >
            <FaPlus className="mr-2" /> New Record
          </Link>}
          <div>
            <FaDatabase className="w-6 h-6 inline text-purple-500 mr-2" />
            <span className="text-2xl font-bold">{repository?.name} Records</span>
          </div>
          <Link
              title="Go Back"
              href={`/repositories/`}
              className="inline-block bg-purple-500 text-white py-2 px-4 rounded-md hover:bg-purple-600 mr-2 focus:outline-none focus:ring-2 focus:ring-purple-600 focus:ring-offset-2"
            >
            <FaArrowLeft />
          </Link>
        </div>
        {!loading && <div className="flex justify-end items-center mb-6 mt-6 sm:mt-0">
          <PageSize page={page} value={limit} onChange={fetchRecords}/>
          </div>}
        {loading && <div className="flex justify-center min-w-full"><FaSpinner className="text-center animate-spin inline mr-2 h-8 w-8" /></div>}
        {!loading && <div className="overflow-x-auto w-full">
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
                <tr key={record._id.$oid} className="hover:bg-gray-100">
                  {repository.parameters.map((param) => (
                    <td key={param.name} className="px-4 py-2 text-sm text-gray-800 text-center">
                      {typeof record.data[param.name] !== 'object' ? (record.data[param.name]|| '-') : '[Object]'}
                    </td>
                  ))}
                  <td className="px-2 py-2 text-sm text-gray-800 justify-between align-middle">
                    <Link
                      href={`/records/show/${record._id.$oid}?repository=${repository._id.$oid}`}
                      className="inline-block"
                    >
                      <FaSearch className="w-4 h-4 text-stone-700 hover:text-stone-800" title="Show Record"/>
                    </Link>
                    {role && role === 'admin' && repository.data_ready && <Link
                      href={`/records/edit/${record._id.$oid}?repository=${repository._id.$oid}`}
                      className="inline-block"
                    >
                      <FaEdit className="w-4 h-4 text-green-500 hover:text-green-600 mr-2 ml-2" title="Edit Record"/>
                    </Link>}
                    {role && role === 'admin' && repository.data_ready && <button
                      onClick={() => handleDeleteClick(record)}
                      className="inline-block"
                    >
                      <FaTrash className="cursor-pointer w-4 h-4 text-red-500 hover:text-red-600" title="Delete Record"/>
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
              onPageChange={fetchRecords}
              module="records"
              limit={limit}
              totalItems={totalItems}
              activeBackgroundColor="bg-purple-500"
            />
          </div>
        </div>}
        {/* Confirmation Modal */}
        <ConfirmationModal
          isOpen={showModal}
          title="Confirm Deletion"
          message={`Are you sure you want to delete record "${recordToDelete?._id.$oid}" from ${repository.name}? This will change the respository version`}
          onConfirm={confirmDelete}
          onCancel={cancelDelete}
        />
      </main>
      <Footer backgroundColor="bg-purple-500"/>
    </div>
  );
}