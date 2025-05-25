"use client";
import {FaGithub, FaLinkedin, FaEnvelope} from "react-icons/fa";

export default function Footer({backgroundColor}) {
  return (
    <footer className={"w-full text-white py-6 text-center " + (backgroundColor || "bg-gray-800")}>
      <p>
        © {new Date().getFullYear()} Big Data Optimizer. All rights reserved.
      </p>
      <div className="mt-4 flex justify-center gap-4">
        <a
          href={process.env.NEXT_PUBLIC_REPOSITORY_URL || "https://github.com/"}
          target="_blank"
          rel="noopener noreferrer"
          className="hover:underline"
        >
          <FaGithub className="h4 w-4"/>
        </a>
        <a
          href={process.env.NEXT_PUBLIC_LINKEDIN_URL || "https://www.linkedin.com/in/"}
          target="_blank"
          className="hover:underline"
        >
          <FaLinkedin className="h4 w-4"/>
        </a>
        <a
          href={process.env.NEXT_PUBLIC_EMAIL}
          className="hover:underline"
        >
          <FaEnvelope className="h4 w-4"/>
        </a>
      </div>
      <div className="mt-4 flex justify-center gap-4">
        <div
          className="text-sm"
        >
          Developed by {process.env.NEXT_PUBLIC_AUTHOR}
        </div>
      </div>
    </footer>
  );
}