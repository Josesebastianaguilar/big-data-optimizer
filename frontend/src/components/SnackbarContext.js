"use client";

import React, { createContext, useContext, useState, useCallback } from "react";

const SnackbarContext = createContext();

const DEFAULT_DURATION = parseInt(process.env.NEXT_PUBLIC_SNACKBAR_DURATION || "5000", 10);

export function useSnackbar() {
  return useContext(SnackbarContext);
}

function getPositionClasses(position) {
  switch (position) {
    case "top-left":
      return "top-6 left-6";
    case "top-right":
      return "top-6 right-6";
    case "top-center":
      return "top-6 left-1/2 transform -translate-x-1/2";
    case "bottom-left":
      return "bottom-6 left-6";
    case "bottom-right":
      return "bottom-6 right-6";
    case "bottom-center":
    default:
      return "bottom-6 left-1/2 transform -translate-x-1/2";
  }
}

export function SnackbarProvider({ children }) {
  const [snackbars, setSnackbars] = useState([]);

  const closeSnackbar = useCallback((id) => {
    setSnackbars((prev) => prev.filter((snack) => snack.id !== id));
  }, []);

  const showSnackbar = useCallback(
    (
      message,
      type = "info",
      auto_close = true,
      position = "bottom-center"
    ) => {
      const id = Date.now() + Math.random();
      setSnackbars((prev) => [
        ...prev,
        { id, message, type, auto_close, position },
      ]);
      if (auto_close) {
        setTimeout(() => closeSnackbar(id), DEFAULT_DURATION);
      }
    },
    [closeSnackbar]
  );

  return (
    <SnackbarContext.Provider value={{ showSnackbar, closeSnackbar }}>
      {children}
      {/* Render snackbars grouped by position */}
      {["top-left", "top-center", "top-right", "bottom-left", "bottom-center", "bottom-right"].map(
        (position) => {
          const snacks = snackbars.filter((snack) => snack.position === position);
          if (!snacks.length) return null;
          return (
            <div
              key={position}
              className={`fixed z-50 space-y-2 ${getPositionClasses(position)}`}
              style={{ minWidth: 250, maxWidth: 400 }}
            >
              {snacks.map((snackbar) => (
                <div
                  key={snackbar.id}
                  className={`px-6 py-3 rounded shadow-lg text-white flex items-center transition-all
                    ${snackbar.closing
                      ? "opacity-0 translate-y-4 pointer-events-none"
                      : "opacity-100 translate-y-0"
                    }
                    ${snackbar.type === "error"
                      ? "bg-red-600"
                      : snackbar.type === "success"
                      ? "bg-green-600"
                      : snackbar.type === "warning"
                      ? "bg-gray-500"
                      : "bg-blue-600"
                    }`}
                    style={{ willChange: "opacity, transform" }}
                >
                  <span className="flex-1">{snackbar.message}</span>
                  {!snackbar.auto_close && (
                    <button
                      onClick={() => closeSnackbar(snackbar.id)}
                      className="cursor-pointer ml-4 text-white hover:text-gray-200 focus:outline-none"
                      aria-label="Close"
                    >
                      &times;
                    </button>
                  )}
                </div>
              ))}
            </div>
          );
        }
      )}
    </SnackbarContext.Provider>
  );
}