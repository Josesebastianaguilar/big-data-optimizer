"use client";

import RepositoryForm from "@/components/RepositoryForm";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { useRouter, useParams } from "next/navigation";
import { useState, useEffect } from "react";
import { FaArrowLeft, FaArchive } from "react-icons/fa";
import Link from "next/link";

export default function EditRepositoryPage() {
  const { id } = useParams();
  const router = useRouter();
  const [repository, setRepository] = useState(null);

  useEffect(() => {
    // Simulate fetching repository data
    const mockRepository = {
      id,
      name: "Repository A",
      description: "A sample repository",
      url: "https://example.com/repo-a",
      large_file: false,
      file_path: "",
      parameters: [
        { name: "filter", type: "string" },
        { name: "limit", type: "number" },
      ],
    };
    setRepository(mockRepository);
  }, [id]);

  const handleUpdate = (data) => {
    console.log("Updating repository:", data);
    // Simulate API call
    setTimeout(() => {
      alert("Repository updated successfully!");
      router.push("/repositories");
    }, 1000);
  };

  if (!repository) return <div>Loading...</div>;

  return (
     <div className="min-h-screen flex flex-col bg-gray-50 text-gray-800">
      <Header backgroundColor="bg-sky-600" title="Repositories"/>
      <main className="flex-grow my-4 flex items-center justify-center px-4">
        <div className="max-w-2xl w-full bg-white p-6 shadow-md rounded-lg">
           <div className="flex justify-end items-center">
            <div>
              <Link
                title="Go Back"
                href="/repositories"
                className="inline-block bg-sky-600 text-white py-2 px-4 rounded-md hover:bg-sky-700 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2"
              >
                <FaArrowLeft className="w-4 h-4" />
              </Link>
            </div>            
          </div>
          <h1 className="text-3xl font-extrabold text-gray-900 text-center mb-6">
            <FaArchive className="w-8 h-8 text-sky-600 inline mr-2" /> Edit Repository
          </h1>
          <RepositoryForm type="edit" initialData={repository} onSubmit={handleUpdate} />
        </div>
      </main>
      <Footer backgroundColor="bg-sky-600"/>
    </div>
  );
}
