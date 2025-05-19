"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { FaHome, FaArchive } from "react-icons/fa";
import { useAuth } from "@/context/AuthContext";

export default function NavBar() {
  const pathname = usePathname();
  const { token } = useAuth();
  

  return (
    <nav className="text-white ">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-8">
          <div className="md:flex space-x-6">
            <Link
              href="/"
              className={`flex items-center text-lg font-medium ${
                pathname === "/" ? "underline font-bold" : "hover:underline"
              }`}
            >
              <FaHome className="mr-2" />
              Home
            </Link>
            {token && <Link
              href="/repositories"
              className={`flex items-center text-lg font-medium ${
                pathname === "/repositories" ? "underline font-bold" : "hover:underline"
              }`}
            >
              <FaArchive className="mr-2" />
              Repositories
            </Link>}
          </div>
        </div>
      </div>
    </nav>
  );
}
