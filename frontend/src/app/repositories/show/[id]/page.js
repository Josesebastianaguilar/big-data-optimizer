"use client";

import { useParams } from "next/navigation";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { FaArrowLeft, FaEdit } from "react-icons/fa";
import Link from "next/link";

export default function ViewRepositoryPage() {
  const { id } = useParams();

  // Mock repository data
  const repository = {
    id,
    name: "Repository A",
    description: "This is a sample repository.",
    url: "https://example.com/repo-a",
    large_file: false,
    file_path: "",
    file_name: "data.csv",
    file_size: "1.2 MB",
    original_data_size: "500 MB",
    current_data_size: "300 MB",
    data_created_at: "2023-01-01",
    data_updated_at: "2023-05-01",
    parameters: [
      { name: "filter", type: "string", value: "active" },
      { name: "limit", type: "number", value: 100 },
    ],
    version: "1.0.0",
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 text-gray-800">
      <Header />
      <div className="flex-grow my-4 flex items-center justify-center px-4">
        {/* Top Buttons */}
        <div className="max-w-3xl w-full bg-white p-6 shadow-md rounded-lg">
          <div className="relative">
            <div className="absolute top-4 left-4">
              <Link
                href={`/repositories/edit/${repository.id}`}
                className="inline-block bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                <FaEdit className="w-4 h-4" />
              </Link>
            </div>
            <div className="absolute top-4 right-4">
              <Link
                href="/repositories"
                className="inline-block bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
              >
                <FaArrowLeft className="w-4 h-4" />
              </Link>
            </div>            
          </div>

          {/* Content */}
          <h1 className="text-3xl font-bold mb-8 text-center">View Repository</h1>
          <div className="space-y-6">
            <p className="text-lg">
              <strong>Name:</strong> {repository.name}
            </p>
            <p className="text-lg">
              <strong>Description:</strong> {repository.description || "N/A"}
            </p>
            <p className="text-lg">
              <strong>URL:</strong>{" "}
              <a
                href={repository.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline"
              >
                {repository.url}
              </a>
            </p>
            {repository.large_file ? (
              <p className="text-lg">
                <strong>File Path:</strong> {repository.file_path || "N/A"}
              </p>
            ) : (
              <p className="text-lg">
                <strong>File Name:</strong> {repository.file_name || "N/A"}
              </p>
            )}
            <p className="text-lg">
              <strong>File Size:</strong> {repository.file_size || "N/A"}
            </p>
            <p className="text-lg">
              <strong>Original Data Size:</strong> {repository.original_data_size}
            </p>
            <p className="text-lg">
              <strong>Current Data Size:</strong> {repository.current_data_size}
            </p>
            <p className="text-lg">
              <strong>Data Created At:</strong> {repository.data_created_at}
            </p>
            <p className="text-lg">
              <strong>Data Updated At:</strong> {repository.data_updated_at}
            </p>
            <p className="text-lg">
              <strong>Version:</strong> {repository.version}
            </p>
            <div>
              <strong>Parameters:</strong>
              <ul className="list-disc list-inside text-lg">
                {repository.parameters.map((param, index) => (
                  <li key={index}>
                    <strong>{param.name}</strong> ({param.type}): {param.value}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
}
