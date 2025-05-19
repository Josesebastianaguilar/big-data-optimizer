"use client";

import Header from "@/components/Header";
import FeaturesSection from "@/components/FeaturesSection";
import CallToAction from "@/components/CallToAction";
import Footer from "@/components/Footer";
import { useAuth } from "@/context/AuthContext";

export default function Home() {
  const { token } = useAuth();
  return (
    <div className="min-h-screen flex flex-col items-center justify-between bg-gray-50 text-gray-800">
      <Header />
      <FeaturesSection />
      {!token && <CallToAction />}
      <Footer />
    </div>
  );
}
