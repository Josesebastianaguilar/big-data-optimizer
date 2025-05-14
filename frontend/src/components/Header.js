import NavBar from "@/components/NavBar";

export default function Header({ backgroundColor }) {
  return (
    <header className={"w-full text-white py-4 text-center " + (backgroundColor || "bg-blue-600")}>
      <h1 className="text-4xl font-bold">Welcome to Big Data Optimizer</h1>
      <p className="mt-4 text-lg">
        Optimize and manage your big data processes with ease.
      </p>
      <NavBar />
    </header>
  );
}