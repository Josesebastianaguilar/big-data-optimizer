import React from "react";

export default function Paginator({ page, totalPages, totalItems, onPageChange, limit, module, activeBackgroundColor = 'bg-blue-600' }) {
  const handleClick = (page_element) => {
    if (page_element !== page && page_element > 0 && page_element <= totalPages) {
      onPageChange(page_element, limit);
    }
  };

  const getPages = () => {
    const pages = [];
    let start = Math.max(1, page - 2);
    let end = Math.min(totalPages, page + 2);
    if (page <= 3) end = Math.min(5, totalPages);
    if (page > totalPages - 2) start = Math.max(1, page - 4);
    for (let i = start; i <= end; i++) pages.push(i);
    return pages;
  };

  return (
    <div>
      {totalPages > 5 && <div className="flex justify-end my-2">
        There are and {totalPages} pages of {module} ({totalItems} items).
      </div>}
      <nav className="flex justify-center my-4">
        {totalPages > 5 && page > 5 && <button
          key={`page_first`}
          className="cursor-pointer px-3 py-1 mx-1 rounded bg-gray-200 hover:bg-gray-300"
          onClick={() => handleClick(1)}
          disabled={page === 1}
        >
          First
        </button>}
        {totalPages > 1 && <button
          className={`px-3 py-1 mx-1 rounded bg-gray-200 ${page !== 1 ? 'cursor-pointer hover:bg-gray-300' : 'text-gray-400'}`}
          onClick={() => handleClick(page - 1)}
          disabled={page === 1}
        >
          Prev
        </button>}        
        {getPages().map((page_number) => (
          <button
            key={`page_${page_number}`}
            className={`px-3 py-1 mx-1 rounded ${page === page_number ? (activeBackgroundColor + " text-white") : "cursor-pointer bg-gray-200 hover:bg-gray-300"}`}
            onClick={() => handleClick(page_number)}
            disabled={page === page_number}
          >
            {page_number}
          </button>
        ))}        
        {totalPages > 1 && <button
          className={`px-3 py-1 mx-1 rounded bg-gray-200 ${page !== totalPages ? 'cursor-pointer hover:bg-gray-300' : 'text-gray-400'}`}
          onClick={() => handleClick(page + 1)}
          disabled={page === totalPages}
        >
          Next
        </button>}
        {totalPages > 5 && page < totalPages - 4 && <button
          key={`page_last`}
          className="cursor-pointer px-3 py-1 mx-1 rounded bg-gray-200 hover:bg-gray-300"
          onClick={() => handleClick(totalPages)}
          disabled={page === totalPages}
        >
          Last
        </button>}
      </nav>
    </div>
  );
}