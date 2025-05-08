import Header from "@/components/Header";
import FeaturesSection from "@/components/FeaturesSection";
import NavBar from "@/components/NavBar";
import CallToAction from "@/components/CallToAction";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-between bg-gray-50 text-gray-800">
      <Header />
      <NavBar />
      <FeaturesSection />
      <CallToAction />
      <Footer />
    </div>
  );
}
