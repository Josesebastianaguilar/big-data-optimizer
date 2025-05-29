import { Geist, Geist_Mono } from "next/font/google";
import { AuthProvider } from "@/context/AuthContext";
import { FaSpinner }  from "react-icons/fa";
import { Suspense } from "react";
import { SnackbarProvider } from "@/components/SnackbarContext";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "Big Data Optimizer",
  description: "App to manage optimization processes in Big Data",
  icons: {
    icon: "/favicon.ico"
  }
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <Suspense fallback={<FaSpinner className="text-center animate-spin inline mr-2 h-8 w-8" />}>
          <SnackbarProvider>
            <AuthProvider>
              {children}
            </AuthProvider>
          </SnackbarProvider>
        </Suspense>
      </body>
    </html>
  );
}
