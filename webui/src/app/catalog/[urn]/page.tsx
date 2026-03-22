'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  ArrowLeft,
  Database,
  GitBranch,
  Table2,
  Columns3,
  History,
  ExternalLink,
  Loader2,
  Tag,
} from 'lucide-react';
import { cn } from '@/lib/utils';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

interface ColumnInfo {
  fieldPath: string;
  type: string;
  nativeDataType?: string;
  description?: string;
  nullable?: boolean;
  tags?: string[];
}

interface LineageRelation {
  entity: string;
  type: string;
}

export default function DatasetDetailPage() {
  const params = useParams();
  const router = useRouter();
  const urn = decodeURIComponent(params.urn as string);

  const [dataset, setDataset] = useState<any>(null);
  const [lineage, setLineage] = useState<{ upstream: LineageRelation[]; downstream: LineageRelation[] }>({
    upstream: [],
    downstream: [],
  });
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'schema' | 'lineage' | 'stats'>('schema');

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const [dsRes, upRes, downRes] = await Promise.all([
          fetch(`${API_BASE}/api/v1/catalog/datasets/${encodeURIComponent(urn)}`).then((r) => r.json()),
          fetch(`${API_BASE}/api/v1/catalog/lineage/${encodeURIComponent(urn)}?direction=UPSTREAM`).then((r) => r.json()).catch(() => ({ relationships: [] })),
          fetch(`${API_BASE}/api/v1/catalog/lineage/${encodeURIComponent(urn)}?direction=DOWNSTREAM`).then((r) => r.json()).catch(() => ({ relationships: [] })),
        ]);
        setDataset(dsRes);
        setLineage({
          upstream: upRes.relationships || [],
          downstream: downRes.relationships || [],
        });
      } catch (e) {
        console.error('Failed to load dataset', e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [urn]);

  const name = urn.split(',').pop()?.replace(')', '') || urn;
  const platform = urn.match(/dataPlatform:(\w+)/)?.[1] || 'unknown';

  const schemaFields: ColumnInfo[] =
    dataset?.aspects?.schemaMetadata?.fields ||
    dataset?.schemaMetadata?.fields ||
    [];

  const datahubUrl =
    process.env.NEXT_PUBLIC_DATAHUB_URL || 'http://datahub.local';

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <Loader2 className="h-6 w-6 animate-spin text-zinc-500" />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => router.back()}
          className="rounded-md border border-zinc-800 bg-zinc-900 p-1.5 text-zinc-400 hover:bg-zinc-800"
        >
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div className="flex-1">
          <h1 className="text-xl font-bold text-zinc-100">{name}</h1>
          <div className="mt-1 flex items-center gap-2">
            <span className="inline-flex items-center gap-1 rounded bg-blue-500/10 px-1.5 py-0.5 text-xs text-blue-400">
              <Database className="h-3 w-3" />
              {platform}
            </span>
          </div>
        </div>
        <a
          href={`${datahubUrl}/dataset/${encodeURIComponent(urn)}`}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 rounded-md border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-300 hover:bg-zinc-700"
        >
          View in DataHub
          <ExternalLink className="h-3.5 w-3.5" />
        </a>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-zinc-800">
        {([
          { id: 'schema' as const, label: 'Schema', icon: Columns3 },
          { id: 'lineage' as const, label: 'Lineage', icon: GitBranch },
          { id: 'stats' as const, label: 'Statistics', icon: Table2 },
        ]).map((tab) => (
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

      {/* Schema tab */}
      {activeTab === 'schema' && (
        <div className="overflow-x-auto rounded-lg border border-zinc-800">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-zinc-800 bg-zinc-900/50">
                <th className="px-4 py-2 text-left font-medium text-zinc-400">Column</th>
                <th className="px-4 py-2 text-left font-medium text-zinc-400">Type</th>
                <th className="px-4 py-2 text-left font-medium text-zinc-400">Description</th>
                <th className="px-4 py-2 text-left font-medium text-zinc-400">Tags</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/50">
              {schemaFields.length > 0 ? (
                schemaFields.map((col, i) => (
                  <tr key={i} className="text-zinc-300 hover:bg-zinc-900/30">
                    <td className="px-4 py-2 font-mono text-xs">{col.fieldPath}</td>
                    <td className="px-4 py-2 text-zinc-500">
                      {col.nativeDataType || col.type}
                    </td>
                    <td className="px-4 py-2 text-zinc-500">{col.description || '-'}</td>
                    <td className="px-4 py-2">
                      {col.tags?.map((t, j) => (
                        <span
                          key={j}
                          className="mr-1 rounded bg-zinc-800 px-1.5 py-0.5 text-xs text-zinc-400"
                        >
                          {t}
                        </span>
                      ))}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="px-4 py-8 text-center text-zinc-600">
                    No schema information available
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Lineage tab */}
      {activeTab === 'lineage' && (
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4">
            <h3 className="mb-3 text-sm font-medium text-zinc-300">Upstream</h3>
            {lineage.upstream.length > 0 ? (
              <ul className="space-y-2">
                {lineage.upstream.map((rel, i) => (
                  <li
                    key={i}
                    className="rounded-md border border-zinc-800 bg-zinc-900 px-3 py-2 text-xs text-zinc-400"
                  >
                    {rel.entity}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-xs text-zinc-600">No upstream dependencies</p>
            )}
          </div>
          <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4">
            <h3 className="mb-3 text-sm font-medium text-zinc-300">Downstream</h3>
            {lineage.downstream.length > 0 ? (
              <ul className="space-y-2">
                {lineage.downstream.map((rel, i) => (
                  <li
                    key={i}
                    className="rounded-md border border-zinc-800 bg-zinc-900 px-3 py-2 text-xs text-zinc-400"
                  >
                    {rel.entity}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-xs text-zinc-600">No downstream dependents</p>
            )}
          </div>
        </div>
      )}

      {/* Stats tab */}
      {activeTab === 'stats' && (
        <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-6 text-center text-sm text-zinc-500">
          Dataset profiling statistics will appear here once DataHub collects profile data.
          <br />
          <a
            href={`${datahubUrl}/dataset/${encodeURIComponent(urn)}/Stats`}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-2 inline-flex items-center gap-1 text-blue-400 hover:underline"
          >
            View stats in DataHub <ExternalLink className="h-3 w-3" />
          </a>
        </div>
      )}
    </div>
  );
}
