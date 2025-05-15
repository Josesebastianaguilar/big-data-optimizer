"use client";

import React from "react";

export default function RecordForm({ repository, record = {}, onSubmit, isEdit = false }) {
  const [form, setForm] = React.useState(() =>
    repository.parameters.reduce(
      (acc, param) => ({ ...acc, [param.name]: record[param.name] || "" }),
      {}
    )
  );

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(form);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {repository.parameters.map((param) => (
        <div key={param.name}>
          <label className="block font-semibold mb-1">{param.name}</label>
          <input
            type={param.type === "number" ? "number" : "text"}
            name={param.name}
            value={form[param.name]}
            onChange={handleChange}
            className="border rounded px-3 py-2 w-full"
            required
          />
        </div>
      ))}
      <button
        type="submit"
        className="cursor-pointer bg-purple-500 hover:bg-purple-600 text-white py-2 px-4 rounded"
      >
        {isEdit ? "Update" : "Create"} Record
      </button>
    </form>
  );
}
