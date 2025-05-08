"use client";

import AuthForm from "@/components/AuthForm";
import Link from "next/link";
import { FaHome } from "react-icons/fa";

export default function RegisterPage() {
  const handleRegister = async (data) => {
    try {
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error("Registration failed");
      }

      const result = await response.json();
      console.log("Registration successful:", result);
      // Redirect or handle successful registration
    } catch (error) {
      console.error("Error during registration:", error.message);
    }
  };

  return (
    <div>
      <div className="flex flex-col items-center">
        <Link href="/" className="mt-4 text-blue-600 hover:underline text-sm font-medium">
          <FaHome className="w-16 h-16 text-blue-600" />
        </Link>
      </div>
      <AuthForm type="register" onSubmit={handleRegister} />
    </div>
  );
}