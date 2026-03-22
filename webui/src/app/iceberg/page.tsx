'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Database,
  Table2,
  RefreshCw,
  Loader2,
  Plus,
  Layers,
  History,
  Eye,
  ChevronRight,
  X,
} from 'lucide-react';
import { cn } from '@/lib/utils';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

interface SchemaField {
  field_id: number;
  name: string;
  type: string;
  required: boolean;
}

interface Snapshot {
  snapshot_id: number;
  timestamp_ms: number;
  manifest_list: string;
}

interface TableMeta {
  table_uuid: string;
  location: string;
  format_version: number;
  schema: SchemaField[];
  snapshot_count: number;
  partition_specs: { spec_id: number; fields: number }[];
  properties: Record<string, any>;
}

// API helpers
async function fetchNamespaces(): Promise<string[]> {
  const res = await fetch(`${API_BASE}/api/v1/iceberg/namespaces`);
  const data = await res.json();
  return data.namespaces || [];
}

async function fetchTables(ns: string): Promise<string[]> {
  const res = await fetch(`${API_BASE}/api/v1/iceberg/tables?namespace=${ns}`);
  const data = await res.json();
  return data.tables || [];
}

async function fetchTableMeta(ns: string, table: string): Promise<TableMeta> {
  const res = await fetch(`${API_BASE}/api/v1/iceberg/tables/${ns}/${table}`);
  return res.json();
}

async function fetchSnapshots(ns: string, table: string): Promise<Snapshot[]> {
  const res = await fetch(`${API_BASE}/api/v1/iceberg/tables/${ns}/${table}/snapshots`);
  const data = await res.json();
  return data.snapshots || [];
}

async function fetchPreview(ns: string, table: string, limit = 50) {
  const res = await fetch(
    `${API_BASE}/api/v1/iceberg/tables/${ns}/${table}/preview?limit=${limit}`
  );
  return res.json();
}

function CreateTableDialog({
  open,
  onClose,
  namespaces,
}: {
  open: boolean;
  onClose: () => void;
  namespaces: string[];
}) {
  const [ns, setNs] = useState(namespaces[0] || '');
  const [tableName, setTableName] = useState('');
  const [fields, setFields] = useState([{ name: '', type: 'string', required: false }]);
  const [creating, setCreating] = useState(false);

  if (!open) return null;

  const addField = () => setFields([...fields, { name: '', type: 'string', required: false }]);

  const submit = async () => {
    setCreating(true);
    try {
      await fetch(`${API_BASE}/api/v1/iceberg/tables`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          namespace: ns,
          table: tableName,
          schema_fields: fields.filter((f) => f.name),
        }),
      });
      onClose();
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="w-full max-w-lg rounded-lg border border-zinc-800 bg-zinc-900 p-6">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-zinc-100">Create Iceberg Table</h2>
          <button onClick={onClose} className="text-zinc-500 hover:text-zinc-300">
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs text-zinc-500">Namespace</label>
              <select
                value={ns}
                onChange={(e) => setNs(e.target.value)}
                className="w-full rounded-md border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-200"
              >
                {namespaces.map((n) => (
                  <option key={n} value={n}>{n}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-xs text-zinc-500">Table Name</label>
              <input
                value={tableName}
                onChange={(e) => setTableName(e.target.value)}
                className="w-full rounded-md border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-200"
                placeholder="my_table"
              />
            </div>
          </div>

          <div>
            <label className="mb-1 block text-xs text-zinc-500">Schema Fields</label>
            <div className="space-y-2">
              {fields.map((f, i) => (
                <div key={i} className="grid grid-cols-3 gap-2">
                  <input
                    value={f.name}
                    onChange={(e) => {
                      const copy = [...fields];
                      copy[i].name = e.target.value;
                      setFields(copy);
                    }}
                    placeholder="column_name"
                    className="rounded-md border border-zinc-700 bg-zinc-800 px-2 py-1 text-sm text-zinc-200"
                  />
                  <select
                    value={f.type}
                    onChange={(e) => {
                      const copy = [...fields];
                      copy[i].type = e.target.value;
                      setFields(copy);
                    }}
                    className="rounded-md border border-zinc-700 bg-zinc-800 px-2 py-1 text-sm text-zinc-200"
                  >
                    {['string', 'long', 'integer', 'float', 'double', 'boolean', 'timestamp'].map((t) => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                  <label className="flex items-center gap-1 text-xs text-zinc-400">
                    <input
                      type="checkbox"
                      checked={f.required}
                      onChange={(e) => {
                        const copy = [...fields];
                        copy[i].required = e.target.checked;
                        setFields(copy);
                      }}
                    />
                    Required
                  </label>
                </div>
              ))}
            </div>
            <button
              onClick={addField}
              className="mt-2 text-xs text-blue-400 hover:underline"
            >
              + Add field
            </button>
          </div>
        </div>

        <div className="mt-6 flex justify-end gap-2">
          <button
            onClick={onClose}
            className="rounded-md border border-zinc-700 px-3 py-1.5 text-sm text-zinc-400 hover:bg-zinc-800"
          >
            Cancel
          </button>
          <button
            onClick={submit}
            disabled={creating || !tableName}
            className="rounded-md bg-blue-600 px-3 py-1.5 text-sm text-white hover:bg-blue-500 disabled:opacity-50"
          >
            {creating ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Create'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function IcebergPage() {
  const [namespaces, setNamespaces] = useState<string[]>([]);
  const [activeNs, setActiveNs] = useState('');
  const [tables, setTables] = useState<string[]>([]);
  const [selectedTable, setSelectedTable] = useState<string | null>(null);
  const [tableMeta, setTableMeta] = useState<TableMeta | null>(null);
  const [snapshots, setSnapshots] = useState<Snapshot[]>([]);
  const [preview, setPreview] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [detailTab, setDetailTab] = useState<'schema' | 'snapshots' | 'preview'>('schema');
  const [showCreate, setShowCreate] = useState(false);

  const loadNamespaces = useCallback(async () => {
    try {
      const ns = await fetchNamespaces();
      setNamespaces(ns);
      if (ns.length > 0 && !activeNs) setActiveNs(ns[0]);
    } catch {
      setNamespaces([]);
    }
  }, [activeNs]);

  const loadTables = useCallback(async () => {
    if (!activeNs) return;
    setLoading(true);
    try {
      setTables(await fetchTables(activeNs));
    } catch {
      setTables([]);
    } finally {
      setLoading(false);
    }
  }, [activeNs]);

  const loadDetail = useCallback(async (table: string) => {
    if (!activeNs) return;
    setSelectedTable(table);
    const tblName = table.includes('.') ? table.split('.').pop()! : table;
    try {
      const [meta, snaps] = await Promise.all([
        fetchTableMeta(activeNs, tblName),
        fetchSnapshots(activeNs, tblName),
      ]);
      setTableMeta(meta);
      setSnapshots(snaps);
      setPreview(null);
    } catch (e) {
      console.error('Failed to load table detail', e);
    }
  }, [activeNs]);

  const loadPreview = useCallback(async () => {
    if (!activeNs || !selectedTable) return;
    const tblName = selectedTable.includes('.') ? selectedTable.split('.').pop()! : selectedTable;
    try {
      setPreview(await fetchPreview(activeNs, tblName));
    } catch (e) {
      console.error('Failed to load preview', e);
    }
  }, [activeNs, selectedTable]);

  useEffect(() => { loadNamespaces(); }, [loadNamespaces]);
  useEffect(() => { loadTables(); }, [loadTables]);

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-zinc-100">Iceberg Tables</h1>
          <p className="mt-1 text-sm text-zinc-500">
            Browse and manage Apache Iceberg tables backed by MinIO
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowCreate(true)}
            className="inline-flex items-center gap-1.5 rounded-md bg-blue-600 px-3 py-1.5 text-sm text-white hover:bg-blue-500"
          >
            <Plus className="h-3.5 w-3.5" /> New Table
          </button>
          <button
            onClick={() => { loadNamespaces(); loadTables(); }}
            className="rounded-md border border-zinc-700 bg-zinc-800 p-1.5 text-zinc-400 hover:bg-zinc-700"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Sidebar: namespace + table list */}
        <div className="space-y-4 lg:col-span-1">
          {/* Namespace selector */}
          <div>
            <label className="mb-1 block text-xs font-medium text-zinc-500">Namespace</label>
            <select
              value={activeNs}
              onChange={(e) => { setActiveNs(e.target.value); setSelectedTable(null); }}
              className="w-full rounded-md border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm text-zinc-200"
            >
              {namespaces.map((ns) => (
                <option key={ns} value={ns}>{ns}</option>
              ))}
            </select>
          </div>

          {/* Table list */}
          <div className="rounded-lg border border-zinc-800 bg-zinc-900/50">
            <div className="border-b border-zinc-800 px-3 py-2 text-xs font-medium text-zinc-500">
              Tables ({tables.length})
            </div>
            {loading ? (
              <div className="flex justify-center py-6">
                <Loader2 className="h-5 w-5 animate-spin text-zinc-600" />
              </div>
            ) : tables.length === 0 ? (
              <p className="px-3 py-4 text-center text-xs text-zinc-600">No tables found</p>
            ) : (
              <ul className="divide-y divide-zinc-800/50">
                {tables.map((t) => (
                  <li key={t}>
                    <button
                      onClick={() => loadDetail(t)}
                      className={cn(
                        'flex w-full items-center gap-2 px-3 py-2 text-left text-sm transition-colors hover:bg-zinc-800/50',
                        selectedTable === t ? 'bg-zinc-800/50 text-blue-400' : 'text-zinc-300'
                      )}
                    >
                      <Table2 className="h-3.5 w-3.5 flex-shrink-0" />
                      <span className="truncate">{t}</span>
                      <ChevronRight className="ml-auto h-3.5 w-3.5 flex-shrink-0 text-zinc-600" />
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Detail panel */}
        <div className="lg:col-span-2">
          {!selectedTable || !tableMeta ? (
            <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-zinc-800 py-16 text-zinc-600">
              <Layers className="mb-3 h-10 w-10 text-zinc-700" />
              <p className="text-sm">Select a table to view its details</p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Table header */}
              <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4">
                <h2 className="text-lg font-semibold text-zinc-100">{selectedTable}</h2>
                <div className="mt-2 flex flex-wrap gap-3 text-xs text-zinc-500">
                  <span>Format v{tableMeta.format_version}</span>
                  <span>{tableMeta.schema?.length || 0} columns</span>
                  <span>{tableMeta.snapshot_count} snapshots</span>
                </div>
              </div>

              {/* Detail tabs */}
              <div className="flex gap-1 border-b border-zinc-800">
                {([
                  { id: 'schema' as const, label: 'Schema', icon: Database },
                  { id: 'snapshots' as const, label: 'Snapshots', icon: History },
                  { id: 'preview' as const, label: 'Preview', icon: Eye },
                ]).map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => {
                      setDetailTab(tab.id);
                      if (tab.id === 'preview' && !preview) loadPreview();
                    }}
                    className={cn(
                      'flex items-center gap-1.5 border-b-2 px-3 py-2 text-sm font-medium transition-colors',
                      detailTab === tab.id
                        ? 'border-blue-500 text-blue-400'
                        : 'border-transparent text-zinc-500 hover:text-zinc-300'
                    )}
                  >
                    <tab.icon className="h-3.5 w-3.5" />
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Schema */}
              {detailTab === 'schema' && (
                <div className="overflow-x-auto rounded-lg border border-zinc-800">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-zinc-800 bg-zinc-900/50">
                        <th className="px-4 py-2 text-left font-medium text-zinc-400">ID</th>
                        <th className="px-4 py-2 text-left font-medium text-zinc-400">Name</th>
                        <th className="px-4 py-2 text-left font-medium text-zinc-400">Type</th>
                        <th className="px-4 py-2 text-left font-medium text-zinc-400">Required</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-zinc-800/50">
                      {(tableMeta.schema || []).map((f) => (
                        <tr key={f.field_id} className="text-zinc-300">
                          <td className="px-4 py-2 text-zinc-500">{f.field_id}</td>
                          <td className="px-4 py-2 font-mono text-xs">{f.name}</td>
                          <td className="px-4 py-2 text-zinc-500">{f.type}</td>
                          <td className="px-4 py-2">{f.required ? 'Yes' : 'No'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Snapshots */}
              {detailTab === 'snapshots' && (
                <div className="space-y-2">
                  {snapshots.length === 0 ? (
                    <p className="py-6 text-center text-sm text-zinc-600">No snapshots yet</p>
                  ) : (
                    snapshots.map((s) => (
                      <div
                        key={s.snapshot_id}
                        className="rounded-md border border-zinc-800 bg-zinc-900/50 px-4 py-3"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-mono text-xs text-zinc-300">
                            {s.snapshot_id}
                          </span>
                          <span className="text-xs text-zinc-500">
                            {new Date(s.timestamp_ms).toLocaleString()}
                          </span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}

              {/* Preview */}
              {detailTab === 'preview' && (
                <div>
                  {!preview ? (
                    <div className="flex justify-center py-8">
                      <Loader2 className="h-5 w-5 animate-spin text-zinc-600" />
                    </div>
                  ) : preview.columns?.length > 0 ? (
                    <div className="overflow-x-auto rounded-lg border border-zinc-800">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b border-zinc-800 bg-zinc-900/50">
                            {preview.columns.map((col: string) => (
                              <th key={col} className="px-3 py-2 text-left font-medium text-zinc-400">
                                {col}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-zinc-800/50">
                          {Array.from({ length: preview.total_rows || 0 }).map((_, rowIdx) => (
                            <tr key={rowIdx} className="text-zinc-300">
                              {preview.columns.map((col: string) => (
                                <td key={col} className="whitespace-nowrap px-3 py-1.5 text-xs">
                                  {String(preview.rows[col]?.[rowIdx] ?? '')}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <p className="py-6 text-center text-sm text-zinc-600">
                      Table is empty or cannot be previewed
                    </p>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <CreateTableDialog
        open={showCreate}
        onClose={() => { setShowCreate(false); loadTables(); }}
        namespaces={namespaces}
      />
    </div>
  );
}
