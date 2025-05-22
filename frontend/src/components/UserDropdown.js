"use client";

import { useState, useRef, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from 'next/navigation'
import { FaUserCircle, FaSignOutAlt, FaChevronDown, FaSignInAlt, FaUserSlash } from "react-icons/fa";
import Link from "next/link";

export default function UserDropdown() {
  const { username, logout, token } = useAuth();
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef(null);
  const router = useRouter();

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleLogout = () => {
    logout();
    router.push("/");
  };

  return (
    <div className="relative inline-block text-left" ref={dropdownRef}>
      <button
        onClick={() => setOpen((prev) => !prev)}
        className="cursor-pointer flex items-center gap-2 px-3 py-2 rounded hover:bg-white/10 focus:outline-none"
        aria-haspopup="true"
        aria-expanded={open}
      >
        {!token && <FaUserSlash className="w-6 h-6" />}
        {token && <FaUserCircle className="w-6 h-6" />}
        {token && <span className="font-medium">{username}</span>}
        <FaChevronDown className="w-4 h-4" />
      </button>
      {open && (
        <div className="absolute right-0 mt-2 w-40 bg-white text-gray-800 rounded shadow-lg z-50">
          {!token && 
          <Link
            title="Login"
            href="/login"
            className="cursor-pointer w-full flex items-center gap-2 px-4 py-2 hover:bg-gray-100 text-left"
          >
            <FaSignInAlt className="w-4 h-4" />
            Login
          </Link>}
          {token && <button
            onClick={handleLogout}
            className="cursor-pointer w-full flex items-center gap-2 px-4 py-2 hover:bg-gray-100 text-left"
          >
            <FaSignOutAlt className="w-4 h-4" />
            Logout
          </button>}
        </div>
      )}
    </div>
  );
}