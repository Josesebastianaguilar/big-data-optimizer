"use client";

import AuthForm from "@/components/AuthForm";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import api from "@/app/api";
import Link from "next/link";
import { FaArrowLeft } from "react-icons/fa";
import { useAuth } from "@/context/AuthContext";
import { useEffect } from "react";
import { useRouter } from 'next/navigation'

export default function LoginPage() {
  const router = useRouter()
  const { token, login } = useAuth();
  useEffect(() => {
    if (token) {
      router.push("/");
    }
  }, [token, router]);
  
  const handleLogin = async (data) => {
    try {
      const response = await api.post("/auth/login/", data);
      const { access_token, username, role } = response.data;
      login(access_token, username, role);
      router.push("/");
      
      return;
    } catch (error) {
      throw new Error(`Error during login: ${error?.message}. Detail: ${error?.response?.data?.detail}`);
    }
  };

  return (
  <div className="min-h-screen flex flex-col items-center justify-between bg-gray-50 text-gray-800">
    <Header/>
    <main className="w-full max-w-md px-4">
      <div className="flex justify-end items-center mt-4 sm:mt-0 mb-4">
          <Link
              title="Go Back"
              href="/"
              className="inline-block bg-gray-700 text-white py-2 px-4 rounded-md hover:bg-gray-800 mr-2 focus:outline-none focus:ring-2 focus:ring-gray-800 focus:ring-offset-2"
            >
            <FaArrowLeft />
          </Link>
        </div>
      <div className="overflow-x-auto w-full mb-4 sm:mb-0">
        <AuthForm type="login" onSubmit={handleLogin} />
      </div>
    </main>
    <Footer />
</div>);
}