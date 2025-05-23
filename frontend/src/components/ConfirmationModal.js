"use client";

import { FaSpinner } from "react-icons/fa";
import { useState } from "react";

export default function ConfirmationModal({ isOpen, title, message, onConfirm, onCancel }) {
  const [loading, setLoading] = useState(false);
  if (!isOpen) return null;
  const handleConfirm = async () => {
    try {
      setLoading(true);
      await onConfirm();
    }
    catch (error) {
      console.error("Error confirming action:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 modal-overlay flex items-center justify-center z-40">
      <div className="bg-white p-6 rounded-lg shadow-lg max-w-sm w-full z-50">
        <h2 className="text-lg font-bold mb-4">{title}</h2>
        <p className="mb-4">{message}</p>
        <div className="flex justify-end space-x-4">
          <button
            onClick={onCancel}
            disabled={loading}
            className="cursor-pointer bg-gray-500 text-white py-2 px-4 rounded-md hover:bg-gray-600"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={loading}
            className="cursor-pointer bg-red-500 text-white py-2 px-4 rounded-md hover:bg-red-600"
          >
            {loading && <FaSpinner className="animate-spin inline mr-2 white" />}
            Confirm
          </button>
        </div>
      </div>
    </div>
  );
}
