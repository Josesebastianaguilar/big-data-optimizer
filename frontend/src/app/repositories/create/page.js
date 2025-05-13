"use client";

import RepositoryForm from "@/components/RepositoryForm";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { useRouter } from "next/navigation";
import { FaArrowLeft } from "react-icons/fa";
import Link from "next/link";

export default function CreateRepositoryPage() {
  const router = useRouter();

  const handleCreate = (data) => {
    console.log("Creating repository:", data);
    // Simulate API call
    setTimeout(() => {
      alert("Repository created successfully!");
      router.push("/repositories");
    }, 1000);
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 text-gray-800">
      <Header />
      <div className="flex-grow my-4 flex items-center justify-center px-4">
        <div className="max-w-2xl w-full bg-white p-6 shadow-md rounded-lg">
          <div className="relative">
            <div className="absolute top-4 right-4">
              <Link
                href="/repositories"
                className="inline-block bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
              >
                <FaArrowLeft className="w-4 h-4" />
              </Link>
            </div>            
          </div>
          <h1 className="text-3xl font-extrabold text-gray-900 text-center mb-6">
            Create Repository
          </h1>
          <RepositoryForm type="create" onSubmit={handleCreate} />
        </div>
      </div>
      <Footer />
    </div>
  );
}
