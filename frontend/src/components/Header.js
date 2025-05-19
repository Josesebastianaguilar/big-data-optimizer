"use client";

import NavBar from "@/components/NavBar";
import UserDropdown from "./UserDropdown";
import {FaArrowRight} from "react-icons/fa";
import { useAuth } from "@/context/AuthContext";
import { usePathname } from "next/navigation";

export default function Header({ backgroundColor, title }) {
  const { token } = useAuth();
  const pathname = usePathname();

  return (
    <header className={"w-full text-white py-4 text-center " + (backgroundColor || "bg-blue-600")}>
      {!title && (<h1 className="text-4xl font-bold">Welcome to Big Data Optimizer</h1>)}
      {title && (<h1 className="text-4xl font-bold">
        <span>Big Data Optimizer&nbsp;</span>
        <FaArrowRight className="w-6 h-6 inline" />
        <span>&nbsp;{title}</span>
        </h1>)}
      {!title && (<p className="mt-4 text-lg">
        A system to compare Big Data processing optimization processes.
      </p>)}
      <div className="flex justify-between items-center ">
        {(token || pathname === '/repositories') && <NavBar />}
        {token && <UserDropdown />}
      </div>
    </header>
  );
}