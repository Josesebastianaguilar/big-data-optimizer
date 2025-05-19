"use client";

export default function Footer({backgroundColor}) {
  const repository_url = process.env.NEXT_PUBLIC_REPOSITORY_URL || "https://github.com/";
  return (
    <footer className={"w-full text-white py-6 text-center " + (backgroundColor || "bg-gray-800")}>
      <p>
        © {new Date().getFullYear()} Big Data Optimizer. All rights reserved.
      </p>
      <div className="mt-4 flex justify-center gap-4">
        <a
          href={repository_url}
          target="_blank"
          rel="noopener noreferrer"
          className="hover:underline"
        >
          GitHub
        </a>
      </div>
    </footer>
  );
}