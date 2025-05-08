"use client";

import Link from "next/link";
import { FaHome, FaArchive } from "react-icons/fa";

export default function NavBar() {
  return (
    <nav className="bg-blue-600 text-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Navigation Links */}
          <div className="hidden md:flex space-x-6">
            <Link
              href="/"
              className="flex items-center text-sm font-medium hover:underline"
            >
              <FaHome className="mr-2" />
              Home
            </Link>
            <Link
              href="/repositories"
              className="flex items-center text-sm font-medium hover:underline"
            >
              <FaArchive className="mr-2" />
              Repositories
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}