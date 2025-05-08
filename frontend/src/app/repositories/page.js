"use client";

import { useState } from "react";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { FaArchive } from "react-icons/fa";

export default function RepositoriesPage() {
  // Mock data for repositories
  const [repositories] = useState([
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

  return (
    <div className="min-h-screen flex flex-col items-center justify-between bg-gray-50 text-gray-800">
      <Header />
      <h1 className="text-3xl font-bold text-gray-800 mb-6">
        <FaArchive className="w-8 h-8 text-blue-600 inline mr-2" />
        Repositories
      </h1>
      <div className="overflow-x-auto w-full px-4">
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
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <Footer />
    </div>
  );
}