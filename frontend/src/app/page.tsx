"use client";

import React, { useState, useEffect, useRef } from "react";

const API_BASE = "http://localhost:8000/api/v1";

interface SearchResult {
  doc_id: number;
  url: string;
  title: string;
  snippet: string;
  domain: string;
  score: number;
  pagerank_score: number;
  word_count: number;
  crawled_at: string | null;
}

interface SearchResponse {
  query: string;
  total_results: number;
  page: number;
  per_page: number;
  total_pages: number;
  response_time_ms: number;
  ranking_method: string;
  results: SearchResult[];
  did_you_mean: string | null;
  cache_hit: boolean;
}

interface AnalyticsData {
  total_searches: number;
  unique_queries: number;
  avg_response_time_ms: number;
  cache_hit_rate: number;
  zero_result_rate: number;
  top_queries: Array<{
    query: string;
    search_count: number;
    avg_results: number;
    avg_response_time_ms: number;
    last_searched: string;
  }>;
  total_documents: number;
  total_indexed_terms: number;
}

export default function SearchEngineApp() {
  const [query, setQuery] = useState("");
  const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [ranking, setRanking] = useState<"bm25" | "tfidf">("bm25");
  const [domainFilter, setDomainFilter] = useState<string>("");
  const [activeTab, setActiveTab] = useState<"search" | "crawler" | "analytics" | "stats">("search");

  // Autocomplete state
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedSuggestionIdx, setSelectedSuggestionIdx] = useState(-1);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Crawler form state
  const [crawlUrl, setCrawlUrl] = useState("https://nptel.ac.in/courses/");
  const [crawlMaxPages, setCrawlMaxPages] = useState(5);
  const [crawling, setCrawling] = useState(false);
  const [crawlResult, setCrawlResult] = useState<any>(null);

  // Analytics & stats state
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [systemStats, setSystemStats] = useState<any>(null);

  // Fetch Autocomplete Suggestions
  useEffect(() => {
    if (!query.trim() || query.length < 2) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        const res = await fetch(`${API_BASE}/autocomplete?q=${encodeURIComponent(query)}&limit=6`);
        if (res.ok) {
          const data = await res.json();
          setSuggestions(data.suggestions || []);
          setShowSuggestions(data.suggestions?.length > 0);
        }
      } catch (err) {
        // Backend might still be starting
      }
    }, 150);

    return () => clearTimeout(timer);
  }, [query]);

  // Execute Search
  const handleSearch = async (searchQuery?: string, customDomain?: string) => {
    const q = searchQuery !== undefined ? searchQuery : query;
    if (!q.trim()) return;

    setLoading(true);
    setShowSuggestions(false);
    setActiveTab("search");

    const targetDomain = customDomain !== undefined ? customDomain : domainFilter;
    let url = `${API_BASE}/search?q=${encodeURIComponent(q)}&ranking=${ranking}&per_page=15`;
    if (targetDomain) {
      url += `&domain=${encodeURIComponent(targetDomain)}`;
    }

    try {
      const res = await fetch(url);
      if (res.ok) {
        const data: SearchResponse = await res.json();
        setSearchResponse(data);
      }
    } catch (err) {
      console.error("Search failed:", err);
    } finally {
      setLoading(false);
    }
  };

  // Record Result Click
  const handleResultClick = async (docId: number, position: number, clickedUrl: string) => {
    try {
      await fetch(`${API_BASE}/analytics/click`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query_id: 1,
          doc_id: docId,
          result_position: position,
          clicked_url: clickedUrl,
        }),
      });
    } catch (e) {
      // Non-critical
    }
  };

  // Handle Autocomplete Keyboard Navigation
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!showSuggestions || suggestions.length === 0) {
      if (e.key === "Enter") handleSearch();
      return;
    }

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedSuggestionIdx((prev) => (prev < suggestions.length - 1 ? prev + 1 : 0));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedSuggestionIdx((prev) => (prev > 0 ? prev - 1 : suggestions.length - 1));
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (selectedSuggestionIdx >= 0 && selectedSuggestionIdx < suggestions.length) {
        const selected = suggestions[selectedSuggestionIdx];
        setQuery(selected);
        handleSearch(selected);
      } else {
        handleSearch();
      }
    } else if (e.key === "Escape") {
      setShowSuggestions(false);
    }
  };

  // Fetch Analytics & Stats
  const loadAnalytics = async () => {
    try {
      const res = await fetch(`${API_BASE}/analytics`);
      if (res.ok) setAnalytics(await res.json());
    } catch (e) {}
  };

  const loadStats = async () => {
    try {
      const res = await fetch(`${API_BASE}/stats`);
      if (res.ok) setSystemStats(await res.json());
    } catch (e) {}
  };

  useEffect(() => {
    if (activeTab === "analytics") loadAnalytics();
    if (activeTab === "stats") loadStats();
  }, [activeTab]);

  // Trigger Live Crawl
  const triggerCrawl = async () => {
    if (!crawlUrl) return;
    setCrawling(true);
    setCrawlResult(null);
    try {
      const res = await fetch(`${API_BASE}/crawl?seed_urls=${encodeURIComponent(crawlUrl)}&max_pages=${crawlMaxPages}`, {
        method: "POST",
      });
      if (res.ok) {
        const data = await res.json();
        setCrawlResult(data);
      }
    } catch (e) {
      setCrawlResult({ error: "Crawl request failed" });
    } finally {
      setCrawling(false);
    }
  };

  // Quick Preset Queries
  const trendingQueries = [
    "Machine Learning IIT Madras",
    "Data Structures NPTEL",
    "Operating Systems COL331",
    "Deep Learning PyTorch",
    "GATE Computer Science PYQ",
    "Python Programming SWAYAM",
    "Database Management Systems",
  ];

  const hasSearched = searchResponse !== null;

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      {/* Navigation Top Bar */}
      <header
        style={{
          borderBottom: "1px solid var(--border-color)",
          background: "rgba(9, 12, 21, 0.8)",
          backdropFilter: "blur(12px)",
          position: "sticky",
          top: 0,
          zIndex: 40,
          padding: "0.85rem 1.5rem",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "0.85rem", cursor: "pointer" }} onClick={() => setSearchResponse(null)}>
          <div
            style={{
              width: "36px",
              height: "36px",
              borderRadius: "10px",
              background: "linear-gradient(135deg, #f59e0b 0%, #6366f1 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 0 20px rgba(99, 102, 241, 0.4)",
              fontWeight: 800,
              fontSize: "1.1rem",
              color: "#fff",
            }}
          >
            V
          </div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
              <span style={{ fontWeight: 800, fontSize: "1.25rem", letterSpacing: "-0.02em" }}>
                Vidya<span style={{ color: "var(--accent-saffron)" }}>Search</span>
              </span>
              <span
                style={{
                  fontSize: "0.65rem",
                  padding: "0.15rem 0.45rem",
                  borderRadius: "999px",
                  background: "rgba(245, 158, 11, 0.15)",
                  color: "var(--accent-saffron-light)",
                  fontWeight: 700,
                  border: "1px solid rgba(245, 158, 11, 0.3)",
                }}
              >
                विद्या • IR
              </span>
            </div>
          </div>
        </div>

        {/* Tab Switcher */}
        <div style={{ display: "flex", gap: "0.5rem", background: "rgba(255,255,255,0.04)", padding: "0.25rem", borderRadius: "10px", border: "1px solid var(--border-color)" }}>
          <button
            onClick={() => setActiveTab("search")}
            style={{
              padding: "0.45rem 0.9rem",
              borderRadius: "8px",
              border: "none",
              background: activeTab === "search" ? "var(--accent-indigo)" : "transparent",
              color: activeTab === "search" ? "#fff" : "var(--text-secondary)",
              fontWeight: 600,
              fontSize: "0.85rem",
              cursor: "pointer",
              transition: "all 0.2s",
            }}
          >
            🔍 Search
          </button>
          <button
            onClick={() => setActiveTab("crawler")}
            style={{
              padding: "0.45rem 0.9rem",
              borderRadius: "8px",
              border: "none",
              background: activeTab === "crawler" ? "var(--accent-indigo)" : "transparent",
              color: activeTab === "crawler" ? "#fff" : "var(--text-secondary)",
              fontWeight: 600,
              fontSize: "0.85rem",
              cursor: "pointer",
              transition: "all 0.2s",
            }}
          >
            🕷️ Web Crawler
          </button>
          <button
            onClick={() => setActiveTab("analytics")}
            style={{
              padding: "0.45rem 0.9rem",
              borderRadius: "8px",
              border: "none",
              background: activeTab === "analytics" ? "var(--accent-indigo)" : "transparent",
              color: activeTab === "analytics" ? "#fff" : "var(--text-secondary)",
              fontWeight: 600,
              fontSize: "0.85rem",
              cursor: "pointer",
              transition: "all 0.2s",
            }}
          >
            📊 Analytics
          </button>
          <button
            onClick={() => setActiveTab("stats")}
            style={{
              padding: "0.45rem 0.9rem",
              borderRadius: "8px",
              border: "none",
              background: activeTab === "stats" ? "var(--accent-indigo)" : "transparent",
              color: activeTab === "stats" ? "#fff" : "var(--text-secondary)",
              fontWeight: 600,
              fontSize: "0.85rem",
              cursor: "pointer",
              transition: "all 0.2s",
            }}
          >
            ⚙️ Index Stats
          </button>
        </div>
      </header>

      {/* Main Container */}
      <main style={{ flex: 1, padding: "2rem 1.5rem", maxWidth: "1100px", margin: "0 auto", width: "100%" }}>
        {/* SEARCH TAB */}
        {activeTab === "search" && (
          <div>
            {/* Hero / Header Section */}
            {!hasSearched ? (
              <div style={{ textAlign: "center", margin: "3.5rem 0 2.5rem" }} className="animate-fade-in">
                <h1
                  style={{
                    fontSize: "3.2rem",
                    fontWeight: 800,
                    letterSpacing: "-0.03em",
                    marginBottom: "0.75rem",
                    background: "linear-gradient(135deg, #ffffff 30%, #94a3b8 100%)",
                    WebkitBackgroundClip: "text",
                    WebkitTextFillColor: "transparent",
                  }}
                >
                  Search Indian College Resources
                </h1>
                <p style={{ color: "var(--text-secondary)", fontSize: "1.15rem", maxWidth: "680px", margin: "0 auto" }}>
                  Fast information retrieval across <strong style={{ color: "#f8fafc" }}>NPTEL</strong> courses, <strong style={{ color: "#f8fafc" }}>SWAYAM</strong>, <strong style={{ color: "#f8fafc" }}>IITs & NITs</strong> notes with BM25 ranking and PageRank.
                </p>
              </div>
            ) : null}

            {/* Search Input Box with Autocomplete */}
            <div style={{ position: "relative", maxWidth: hasSearched ? "850px" : "750px", margin: "0 auto 1.5rem" }}>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  background: "var(--bg-secondary)",
                  border: "1px solid rgba(255, 255, 255, 0.12)",
                  borderRadius: "14px",
                  padding: "0.4rem 0.6rem 0.4rem 1.2rem",
                  boxShadow: "0 8px 32px rgba(0, 0, 0, 0.35)",
                  transition: "all 0.2s ease",
                }}
              >
                <span style={{ fontSize: "1.2rem", marginRight: "0.75rem", color: "var(--text-muted)" }}>🔍</span>
                <input
                  ref={searchInputRef}
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={handleKeyDown}
                  onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
                  placeholder='Search topics e.g. "Data Structures", "Machine Learning", "Operating Systems"...'
                  style={{
                    flex: 1,
                    background: "transparent",
                    border: "none",
                    outline: "none",
                    color: "var(--text-primary)",
                    fontSize: "1.05rem",
                    fontWeight: 500,
                  }}
                />
                {query && (
                  <button
                    onClick={() => {
                      setQuery("");
                      setSuggestions([]);
                    }}
                    style={{
                      background: "transparent",
                      border: "none",
                      color: "var(--text-muted)",
                      cursor: "pointer",
                      fontSize: "1.2rem",
                      padding: "0.2rem 0.5rem",
                    }}
                  >
                    ✕
                  </button>
                )}
                <button
                  onClick={() => handleSearch()}
                  disabled={loading}
                  style={{
                    background: "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",
                    color: "#fff",
                    border: "none",
                    borderRadius: "10px",
                    padding: "0.65rem 1.4rem",
                    fontWeight: 700,
                    fontSize: "0.95rem",
                    cursor: "pointer",
                    boxShadow: "0 2px 10px rgba(245, 158, 11, 0.3)",
                    transition: "all 0.2s",
                  }}
                >
                  {loading ? "Searching..." : "Search"}
                </button>
              </div>

              {/* Autocomplete Suggestions Dropdown */}
              {showSuggestions && suggestions.length > 0 && (
                <div
                  style={{
                    position: "absolute",
                    top: "105%",
                    left: 0,
                    right: 0,
                    background: "var(--bg-secondary)",
                    border: "1px solid rgba(255, 255, 255, 0.12)",
                    borderRadius: "12px",
                    overflow: "hidden",
                    zIndex: 50,
                    boxShadow: "0 12px 36px rgba(0, 0, 0, 0.5)",
                  }}
                >
                  {suggestions.map((suggestion, idx) => (
                    <div
                      key={idx}
                      onClick={() => {
                        setQuery(suggestion);
                        setShowSuggestions(false);
                        handleSearch(suggestion);
                      }}
                      onMouseEnter={() => setSelectedSuggestionIdx(idx)}
                      style={{
                        padding: "0.75rem 1.25rem",
                        cursor: "pointer",
                        background: idx === selectedSuggestionIdx ? "rgba(99, 102, 241, 0.2)" : "transparent",
                        borderBottom: idx < suggestions.length - 1 ? "1px solid rgba(255, 255, 255, 0.04)" : "none",
                        display: "flex",
                        alignItems: "center",
                        gap: "0.75rem",
                        fontSize: "0.95rem",
                        color: idx === selectedSuggestionIdx ? "#fff" : "var(--text-secondary)",
                      }}
                    >
                      <span style={{ color: "var(--accent-saffron)", fontSize: "0.85rem" }}>⚡</span>
                      <span>{suggestion}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Filter and Algorithm Options Bar */}
            <div
              style={{
                maxWidth: hasSearched ? "850px" : "750px",
                margin: "0 auto 2rem",
                display: "flex",
                flexWrap: "wrap",
                alignItems: "center",
                justifyContent: "space-between",
                gap: "0.75rem",
                fontSize: "0.85rem",
              }}
            >
              {/* Domain Filter Pills */}
              <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap" }}>
                {[
                  { label: "All Sources", domain: "" },
                  { label: "NPTEL", domain: "nptel.ac.in" },
                  { label: "SWAYAM", domain: "swayam.gov.in" },
                  { label: "IITs", domain: "iit" },
                  { label: "GATE", domain: "gate" },
                ].map((item) => (
                  <button
                    key={item.label}
                    onClick={() => {
                      setDomainFilter(item.domain);
                      if (hasSearched) handleSearch(query, item.domain);
                    }}
                    style={{
                      padding: "0.35rem 0.75rem",
                      borderRadius: "999px",
                      border: domainFilter === item.domain ? "1px solid var(--accent-saffron)" : "1px solid var(--border-color)",
                      background: domainFilter === item.domain ? "rgba(245, 158, 11, 0.15)" : "rgba(255, 255, 255, 0.03)",
                      color: domainFilter === item.domain ? "var(--accent-saffron-light)" : "var(--text-secondary)",
                      fontWeight: 600,
                      cursor: "pointer",
                      fontSize: "0.8rem",
                    }}
                  >
                    {item.label}
                  </button>
                ))}
              </div>

              {/* Ranking Algorithm Selector */}
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <span style={{ color: "var(--text-muted)" }}>Ranking:</span>
                <button
                  onClick={() => {
                    setRanking("bm25");
                    if (hasSearched) handleSearch();
                  }}
                  style={{
                    padding: "0.3rem 0.65rem",
                    borderRadius: "6px",
                    border: ranking === "bm25" ? "1px solid var(--accent-indigo)" : "1px solid var(--border-color)",
                    background: ranking === "bm25" ? "rgba(99, 102, 241, 0.25)" : "transparent",
                    color: ranking === "bm25" ? "#fff" : "var(--text-muted)",
                    fontWeight: 600,
                    cursor: "pointer",
                    fontSize: "0.78rem",
                  }}
                >
                  BM25 + PageRank
                </button>
                <button
                  onClick={() => {
                    setRanking("tfidf");
                    if (hasSearched) handleSearch();
                  }}
                  style={{
                    padding: "0.3rem 0.65rem",
                    borderRadius: "6px",
                    border: ranking === "tfidf" ? "1px solid var(--accent-indigo)" : "1px solid var(--border-color)",
                    background: ranking === "tfidf" ? "rgba(99, 102, 241, 0.25)" : "transparent",
                    color: ranking === "tfidf" ? "#fff" : "var(--text-muted)",
                    fontWeight: 600,
                    cursor: "pointer",
                    fontSize: "0.78rem",
                  }}
                >
                  TF-IDF
                </button>
              </div>
            </div>

            {/* Trending Quick Search Tags (When idle) */}
            {!hasSearched && (
              <div style={{ maxWidth: "750px", margin: "0 auto", textAlign: "center" }} className="animate-fade-in">
                <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: "0.75rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  Popular Indian College Searches
                </p>
                <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: "0.5rem" }}>
                  {trendingQueries.map((tq) => (
                    <span
                      key={tq}
                      onClick={() => {
                        setQuery(tq);
                        handleSearch(tq);
                      }}
                      style={{
                        padding: "0.4rem 0.85rem",
                        borderRadius: "999px",
                        background: "rgba(255, 255, 255, 0.04)",
                        border: "1px solid var(--border-color)",
                        color: "var(--text-secondary)",
                        fontSize: "0.85rem",
                        cursor: "pointer",
                        transition: "all 0.2s",
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.borderColor = "var(--accent-saffron)";
                        e.currentTarget.style.color = "#fff";
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.borderColor = "var(--border-color)";
                        e.currentTarget.style.color = "var(--text-secondary)";
                      }}
                    >
                      {tq}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Search Results Display */}
            {hasSearched && (
              <div style={{ maxWidth: "850px", margin: "0 auto" }} className="animate-fade-in">
                {/* Meta stats bar */}
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    paddingBottom: "1rem",
                    borderBottom: "1px solid var(--border-color)",
                    marginBottom: "1.25rem",
                    fontSize: "0.85rem",
                    color: "var(--text-muted)",
                  }}
                >
                  <div>
                    Found <strong style={{ color: "var(--text-primary)" }}>{searchResponse.total_results}</strong> results in{" "}
                    <strong style={{ color: "var(--accent-cyan)" }}>{searchResponse.response_time_ms} ms</strong>
                  </div>
                  <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
                    <span style={{ padding: "0.15rem 0.5rem", borderRadius: "4px", background: "rgba(255, 255, 255, 0.06)", fontSize: "0.75rem" }}>
                      Model: {searchResponse.ranking_method.toUpperCase()}
                    </span>
                    {searchResponse.cache_hit && (
                      <span style={{ padding: "0.15rem 0.5rem", borderRadius: "4px", background: "rgba(16, 185, 129, 0.15)", color: "var(--accent-emerald)", fontSize: "0.75rem", fontWeight: 700 }}>
                        ⚡ CACHE HIT
                      </span>
                    )}
                  </div>
                </div>

                {/* Did You Mean Typo Suggestion */}
                {searchResponse.did_you_mean && (
                  <div
                    style={{
                      background: "rgba(245, 158, 11, 0.1)",
                      border: "1px solid rgba(245, 158, 11, 0.3)",
                      borderRadius: "10px",
                      padding: "0.75rem 1.25rem",
                      marginBottom: "1.5rem",
                      fontSize: "0.95rem",
                    }}
                  >
                    Did you mean:{" "}
                    <strong
                      onClick={() => {
                        setQuery(searchResponse.did_you_mean!);
                        handleSearch(searchResponse.did_you_mean!);
                      }}
                      style={{ color: "var(--accent-saffron-light)", cursor: "pointer", textDecoration: "underline" }}
                    >
                      {searchResponse.did_you_mean}
                    </strong>
                    ?
                  </div>
                )}

                {/* Zero Results State */}
                {searchResponse.results.length === 0 && (
                  <div style={{ textAlign: "center", padding: "3rem 1rem", color: "var(--text-muted)" }}>
                    <div style={{ fontSize: "2.5rem", marginBottom: "0.5rem" }}>🔍</div>
                    <h3 style={{ color: "var(--text-primary)", marginBottom: "0.5rem" }}>No results found</h3>
                    <p>Try searching for keywords like "NPTEL", "Machine Learning", "Data Structures", or "Operating Systems".</p>
                  </div>
                )}

                {/* Results List */}
                <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
                  {searchResponse.results.map((result, idx) => (
                    <article
                      key={result.doc_id}
                      className="glass-panel"
                      style={{
                        padding: "1.25rem 1.5rem",
                        transition: "transform 0.15s ease, border-color 0.15s ease",
                      }}
                    >
                      {/* URL and Domain Header */}
                      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.4rem" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.8rem", color: "var(--text-muted)" }}>
                          <span
                            style={{
                              padding: "0.15rem 0.5rem",
                              borderRadius: "4px",
                              background: "rgba(99, 102, 241, 0.15)",
                              color: "#a5b4fc",
                              fontWeight: 700,
                            }}
                          >
                            {result.domain}
                          </span>
                          <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: "450px" }}>
                            {result.url}
                          </span>
                        </div>
                        {/* Score badges */}
                        <div style={{ display: "flex", gap: "0.4rem" }}>
                          <span style={{ fontSize: "0.75rem", padding: "0.15rem 0.45rem", borderRadius: "4px", background: "rgba(255,255,255,0.05)", color: "var(--text-secondary)" }} title="BM25 Relevance Score">
                            Score: {result.score}
                          </span>
                          <span style={{ fontSize: "0.75rem", padding: "0.15rem 0.45rem", borderRadius: "4px", background: "rgba(245, 158, 11, 0.15)", color: "var(--accent-saffron-light)" }} title="PageRank Score">
                            PR: {result.pagerank_score}
                          </span>
                        </div>
                      </div>

                      {/* Title */}
                      <h2 style={{ fontSize: "1.2rem", fontWeight: 700, marginBottom: "0.5rem" }}>
                        <a
                          href={result.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          onClick={() => handleResultClick(result.doc_id, idx + 1, result.url)}
                          style={{ color: "#38bdf8", textDecoration: "none" }}
                          onMouseEnter={(e) => (e.currentTarget.style.textDecoration = "underline")}
                          onMouseLeave={(e) => (e.currentTarget.style.textDecoration = "none")}
                        >
                          {result.title}
                        </a>
                      </h2>

                      {/* Snippet with <mark> highlighting */}
                      <p
                        style={{ color: "var(--text-secondary)", fontSize: "0.95rem", lineHeight: "1.6" }}
                        dangerouslySetInnerHTML={{ __html: result.snippet }}
                      />

                      {/* Footer metadata */}
                      <div style={{ marginTop: "0.75rem", display: "flex", gap: "1rem", fontSize: "0.75rem", color: "var(--text-muted)" }}>
                        <span>Words: {result.word_count}</span>
                        {result.crawled_at && <span>Indexed: {new Date(result.crawled_at).toLocaleDateString()}</span>}
                      </div>
                    </article>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* WEB CRAWLER TAB */}
        {activeTab === "crawler" && (
          <div style={{ maxWidth: "800px", margin: "0 auto" }} className="animate-fade-in">
            <h2 style={{ fontSize: "1.8rem", fontWeight: 800, marginBottom: "0.5rem" }}>Live Web Crawler Engine</h2>
            <p style={{ color: "var(--text-secondary)", marginBottom: "2rem" }}>
              Crawl college portals, parse HTML, extract hyperlink graphs for PageRank, and dynamically update the inverted index.
            </p>

            <div className="glass-panel" style={{ padding: "1.75rem", marginBottom: "2rem" }}>
              <div style={{ marginBottom: "1.25rem" }}>
                <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "0.4rem" }}>
                  Seed URL
                </label>
                <input
                  type="text"
                  value={crawlUrl}
                  onChange={(e) => setCrawlUrl(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "0.75rem 1rem",
                    borderRadius: "8px",
                    background: "var(--bg-primary)",
                    border: "1px solid var(--border-color)",
                    color: "#fff",
                    fontSize: "0.95rem",
                  }}
                />
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1.5rem" }}>
                <div>
                  <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "0.4rem" }}>
                    Max Pages to Crawl
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="20"
                    value={crawlMaxPages}
                    onChange={(e) => setCrawlMaxPages(parseInt(e.target.value) || 5)}
                    style={{
                      width: "100%",
                      padding: "0.75rem 1rem",
                      borderRadius: "8px",
                      background: "var(--bg-primary)",
                      border: "1px solid var(--border-color)",
                      color: "#fff",
                    }}
                  />
                </div>
                <div>
                  <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "0.4rem" }}>
                    Robots.txt & Politeness
                  </label>
                  <div style={{ padding: "0.75rem 1rem", borderRadius: "8px", background: "rgba(16, 185, 129, 0.1)", color: "var(--accent-emerald)", fontSize: "0.85rem", fontWeight: 600 }}>
                    ✓ 1 req/sec Rate Limit Active
                  </div>
                </div>
              </div>

              <button
                onClick={triggerCrawl}
                disabled={crawling}
                style={{
                  width: "100%",
                  padding: "0.85rem",
                  borderRadius: "10px",
                  background: "linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)",
                  color: "#fff",
                  fontWeight: 700,
                  fontSize: "1rem",
                  border: "none",
                  cursor: "pointer",
                }}
              >
                {crawling ? "Crawling in Progress (Async Fetcher & Indexer)..." : "Start Live Crawl"}
              </button>
            </div>

            {crawlResult && (
              <div className="glass-panel" style={{ padding: "1.5rem" }}>
                <h3 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "0.75rem", color: "var(--accent-emerald)" }}>
                  ✓ Crawl & Index Completed
                </h3>
                <pre style={{ background: "rgba(0,0,0,0.3)", padding: "1rem", borderRadius: "8px", fontFamily: "var(--font-mono)", fontSize: "0.85rem" }}>
                  {JSON.stringify(crawlResult, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}

        {/* ANALYTICS TAB */}
        {activeTab === "analytics" && (
          <div style={{ maxWidth: "900px", margin: "0 auto" }} className="animate-fade-in">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
              <div>
                <h2 style={{ fontSize: "1.8rem", fontWeight: 800, marginBottom: "0.3rem" }}>Search Engine Analytics</h2>
                <p style={{ color: "var(--text-secondary)" }}>Query metrics, response latency, and usage distribution</p>
              </div>
              <button
                onClick={loadAnalytics}
                style={{ padding: "0.45rem 0.9rem", borderRadius: "8px", background: "rgba(255,255,255,0.06)", border: "1px solid var(--border-color)", color: "#fff", cursor: "pointer" }}
              >
                ↻ Refresh
              </button>
            </div>

            {analytics ? (
              <div>
                {/* Stats Grid */}
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "1rem", marginBottom: "2rem" }}>
                  <div className="glass-panel" style={{ padding: "1.25rem" }}>
                    <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "0.25rem" }}>Total Searches</div>
                    <div style={{ fontSize: "1.8rem", fontWeight: 800, color: "var(--accent-cyan)" }}>{analytics.total_searches}</div>
                  </div>
                  <div className="glass-panel" style={{ padding: "1.25rem" }}>
                    <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "0.25rem" }}>Unique Queries</div>
                    <div style={{ fontSize: "1.8rem", fontWeight: 800, color: "var(--accent-saffron)" }}>{analytics.unique_queries}</div>
                  </div>
                  <div className="glass-panel" style={{ padding: "1.25rem" }}>
                    <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "0.25rem" }}>Avg Latency</div>
                    <div style={{ fontSize: "1.8rem", fontWeight: 800, color: "var(--accent-emerald)" }}>{analytics.avg_response_time_ms} ms</div>
                  </div>
                  <div className="glass-panel" style={{ padding: "1.25rem" }}>
                    <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "0.25rem" }}>Cache Hit Rate</div>
                    <div style={{ fontSize: "1.8rem", fontWeight: 800, color: "#a5b4fc" }}>{analytics.cache_hit_rate}%</div>
                  </div>
                </div>

                {/* Popular Queries Table */}
                <div className="glass-panel" style={{ padding: "1.5rem" }}>
                  <h3 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "1rem" }}>Top Searched Queries</h3>
                  <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.9rem" }}>
                    <thead>
                      <tr style={{ borderBottom: "1px solid var(--border-color)", textAlign: "left", color: "var(--text-muted)" }}>
                        <th style={{ padding: "0.75rem 0.5rem" }}>Query</th>
                        <th style={{ padding: "0.75rem 0.5rem" }}>Searches</th>
                        <th style={{ padding: "0.75rem 0.5rem" }}>Avg Results</th>
                        <th style={{ padding: "0.75rem 0.5rem" }}>Avg Time</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analytics.top_queries.map((q, idx) => (
                        <tr key={idx} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                          <td style={{ padding: "0.75rem 0.5rem", fontWeight: 600, color: "#fff" }}>{q.query}</td>
                          <td style={{ padding: "0.75rem 0.5rem", color: "var(--accent-saffron-light)" }}>{q.search_count}</td>
                          <td style={{ padding: "0.75rem 0.5rem", color: "var(--text-secondary)" }}>{q.avg_results}</td>
                          <td style={{ padding: "0.75rem 0.5rem", color: "var(--accent-cyan)" }}>{q.avg_response_time_ms} ms</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div style={{ textAlign: "center", padding: "2rem", color: "var(--text-muted)" }}>Loading analytics...</div>
            )}
          </div>
        )}

        {/* INDEX STATS TAB */}
        {activeTab === "stats" && (
          <div style={{ maxWidth: "800px", margin: "0 auto" }} className="animate-fade-in">
            <h2 style={{ fontSize: "1.8rem", fontWeight: 800, marginBottom: "0.5rem" }}>Inverted Index & Engine Statistics</h2>
            <p style={{ color: "var(--text-secondary)", marginBottom: "2rem" }}>Internal data structure statistics, posting lists, and link graph density</p>

            {systemStats ? (
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.25rem" }}>
                <div className="glass-panel" style={{ padding: "1.5rem" }}>
                  <div style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: "0.25rem" }}>Indexed Documents</div>
                  <div style={{ fontSize: "2.2rem", fontWeight: 800, color: "#fff" }}>{systemStats.total_documents}</div>
                </div>
                <div className="glass-panel" style={{ padding: "1.5rem" }}>
                  <div style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: "0.25rem" }}>Unique Indexed Terms</div>
                  <div style={{ fontSize: "2.2rem", fontWeight: 800, color: "var(--accent-saffron)" }}>{systemStats.total_indexed_terms}</div>
                </div>
                <div className="glass-panel" style={{ padding: "1.5rem" }}>
                  <div style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: "0.25rem" }}>Link Graph Edges (PageRank)</div>
                  <div style={{ fontSize: "2.2rem", fontWeight: 800, color: "#a5b4fc" }}>{systemStats.total_link_edges}</div>
                </div>
                <div className="glass-panel" style={{ padding: "1.5rem" }}>
                  <div style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: "0.25rem" }}>In-Memory Cache Size</div>
                  <div style={{ fontSize: "2.2rem", fontWeight: 800, color: "var(--accent-emerald)" }}>{systemStats.cache?.size || 0} / 1000</div>
                </div>
              </div>
            ) : (
              <div style={{ textAlign: "center", padding: "2rem", color: "var(--text-muted)" }}>Loading stats...</div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer style={{ borderTop: "1px solid var(--border-color)", padding: "1.5rem", textAlign: "center", fontSize: "0.85rem", color: "var(--text-muted)" }}>
        VidyaSearch • Information Retrieval System for Indian Higher Education • BM25 + PageRank + Prefix Trie
      </footer>
    </div>
  );
}
