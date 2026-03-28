'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Search,
  Database,
  ExternalLink,
  RefreshCw,
  Loader2,
  GitBranch,
  Tag,
  Table2,
  BarChart3,
  Globe,
  BookOpen,
  Filter,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import Link from 'next/link';
import { getBackendUrl } from "@/lib/api-client";

const API_BASE = getBackendUrl();

interface DatasetResult {
  entity: string;
  urn: string;
  aspects?: Record<string, any>;
  matchedFields?: { name: string; value: string }[];
}

interface CatalogStats {
  datasets: number;
  dashboards: number;
  pipelines: number;
}

async function searchCatalog(query: string, start = 0, count = 20) {
  const res = await fetch(
    `${API_BASE}/api/v1/catalog/search?q=${encodeURIComponent(query)}&start=${start}&count=${count}`
  );
  return res.json();
}

async function fetchStats(): Promise<CatalogStats> {
  const res = await fetch(`${API_BASE}/api/v1/catalog/stats`);
  if (!res.ok) return { datasets: 0, dashboards: 0, pipelines: 0 };
  return res.json();
}

async function fetchDomains() {
  const res = await fetch(`${API_BASE}/api/v1/catalog/domains`);
  return res.json();
}

function StatusBadge({ connected }: { connected: boolean }) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium',
        connected
          ? 'bg-emerald-500/10 text-emerald-400'
          : 'bg-zinc-500/10 text-zinc-400'
      )}
    >
      <span
        className={cn(
          'h-1.5 w-1.5 rounded-full',
          connected ? 'bg-emerald-400' : 'bg-zinc-500'
        )}
      />
      {connected ? 'Connected' : 'Offline'}
    </span>
  );
}

function StatCard({
  label,
  value,
  icon: Icon,
}: {
  label: string;
  value: number;
  icon: React.ElementType;
}) {
  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4">
      <div className="flex items-center gap-3">
        <div className="rounded-md bg-zinc-800 p-2">
          <Icon className="h-4 w-4 text-zinc-400" />
        </div>
        <div>
          <p className="text-2xl font-semibold text-zinc-100">{value}</p>
          <p className="text-xs text-zinc-500">{label}</p>
        </div>
      </div>
    </div>
  );
}

function DatasetCard({ dataset }: { dataset: DatasetResult }) {
  const name = dataset.urn?.split(',').pop()?.replace(')', '') || dataset.urn;
  const platform =
    dataset.urn?.match(/dataPlatform:(\w+)/)?.[1] || 'unknown';

  return (
    <Link
      href={`/catalog/${encodeURIComponent(dataset.urn)}`}
      className="block rounded-lg border border-zinc-800 bg-zinc-900/50 p-4 transition-colors hover:border-zinc-700 hover:bg-zinc-900"
    >
      <div className="flex items-start justify-between">
        <div className="min-w-0 flex-1">
          <h3 className="truncate text-sm font-medium text-zinc-100">
            {name}
          </h3>
          <div className="mt-1 flex items-center gap-2">
            <span className="inline-flex items-center gap-1 rounded bg-blue-500/10 px-1.5 py-0.5 text-xs text-blue-400">
              <Database className="h-3 w-3" />
              {platform}
            </span>
          </div>
        </div>
        <GitBranch className="h-4 w-4 flex-shrink-0 text-zinc-600" />
      </div>
    </Link>
  );
}

export default function CatalogPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<DatasetResult[]>([]);
  const [stats, setStats] = useState<CatalogStats>({
    datasets: 0,
    dashboards: 0,
    pipelines: 0,
  });
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'datasets' | 'domains' | 'glossary'>('datasets');

  const loadStats = useCallback(async () => {
    try {
      const s = await fetchStats();
      setStats(s);
      setConnected(true);
    } catch {
      setConnected(false);
    }
  }, []);

  const doSearch = useCallback(
    async (q: string) => {
      setLoading(true);
      try {
        const data = await searchCatalog(q || '*');
        const entities = data?.value?.entities || data?.entities || [];
        setResults(entities);
        setConnected(true);
      } catch {
        setResults([]);
        setConnected(false);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  useEffect(() => {
    loadStats();
    doSearch('');
  }, [loadStats, doSearch]);

  const datahubUrl =
    process.env.NEXT_PUBLIC_DATAHUB_URL || 'http://datahub.local';

  const tabs = [
    { id: 'datasets' as const, label: 'Datasets', icon: Table2 },
    { id: 'domains' as const, label: 'Domains', icon: Globe },
    { id: 'glossary' as const, label: 'Glossary', icon: BookOpen },
  ];

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-zinc-100">Data Catalog</h1>
          <p className="mt-1 text-sm text-zinc-500">
            Discover, understand, and govern your data assets via DataHub
          </p>
        </div>
        <div className="flex items-center gap-3">
          <StatusBadge connected={connected} />
          <a
            href={datahubUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 rounded-md border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-300 transition-colors hover:bg-zinc-700"
          >
            Open DataHub UI
            <ExternalLink className="h-3.5 w-3.5" />
          </a>
          <button
            onClick={() => {
              loadStats();
              doSearch(query);
            }}
            className="rounded-md border border-zinc-700 bg-zinc-800 p-1.5 text-zinc-400 transition-colors hover:bg-zinc-700"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <StatCard label="Datasets" value={stats.datasets} icon={Table2} />
        <StatCard label="Dashboards" value={stats.dashboards} icon={BarChart3} />
        <StatCard label="Pipelines" value={stats.pipelines} icon={GitBranch} />
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-500" />
        <input
          type="text"
          placeholder="Search datasets, tables, dashboards..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && doSearch(query)}
          className="w-full rounded-md border border-zinc-800 bg-zinc-900 py-2 pl-10 pr-4 text-sm text-zinc-100 placeholder-zinc-600 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-zinc-800">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              'flex items-center gap-1.5 border-b-2 px-3 py-2 text-sm font-medium transition-colors',
              activeTab === tab.id
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-zinc-500 hover:text-zinc-300'
            )}
          >
            <tab.icon className="h-3.5 w-3.5" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Results */}
      <div>
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-6 w-6 animate-spin text-zinc-500" />
          </div>
        ) : results.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-zinc-500">
            <Database className="mb-3 h-10 w-10 text-zinc-700" />
            <p className="text-sm">
              {connected
                ? 'No datasets found. Try a different search query.'
                : 'Could not connect to DataHub. Check that the GMS service is running.'}
            </p>
          </div>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {results.map((ds, i) => (
              <DatasetCard key={ds.urn || i} dataset={ds} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
