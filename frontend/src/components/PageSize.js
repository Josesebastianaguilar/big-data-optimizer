import React from "react";

export default function PageSizeSelector({ page, value, options = [1, 5, 10, 20, 50, 100], onChange }) {
  return (
    <div className="flex items-center gap-2">
      <label htmlFor="page-size" className="text-sm text-gray-700">Rows per page:</label>
      <select
        id="page-size"
        value={value}
        onChange={e => onChange(page, Number(e.target.value))}
        className="cursor-pointer border rounded px-2 py-1 text-sm"
      >
        {options.map(opt => (
          <option key={opt} value={opt}>{opt}</option>
        ))}
      </select>
    </div>
  );
}