export default function Footer({backgroundColor}) {
  return (
    <footer className={"w-full text-white py-6 text-center " + (backgroundColor || "bg-gray-800")}>
      <p>
        © {new Date().getFullYear()} Big Data Optimizer. All rights reserved.
      </p>
      <div className="mt-4 flex justify-center gap-4">
        <a
          href="https://github.com/Josesebastianaguilar/big-data-optimizer.git"
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