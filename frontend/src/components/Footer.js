export default function Footer() {
  return (
    <footer className="w-full bg-gray-800 text-white py-6 text-center">
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