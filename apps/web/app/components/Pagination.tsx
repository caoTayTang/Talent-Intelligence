"use client";

import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from "lucide-react";

interface PaginationProps {
  currentPage: number; // 0-indexed
  totalItems: number;
  pageSize: number;
  onPageChange: (page: number) => void;
}

export function Pagination({ currentPage, totalItems, pageSize, onPageChange }: PaginationProps) {
  const totalPages = Math.ceil(totalItems / pageSize);
  if (totalPages <= 1) return null;

  // The user wants blocks of 5: << < 1 2 3 4 5 > >>
  // startPage is the first number in the current block of 5
  const blockIndex = Math.floor(currentPage / 5);
  const startPage = blockIndex * 5; 
  const endPage = Math.min(startPage + 5, totalPages);

  const pages = [];
  for (let i = startPage; i < endPage; i++) {
    pages.push(i);
  }

  return (
    <div className="mt-8 flex items-center justify-center gap-2">
      {/* << Jump to first block / first 5 digits */}
      <button
        onClick={() => onPageChange(0)}
        disabled={currentPage < 5}
        className="flex h-9 w-9 items-center justify-center rounded-lg border border-black/5 bg-white text-[#607063] transition-colors hover:bg-[#f3f5f0] disabled:opacity-30"
        title="First 5 pages"
      >
        <ChevronsLeft size={16} />
      </button>

      {/* < Move backwards 5 digits */}
      <button
        onClick={() => onPageChange(Math.max(0, startPage - 5))}
        disabled={startPage === 0}
        className="flex h-9 w-9 items-center justify-center rounded-lg border border-black/5 bg-white text-[#607063] transition-colors hover:bg-[#f3f5f0] disabled:opacity-30"
        title="Previous 5 pages"
      >
        <ChevronLeft size={16} />
      </button>

      {/* Numeric Pages 1 2 3 4 5 */}
      <div className="flex items-center gap-1 mx-2">
        {pages.map((p) => (
          <button
            key={p}
            onClick={() => onPageChange(p)}
            className={`flex h-9 w-9 items-center justify-center rounded-lg border text-sm font-bold transition-all ${
              currentPage === p
                ? "border-[#e0563f] bg-[#fdf6f4] text-[#e0563f]"
                : "border-black/5 bg-white text-[#607063] hover:bg-[#f3f5f0]"
            }`}
          >
            {p + 1}
          </button>
        ))}
      </div>

      {/* > Move towards 5 digits */}
      <button
        onClick={() => onPageChange(Math.min(totalPages - 1, startPage + 5))}
        disabled={startPage + 5 >= totalPages}
        className="flex h-9 w-9 items-center justify-center rounded-lg border border-black/5 bg-white text-[#607063] transition-colors hover:bg-[#f3f5f0] disabled:opacity-30"
        title="Next 5 pages"
      >
        <ChevronRight size={16} />
      </button>

      {/* >> Jump to last block / last 5 digits */}
      <button
        onClick={() => onPageChange(Math.floor((totalPages - 1) / 5) * 5)}
        disabled={startPage + 5 >= totalPages}
        className="flex h-9 w-9 items-center justify-center rounded-lg border border-black/5 bg-white text-[#607063] transition-colors hover:bg-[#f3f5f0] disabled:opacity-30"
        title="Last 5 pages"
      >
        <ChevronsRight size={16} />
      </button>
    </div>
  );
}
