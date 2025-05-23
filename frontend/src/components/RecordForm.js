"use client";

import React from "react";
import { useState } from "react";
import { FaSpinner } from "react-icons/fa";
import { useRouter } from "next/navigation";

export default function RecordForm({ repository, record = {}, onSubmit, isEdit = false }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState(() =>
    repository.parameters.reduce(
      (acc, param) => ({ ...acc, [param.name]: (isEdit? record.data[param.name] : record[param.name]) || "" }),
      {}
    )
  );

  const handleChange = (name, value, param_type) => {
    setForm({ ...form, [name]: value ? (param_type === "string" ? value : Number(value)) : null});
  };

  const handleSubmit = async (e) => {
    try {
      e.preventDefault();
      setLoading(true);

      await onSubmit(form);

      router.push(`/records?repository=${repository._id.$oid}`);
    } catch (error) {
      console.error("Error submitting form:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {repository.parameters.map((param) => (
        <div key={`${repository._id.$oid}_${param.name}`}>
          <label className="block font-semibold mb-1">{param.name}</label>
          <input
            type={param.type === "number" ? "number" : "text"}
            name={param.name}
            disabled={loading}
            value={ param.type === "string" ? (form[param.name] ? (typeof form[param.name] === 'object' ? JSON.stringify(form[param.name]) : form[param.name]) : "") : (form[param.name] ? Number(form[param.name]) : "")}
            onChange={(e) => handleChange(e.target.name, e.target.value, param.type)}
            className="border rounded px-3 py-2 w-full"
            required
          />
        </div>
      ))}
      <button
        type="submit"
        disabled={loading}
        className="cursor-pointer bg-purple-500 hover:bg-purple-600 text-white py-2 px-4 rounded"
      >
        {loading && <FaSpinner className="animate-spin inline mr-2 white" />}
        {isEdit ? "Update" : "Create"} Record
      </button>
      <div className="flex justify-center text-sm items-center mb-6 mt-6 sm:mt-0">
        By {!isEdit ? "creating a" : "modifying this"} record, the version of the repository will be updated to&nbsp;<strong>{repository.version + 1}</strong>.
      </div>
    </form>
  );
}
