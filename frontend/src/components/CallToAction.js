export default function CallToAction() {
  return (
    <section className="w-full bg-blue-100 py-12 text-center">
      <h2 className="text-2xl font-semibold">Get Started Today</h2>
      <p className="mt-4 text-gray-700">
        Sign up now and start optimizing your big data workflows.
      </p>
      <div className="mt-6 flex justify-center gap-4">
        <a
          href="/login"
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
        >
          Login
        </a>
        <a
          href="/repositories"
          className="bg-gray-200 text-gray-800 px-6 py-3 rounded-lg hover:bg-gray-300"
        >
          Explore Repositories
        </a>
      </div>
    </section>
  );
}