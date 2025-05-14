"use client";

import { useState, useEffect } from "react";

export default function RepositoryForm({
  type, // "create" or "edit"
  initialData = {}, // Initial data for edit view
  onSubmit,
}) {
  const [name, setName] = useState(initialData.name || "");
  const [description, setDescription] = useState(initialData.description || "");
  const [url, setUrl] = useState(initialData.url || "");
  const [file, setFile] = useState(null);
  const [largeFile, setLargeFile] = useState(initialData.large_file || false);
  const [filePath, setFilePath] = useState(initialData.file_path || "");
  const [parameters, setParameters] = useState(initialData.parameters || []);
  const [changeFile, setChangeFile] = useState(false); // For edit view

  useEffect(() => {
    console.log("filePath:", filePath);
    console.log("largeFile:", largeFile);
    console.log("file:", file);
  }, [filePath, largeFile, file]);

  const handleSubmit = (e) => {
    e.preventDefault();

    // Validation for create view
    if (type === "create" && !largeFile && !file) {
      alert("You must upload a CSV file or enable 'Large File' and provide a file path.");
      return;
    }

    // Validation for edit view
    if (type === "edit" && changeFile && !largeFile && !file) {
      alert("You must upload a CSV file or enable 'Large File' and provide a file path.");
      return;
    }

    const formData = {
      name,
      description,
      url,
      large_file: largeFile,
      file_path: largeFile ? filePath : null,
      file: largeFile ? null : file,
      parameters,
    };

    onSubmit(formData);
  };

  const handleLargeFileToggle = (e) => {
    setLargeFile(e.target.checked);
    if (!e.target.checked) {
      setFilePath(""); // Reset filePath when largeFile is unchecked
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Name */}
      <div>
        <label className="block text-sm font-medium text-gray-700">Name</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          required
        />
      </div>

      {/* Description */}
      <div>
        <label className="block text-sm font-medium text-gray-700">Description</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
        />
      </div>

      {/* URL */}
      <div>
        <label className="block text-sm font-medium text-gray-700">URL</label>
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
        />
      </div>

      {/* File or Large File */}
      {type === "edit" && (
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Change File or Large File
          </label>
          <input
            type="checkbox"
            checked={changeFile}
            onChange={(e) => setChangeFile(e.target.checked)}
            className="mr-2"
          />
          <span>Check to change file or enable large file</span>
        </div>
      )}
      {(type === "create" || changeFile) && (
        <>
          <div>
            <label className="block text-sm font-medium text-gray-700">Large File</label>
            <input
              type="checkbox"
              checked={largeFile}
              onChange={handleLargeFileToggle}
              className="mr-2"
            />
            <span>Enable Large File</span>
          </div>
          {largeFile ? (
            <div>
              <label className="block text-sm font-medium text-gray-700">File Path</label>
              <input
                type="text"
                value={filePath}
                onChange={(e) => setFilePath(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                required
              />
            </div>
          ) : (
            <div>
              <label className="block text-sm font-medium text-gray-700">CSV File</label>
              <input
                type="file"
                onChange={(e) => setFile(e.target.files[0])}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                required={type === "create"}
              />
            </div>
          )}
        </>
      )}

      {/* Parameters (Edit View Only) */}
      {type === "edit" && (
        <div>
          <label className="block text-sm font-medium text-gray-700">Parameters</label>
          <div className="space-y-2">
            {parameters.map((param, index) => (
              <div key={index} className="flex items-center space-x-4">
                <input
                  type="text"
                  value={param.name}
                  onChange={(e) => {
                    const updatedParams = [...parameters];
                    updatedParams[index].name = e.target.value;
                    setParameters(updatedParams);
                  }}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="Parameter Name"
                  disabled
                />
                <select
                  value={param.type}
                  onChange={(e) => {
                    const updatedParams = [...parameters];
                    updatedParams[index].type = e.target.value;
                    setParameters(updatedParams);
                  }}
                  className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                >
                  <option value="string">String</option>
                  <option value="number">Number</option>
                </select>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        className="cursor-pointer w-full sm:w-1/2 md:w-2/5 lg:w-1/5 bg-sky-600 text-white py-2 px-4 rounded-md hover:bg-sky-700 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2"
      >
        {type === "create" ? "Create" : "Update"}
      </button>
    </form>
  );
}
