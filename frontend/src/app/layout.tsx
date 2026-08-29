import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VidyaSearch — Search Engine for Indian College Resources",
  description: "Crawl, index, and search through NPTEL, SWAYAM, IITs, NITs, course notes, and Indian academic materials with BM25 and PageRank.",
  keywords: ["search engine", "NPTEL", "SWAYAM", "IIT", "NIT", "college resources", "BM25", "PageRank", "GATE syllabus", "lecture notes"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
      </head>
      <body>{children}</body>
    </html>
  );
}
