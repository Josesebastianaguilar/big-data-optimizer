import { FaFilter, FaLayerGroup, FaChartBar, FaClock } from "react-icons/fa";

export default function FeaturesSection() {
  return (
    <main className="flex flex-col items-center py-12 px-6 gap-12 max-w-4xl">
      <h2 className="text-2xl font-semibold">Features</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
        <div className="flex flex-col items-center text-center">
          <FaFilter className="w-16 h-16 text-blue-600" />
          <h3 className="mt-4 text-xl font-medium">Data Filtering</h3>
          <p className="mt-2 text-gray-600">
            Easily filter large datasets with advanced filtering options.
          </p>
        </div>
        <div className="flex flex-col items-center text-center">
        <FaLayerGroup className="w-16 h-16 text-blue-600" />
          <h3 className="mt-4 text-xl font-medium">Data Grouping</h3>
          <p className="mt-2 text-gray-600">
            Group your data efficiently for better insights.
          </p>
        </div>
        <div className="flex flex-col items-center text-center">
          <FaChartBar className="w-16 h-16 text-blue-600" />
          <h3 className="mt-4 text-xl font-medium">Data Aggregation</h3>
          <p className="mt-2 text-gray-600">
            Aggregate data to generate meaningful summaries.
          </p>
        </div>
        <div className="flex flex-col items-center text-center">
          <FaClock className="w-16 h-16 text-blue-600" />
          <h3 className="mt-4 text-xl font-medium">Automated Cron Jobs</h3>
          <p className="mt-2 text-gray-600">
            Automate your processes with scheduled cron jobs.
          </p>
        </div>
      </div>
    </main>
  );
}