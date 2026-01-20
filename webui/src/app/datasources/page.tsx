"use client";

import * as React from "react";
import Link from "next/link";
import { 
  Plus, 
  Search, 
  Filter, 
  MoreHorizontal, 
  Database, 
  Pencil, 
  Trash2,
  Globe,
  FolderClosed,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Clock,
  ArrowUpRight,
  Link2,
  Table2,
  HardDrive,
  Plug,
  ChevronRight,
  ChevronLeft,
  Eye,
  Loader2,
  Copy,
  Columns3,
  Key,
  Hash,
  FileJson,
  Snowflake,
  Flame,
  Zap,
  Cloud
} from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  useDataSources, 
  useTestDataSource, 
  usePromoteDataSource,
  useDeleteDataSource,
  useCreateDataSource,
  useProjects,
  useDataSourceSchema,
  useTestDataSourceConfig,
} from "@/lib/api";
import type { DataSource, SchemaInfo, TableSchema, ColumnSchema } from "@/lib/types";
import { toast } from "sonner";

const sourceTypeIcons: Record<string, React.ReactNode> = {
  database: <Database className="size-5" />,
  file_store: <HardDrive className="size-5" />,
  api: <Plug className="size-5" />,
};

const sourceTypeColors: Record<string, string> = {
  database: "from-blue-500 to-indigo-500",
  file_store: "from-emerald-500 to-teal-500",
  api: "from-purple-500 to-pink-500",
};

const statusBadgeStyles: Record<string, string> = {
  active: "bg-green-500/10 text-green-500 border-green-500/20",
  inactive: "bg-gray-500/10 text-gray-500 border-gray-500/20",
  error: "bg-red-500/10 text-red-500 border-red-500/20",
};

// ============================================================================
// Database Types Configuration
// ============================================================================

interface DatabaseTypeConfig {
  id: string;
  name: string;
  icon: React.ReactNode;
  description: string;
  color: string;
  fields: DatabaseField[];
  defaultPort?: number;
}

interface DatabaseField {
  name: string;
  label: string;
  type: "text" | "password" | "number" | "boolean" | "textarea";
  placeholder?: string;
  required?: boolean;
  description?: string;
  defaultValue?: string | number | boolean;
}

const DATABASE_TYPES: DatabaseTypeConfig[] = [
  {
    id: "postgresql",
    name: "PostgreSQL",
    icon: <Database className="size-6" />,
    description: "Open-source relational database",
    color: "from-blue-500 to-blue-600",
    defaultPort: 5432,
    fields: [
      { name: "host", label: "Host", type: "text", placeholder: "localhost", required: true },
      { name: "port", label: "Port", type: "number", placeholder: "5432", defaultValue: 5432, required: true },
      { name: "database", label: "Database", type: "text", placeholder: "mydb", required: true },
      { name: "username", label: "Username", type: "text", placeholder: "postgres", required: true },
      { name: "password", label: "Password", type: "password", placeholder: "••••••••", required: true },
      { name: "ssl", label: "Use SSL", type: "boolean", defaultValue: false },
    ],
  },
  {
    id: "mysql",
    name: "MySQL",
    icon: <Database className="size-6" />,
    description: "Popular open-source database",
    color: "from-orange-500 to-orange-600",
    defaultPort: 3306,
    fields: [
      { name: "host", label: "Host", type: "text", placeholder: "localhost", required: true },
      { name: "port", label: "Port", type: "number", placeholder: "3306", defaultValue: 3306, required: true },
      { name: "database", label: "Database", type: "text", placeholder: "mydb", required: true },
      { name: "username", label: "Username", type: "text", placeholder: "root", required: true },
      { name: "password", label: "Password", type: "password", placeholder: "••••••••", required: true },
    ],
  },
  {
    id: "mongodb",
    name: "MongoDB",
    icon: <FileJson className="size-6" />,
    description: "Document-oriented NoSQL database",
    color: "from-green-500 to-green-600",
    defaultPort: 27017,
    fields: [
      { name: "connection_string", label: "Connection String", type: "text", placeholder: "mongodb://localhost:27017", description: "Full MongoDB connection URI" },
      { name: "host", label: "Or Host", type: "text", placeholder: "localhost" },
      { name: "port", label: "Port", type: "number", placeholder: "27017", defaultValue: 27017 },
      { name: "database", label: "Database", type: "text", placeholder: "mydb", required: true },
      { name: "username", label: "Username", type: "text", placeholder: "admin" },
      { name: "password", label: "Password", type: "password", placeholder: "••••••••" },
    ],
  },
  {
    id: "redis",
    name: "Redis",
    icon: <Flame className="size-6" />,
    description: "In-memory data structure store",
    color: "from-red-500 to-red-600",
    defaultPort: 6379,
    fields: [
      { name: "host", label: "Host", type: "text", placeholder: "localhost", required: true },
      { name: "port", label: "Port", type: "number", placeholder: "6379", defaultValue: 6379, required: true },
      { name: "password", label: "Password", type: "password", placeholder: "••••••••" },
      { name: "db", label: "Database Index", type: "number", placeholder: "0", defaultValue: 0 },
      { name: "ssl", label: "Use SSL", type: "boolean", defaultValue: false },
    ],
  },
  {
    id: "elasticsearch",
    name: "Elasticsearch",
    icon: <Zap className="size-6" />,
    description: "Distributed search and analytics",
    color: "from-yellow-500 to-yellow-600",
    defaultPort: 9200,
    fields: [
      { name: "hosts", label: "Hosts", type: "text", placeholder: "http://localhost:9200", description: "Comma-separated list of hosts", required: true },
      { name: "username", label: "Username", type: "text", placeholder: "elastic" },
      { name: "password", label: "Password", type: "password", placeholder: "••••••••" },
      { name: "api_key", label: "API Key", type: "password", placeholder: "API key (alternative to user/pass)" },
      { name: "verify_certs", label: "Verify SSL Certs", type: "boolean", defaultValue: true },
    ],
  },
  {
    id: "bigquery",
    name: "BigQuery",
    icon: <Cloud className="size-6" />,
    description: "Google Cloud data warehouse",
    color: "from-blue-400 to-cyan-500",
    fields: [
      { name: "project_id", label: "Project ID", type: "text", placeholder: "my-gcp-project", required: true },
      { name: "dataset", label: "Dataset", type: "text", placeholder: "my_dataset" },
      { name: "credentials_json", label: "Service Account JSON", type: "textarea", placeholder: '{"type": "service_account", ...}', description: "Paste your service account JSON key" },
      { name: "location", label: "Location", type: "text", placeholder: "US", defaultValue: "US" },
    ],
  },
  {
    id: "snowflake",
    name: "Snowflake",
    icon: <Snowflake className="size-6" />,
    description: "Cloud data platform",
    color: "from-cyan-400 to-blue-500",
    fields: [
      { name: "account", label: "Account", type: "text", placeholder: "xy12345.us-east-1", required: true },
      { name: "username", label: "Username", type: "text", placeholder: "user", required: true },
      { name: "password", label: "Password", type: "password", placeholder: "••••••••", required: true },
      { name: "warehouse", label: "Warehouse", type: "text", placeholder: "COMPUTE_WH" },
      { name: "database", label: "Database", type: "text", placeholder: "MY_DB" },
      { name: "schema", label: "Schema", type: "text", placeholder: "PUBLIC", defaultValue: "PUBLIC" },
      { name: "role", label: "Role", type: "text", placeholder: "ACCOUNTADMIN" },
    ],
  },
  {
    id: "sqlite",
    name: "SQLite",
    icon: <Database className="size-6" />,
    description: "Lightweight file-based database",
    color: "from-gray-500 to-gray-600",
    fields: [
      { name: "database_path", label: "Database Path", type: "text", placeholder: "/path/to/database.db", required: true, description: "Path to SQLite database file" },
    ],
  },
];

// ============================================================================
// Schema Browser Dialog
// ============================================================================

function SchemaBrowserDialog({
  dataSourceId,
  dataSourceName,
  open,
  onOpenChange,
}: {
  dataSourceId: string;
  dataSourceName: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const { data: schema, isLoading, error } = useDataSourceSchema(open ? dataSourceId : null);
  const [selectedTable, setSelectedTable] = React.useState<string | null>(null);
  const [searchQuery, setSearchQuery] = React.useState("");

  const filteredTables = React.useMemo(() => {
    if (!schema?.tables) return [];
    if (!searchQuery) return schema.tables;
    const query = searchQuery.toLowerCase();
    return schema.tables.filter(
      (t) =>
        t.name.toLowerCase().includes(query) ||
        t.columns.some((c) => c.name.toLowerCase().includes(query))
    );
  }, [schema?.tables, searchQuery]);

  const selectedTableData = React.useMemo(() => {
    if (!selectedTable || !schema?.tables) return null;
    return schema.tables.find((t) => t.name === selectedTable);
  }, [selectedTable, schema?.tables]);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard");
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[900px] max-h-[80vh]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Table2 className="size-5" />
            Schema Browser - {dataSourceName}
          </DialogTitle>
          <DialogDescription>
            Explore tables, columns, and data types
          </DialogDescription>
        </DialogHeader>

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="size-8 animate-spin text-muted-foreground" />
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <XCircle className="size-12 mx-auto mb-4 text-destructive/50" />
            <p className="text-muted-foreground">Failed to load schema</p>
            <p className="text-sm text-muted-foreground mt-1">
              Make sure the connection is working
            </p>
          </div>
        ) : schema?.tables && schema.tables.length > 0 ? (
          <div className="grid grid-cols-3 gap-4 h-[500px]">
            {/* Tables List */}
            <div className="col-span-1 border rounded-lg overflow-hidden flex flex-col">
              <div className="p-3 border-b bg-muted/30">
                <div className="relative">
                  <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                  <Input
                    placeholder="Search tables..."
                    className="pl-8 h-8"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
              </div>
              <ScrollArea className="flex-1">
                <div className="p-2 space-y-1">
                  {filteredTables.map((table) => (
                    <button
                      key={table.name}
                      onClick={() => setSelectedTable(table.name)}
                      className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors flex items-center justify-between group ${
                        selectedTable === table.name
                          ? "bg-primary text-primary-foreground"
                          : "hover:bg-muted"
                      }`}
                    >
                      <span className="flex items-center gap-2 truncate">
                        <Table2 className="size-4 shrink-0" />
                        <span className="truncate">{table.name}</span>
                      </span>
                      <Badge
                        variant={selectedTable === table.name ? "secondary" : "outline"}
                        className="text-xs shrink-0"
                      >
                        {table.columns.length}
                      </Badge>
                    </button>
                  ))}
                </div>
              </ScrollArea>
              <div className="p-2 border-t bg-muted/30 text-xs text-muted-foreground">
                {filteredTables.length} table{filteredTables.length !== 1 ? "s" : ""}
              </div>
            </div>

            {/* Column Details */}
            <div className="col-span-2 border rounded-lg overflow-hidden flex flex-col">
              {selectedTableData ? (
                <>
                  <div className="p-3 border-b bg-muted/30 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Table2 className="size-4" />
                      <span className="font-medium">{selectedTableData.name}</span>
                      {selectedTableData.row_count !== undefined && (
                        <Badge variant="secondary" className="text-xs">
                          {selectedTableData.row_count.toLocaleString()} rows
                        </Badge>
                      )}
                    </div>
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="size-8"
                            onClick={() => copyToClipboard(selectedTableData.name)}
                          >
                            <Copy className="size-4" />
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>Copy table name</TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </div>
                  <ScrollArea className="flex-1">
                    <div className="p-2">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b">
                            <th className="text-left p-2 font-medium text-muted-foreground">Column</th>
                            <th className="text-left p-2 font-medium text-muted-foreground">Type</th>
                            <th className="text-center p-2 font-medium text-muted-foreground">Nullable</th>
                            <th className="text-center p-2 font-medium text-muted-foreground">Key</th>
                          </tr>
                        </thead>
                        <tbody>
                          {selectedTableData.columns.map((column) => (
                            <tr
                              key={column.name}
                              className="border-b last:border-0 hover:bg-muted/50 transition-colors"
                            >
                              <td className="p-2">
                                <div className="flex items-center gap-2">
                                  <Columns3 className="size-4 text-muted-foreground" />
                                  <span className="font-mono">{column.name}</span>
                                </div>
                              </td>
                              <td className="p-2">
                                <Badge variant="outline" className="font-mono text-xs">
                                  {column.data_type}
                                </Badge>
                              </td>
                              <td className="p-2 text-center">
                                {column.nullable ? (
                                  <span className="text-muted-foreground">Yes</span>
                                ) : (
                                  <span className="text-orange-500 font-medium">No</span>
                                )}
                              </td>
                              <td className="p-2 text-center">
                                {column.primary_key && (
                                  <TooltipProvider>
                                    <Tooltip>
                                      <TooltipTrigger>
                                        <Key className="size-4 text-yellow-500 mx-auto" />
                                      </TooltipTrigger>
                                      <TooltipContent>Primary Key</TooltipContent>
                                    </Tooltip>
                                  </TooltipProvider>
                                )}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </ScrollArea>
                </>
              ) : (
                <div className="flex-1 flex items-center justify-center text-muted-foreground">
                  <div className="text-center">
                    <Columns3 className="size-12 mx-auto mb-4 opacity-30" />
                    <p>Select a table to view columns</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="text-center py-12">
            <Table2 className="size-12 mx-auto mb-4 opacity-30" />
            <p className="text-muted-foreground">No tables found</p>
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// ============================================================================
// Data Source Card Component
// ============================================================================

function DataSourceCard({ 
  dataSource, 
  onDelete, 
  onTest,
  onPromote,
  onViewSchema,
  isTestingConnection,
}: { 
  dataSource: DataSource; 
  onDelete: () => void;
  onTest: () => void;
  onPromote: () => void;
  onViewSchema: () => void;
  isTestingConnection?: boolean;
}) {
  return (
    <Card className="group hover:shadow-lg transition-all duration-300">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg bg-gradient-to-br ${sourceTypeColors[dataSource.source_type] || 'from-gray-500 to-gray-600'} text-white`}>
              {sourceTypeIcons[dataSource.source_type] || <Database className="size-5" />}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <CardTitle className="text-lg">
                  <Link href={`/datasources/${dataSource.id}`} className="hover:underline">
                    {dataSource.name}
                  </Link>
                </CardTitle>
                {dataSource.is_global && (
                  <Badge variant="secondary" className="text-xs gap-1">
                    <Globe className="size-3" />
                    Global
                  </Badge>
                )}
              </div>
              <CardDescription className="line-clamp-1">
                {dataSource.description || "No description"}
              </CardDescription>
            </div>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="opacity-0 group-hover:opacity-100 transition-opacity">
                <MoreHorizontal className="size-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem asChild>
                <Link href={`/datasources/${dataSource.id}`}>
                  <Pencil className="size-4 mr-2" />
                  Edit
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem onClick={onTest}>
                <RefreshCw className="size-4 mr-2" />
                Test Connection
              </DropdownMenuItem>
              {dataSource.source_type === "database" && (
                <DropdownMenuItem onClick={onViewSchema}>
                  <Table2 className="size-4 mr-2" />
                  Browse Schema
                </DropdownMenuItem>
              )}
              {!dataSource.is_global && (
                <DropdownMenuItem onClick={onPromote}>
                  <ArrowUpRight className="size-4 mr-2" />
                  Promote to Global
                </DropdownMenuItem>
              )}
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-destructive" onClick={onDelete}>
                <Trash2 className="size-4 mr-2" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center justify-between">
          <Badge variant="outline" className="gap-1">
            {sourceTypeIcons[dataSource.source_type]}
            {dataSource.source_type.replace('_', ' ')}
          </Badge>
          <div className="flex items-center gap-2">
            {isTestingConnection ? (
              <Badge variant="secondary" className="gap-1">
                <RefreshCw className="size-3 animate-spin" />
                Testing...
              </Badge>
            ) : dataSource.last_test_success !== null ? (
              <Badge 
                variant="outline" 
                className={dataSource.last_test_success ? statusBadgeStyles.active : statusBadgeStyles.error}
              >
                {dataSource.last_test_success ? (
                  <CheckCircle2 className="size-3 mr-1" />
                ) : (
                  <XCircle className="size-3 mr-1" />
                )}
                {dataSource.last_test_success ? 'Connected' : 'Failed'}
              </Badge>
            ) : (
              <Badge variant="outline" className={statusBadgeStyles.inactive}>
                <Clock className="size-3 mr-1" />
                Not tested
              </Badge>
            )}
          </div>
        </div>
        
        {dataSource.project_id && (
          <div className="flex items-center gap-1 text-sm text-muted-foreground">
            <FolderClosed className="size-3" />
            <Link href={`/projects/${dataSource.project_id}`} className="hover:underline">
              Project Scoped
            </Link>
          </div>
        )}

        {dataSource.tags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {dataSource.tags.slice(0, 3).map((tag) => (
              <Badge key={tag} variant="secondary" className="text-xs">
                {tag}
              </Badge>
            ))}
            {dataSource.tags.length > 3 && (
              <Badge variant="secondary" className="text-xs">
                +{dataSource.tags.length - 3}
              </Badge>
            )}
          </div>
        )}

        <div className="text-xs text-muted-foreground">
          Updated {new Date(dataSource.updated_at).toLocaleDateString()}
        </div>
      </CardContent>
    </Card>
  );
}

// ============================================================================
// Database Wizard Dialog (Multi-step)
// ============================================================================

type WizardStep = "type" | "config" | "details" | "test";

function CreateDataSourceDialog({ 
  open, 
  onOpenChange, 
  onCreated 
}: { 
  open: boolean; 
  onOpenChange: (open: boolean) => void;
  onCreated: () => void;
}) {
  const [step, setStep] = React.useState<WizardStep>("type");
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [isTesting, setIsTesting] = React.useState(false);
  const [testResult, setTestResult] = React.useState<{ success: boolean; message: string } | null>(null);
  
  const { trigger: createDataSource } = useCreateDataSource();
  const { trigger: testConfig } = useTestDataSourceConfig();
  const { data: projects } = useProjects();

  const [sourceType, setSourceType] = React.useState<"database" | "file_store" | "api">("database");
  const [databaseType, setDatabaseType] = React.useState<string>("postgresql");
  const [connectionFields, setConnectionFields] = React.useState<Record<string, string | number | boolean>>({});
  const [formData, setFormData] = React.useState({
    name: "",
    description: "",
    is_global: false,
    project_id: "",
  });

  const selectedDbConfig = DATABASE_TYPES.find((db) => db.id === databaseType);

  // Reset wizard when dialog opens
  React.useEffect(() => {
    if (open) {
      setStep("type");
      setSourceType("database");
      setDatabaseType("postgresql");
      setConnectionFields({});
      setFormData({
        name: "",
        description: "",
        is_global: false,
        project_id: "",
      });
      setTestResult(null);
    }
  }, [open]);

  // Initialize default values when database type changes
  React.useEffect(() => {
    if (selectedDbConfig) {
      const defaults: Record<string, string | number | boolean> = {};
      selectedDbConfig.fields.forEach((field) => {
        if (field.defaultValue !== undefined) {
          defaults[field.name] = field.defaultValue;
        }
      });
      setConnectionFields(defaults);
    }
  }, [databaseType, selectedDbConfig]);

  const buildConnectionConfig = (): Record<string, unknown> => {
    const config: Record<string, unknown> = {
      driver: databaseType,
      ...connectionFields,
    };
    // Remove empty strings
    Object.keys(config).forEach((key) => {
      if (config[key] === "" || config[key] === undefined) {
        delete config[key];
      }
    });
    return config;
  };

  const handleTestConnection = async () => {
    setIsTesting(true);
    setTestResult(null);
    try {
      const result = await testConfig({
        name: formData.name || "test",
        source_type: sourceType,
        connection_config: buildConnectionConfig(),
      });
      setTestResult({
        success: result.success,
        message: result.message,
      });
      if (result.success) {
        toast.success("Connection successful!");
      } else {
        toast.error(result.message || "Connection failed");
      }
    } catch (error) {
      setTestResult({
        success: false,
        message: "Failed to test connection",
      });
      toast.error("Failed to test connection");
    } finally {
      setIsTesting(false);
    }
  };

  const handleSubmit = async () => {
    if (!formData.name.trim()) {
      toast.error("Name is required");
      return;
    }

    setIsSubmitting(true);
    try {
      await createDataSource({
        name: formData.name.trim(),
        source_type: sourceType,
        description: formData.description.trim(),
        is_global: formData.is_global,
        project_id: formData.project_id || undefined,
        connection_config: buildConnectionConfig(),
      });

      toast.success("Data source created");
      onOpenChange(false);
      onCreated();
    } catch (error) {
      toast.error("Failed to create data source");
    } finally {
      setIsSubmitting(false);
    }
  };

  const canProceed = () => {
    switch (step) {
      case "type":
        return true;
      case "config":
        if (sourceType === "database" && selectedDbConfig) {
          return selectedDbConfig.fields
            .filter((f) => f.required)
            .every((f) => connectionFields[f.name]);
        }
        return true;
      case "details":
        return formData.name.trim().length > 0;
      case "test":
        return true;
      default:
        return false;
    }
  };

  const nextStep = () => {
    const steps: WizardStep[] = ["type", "config", "details", "test"];
    const currentIndex = steps.indexOf(step);
    if (currentIndex < steps.length - 1) {
      setStep(steps[currentIndex + 1]);
    }
  };

  const prevStep = () => {
    const steps: WizardStep[] = ["type", "config", "details", "test"];
    const currentIndex = steps.indexOf(step);
    if (currentIndex > 0) {
      setStep(steps[currentIndex - 1]);
    }
  };

  const renderStepIndicator = () => {
    const steps: { key: WizardStep; label: string }[] = [
      { key: "type", label: "Type" },
      { key: "config", label: "Connection" },
      { key: "details", label: "Details" },
      { key: "test", label: "Test" },
    ];

    return (
      <div className="flex items-center justify-center gap-2 mb-6">
        {steps.map((s, index) => (
          <React.Fragment key={s.key}>
            <div
              className={`flex items-center gap-2 ${
                step === s.key
                  ? "text-primary"
                  : steps.indexOf({ key: step, label: "" }) > index
                  ? "text-green-500"
                  : "text-muted-foreground"
              }`}
            >
              <div
                className={`size-8 rounded-full flex items-center justify-center text-sm font-medium border-2 ${
                  step === s.key
                    ? "border-primary bg-primary text-primary-foreground"
                    : steps.findIndex((x) => x.key === step) > index
                    ? "border-green-500 bg-green-500 text-white"
                    : "border-muted-foreground/30"
                }`}
              >
                {steps.findIndex((x) => x.key === step) > index ? (
                  <CheckCircle2 className="size-4" />
                ) : (
                  index + 1
                )}
              </div>
              <span className="text-sm hidden sm:inline">{s.label}</span>
            </div>
            {index < steps.length - 1 && (
              <div
                className={`w-8 h-0.5 ${
                  steps.findIndex((x) => x.key === step) > index
                    ? "bg-green-500"
                    : "bg-muted-foreground/30"
                }`}
              />
            )}
          </React.Fragment>
        ))}
      </div>
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[700px]">
        <DialogHeader>
          <DialogTitle>Create Data Source</DialogTitle>
          <DialogDescription>
            {step === "type" && "Choose the type of data source you want to connect"}
            {step === "config" && "Configure the connection settings"}
            {step === "details" && "Add name and description"}
            {step === "test" && "Test the connection and create"}
          </DialogDescription>
        </DialogHeader>

        {renderStepIndicator()}

        <div className="min-h-[350px]">
          {/* Step 1: Type Selection */}
          {step === "type" && (
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-3">
                {[
                  { id: "database", label: "Database", icon: <Database className="size-6" />, color: "from-blue-500 to-indigo-500" },
                  { id: "file_store", label: "File Store", icon: <HardDrive className="size-6" />, color: "from-emerald-500 to-teal-500" },
                  { id: "api", label: "API", icon: <Plug className="size-6" />, color: "from-purple-500 to-pink-500" },
                ].map((type) => (
                  <button
                    key={type.id}
                    onClick={() => setSourceType(type.id as "database" | "file_store" | "api")}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      sourceType === type.id
                        ? "border-primary bg-primary/5"
                        : "border-transparent bg-muted/50 hover:bg-muted"
                    }`}
                  >
                    <div className={`p-3 rounded-lg bg-gradient-to-br ${type.color} text-white w-fit mx-auto mb-3`}>
                      {type.icon}
                    </div>
                    <p className="font-medium text-center">{type.label}</p>
                  </button>
                ))}
              </div>

              {sourceType === "database" && (
                <div className="mt-6">
                  <Label className="text-sm text-muted-foreground mb-3 block">Select Database Type</Label>
                  <div className="grid grid-cols-4 gap-2">
                    {DATABASE_TYPES.map((db) => (
                      <button
                        key={db.id}
                        onClick={() => setDatabaseType(db.id)}
                        className={`p-3 rounded-lg border transition-all text-center ${
                          databaseType === db.id
                            ? "border-primary bg-primary/5"
                            : "border-transparent bg-muted/50 hover:bg-muted"
                        }`}
                      >
                        <div className={`p-2 rounded-md bg-gradient-to-br ${db.color} text-white w-fit mx-auto mb-2`}>
                          {db.icon}
                        </div>
                        <p className="text-xs font-medium">{db.name}</p>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Step 2: Connection Configuration */}
          {step === "config" && (
            <ScrollArea className="h-[350px] pr-4">
              <div className="space-y-4">
                {sourceType === "database" && selectedDbConfig ? (
                  <>
                    <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50 mb-4">
                      <div className={`p-2 rounded-md bg-gradient-to-br ${selectedDbConfig.color} text-white`}>
                        {selectedDbConfig.icon}
                      </div>
                      <div>
                        <p className="font-medium">{selectedDbConfig.name}</p>
                        <p className="text-sm text-muted-foreground">{selectedDbConfig.description}</p>
                      </div>
                    </div>

                    {selectedDbConfig.fields.map((field) => (
                      <div key={field.name} className="space-y-2">
                        <Label htmlFor={field.name}>
                          {field.label}
                          {field.required && <span className="text-destructive ml-1">*</span>}
                        </Label>
                        {field.type === "boolean" ? (
                          <div className="flex items-center gap-2">
                            <Switch
                              id={field.name}
                              checked={!!connectionFields[field.name]}
                              onCheckedChange={(checked) =>
                                setConnectionFields({ ...connectionFields, [field.name]: checked })
                              }
                            />
                            <span className="text-sm text-muted-foreground">
                              {connectionFields[field.name] ? "Enabled" : "Disabled"}
                            </span>
                          </div>
                        ) : field.type === "textarea" ? (
                          <Textarea
                            id={field.name}
                            placeholder={field.placeholder}
                            value={(connectionFields[field.name] as string) || ""}
                            onChange={(e) =>
                              setConnectionFields({ ...connectionFields, [field.name]: e.target.value })
                            }
                            rows={4}
                            className="font-mono text-sm"
                          />
                        ) : (
                          <Input
                            id={field.name}
                            type={field.type === "password" ? "password" : field.type === "number" ? "number" : "text"}
                            placeholder={field.placeholder}
                            value={(connectionFields[field.name] as string | number) || ""}
                            onChange={(e) =>
                              setConnectionFields({
                                ...connectionFields,
                                [field.name]: field.type === "number" ? Number(e.target.value) : e.target.value,
                              })
                            }
                          />
                        )}
                        {field.description && (
                          <p className="text-xs text-muted-foreground">{field.description}</p>
                        )}
                      </div>
                    ))}
                  </>
                ) : sourceType === "file_store" ? (
                  <div className="space-y-4">
                    <div className="grid gap-2">
                      <Label>Storage Type</Label>
                      <Select
                        value={(connectionFields.storage_type as string) || "s3"}
                        onValueChange={(v) => setConnectionFields({ ...connectionFields, storage_type: v })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="s3">Amazon S3 / MinIO</SelectItem>
                          <SelectItem value="gcs">Google Cloud Storage</SelectItem>
                          <SelectItem value="azure">Azure Blob Storage</SelectItem>
                          <SelectItem value="local">Local Filesystem</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="grid gap-2">
                      <Label>Endpoint / Path</Label>
                      <Input
                        placeholder="https://s3.amazonaws.com or /path/to/files"
                        value={(connectionFields.endpoint as string) || ""}
                        onChange={(e) => setConnectionFields({ ...connectionFields, endpoint: e.target.value })}
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label>Bucket / Container</Label>
                      <Input
                        placeholder="my-bucket"
                        value={(connectionFields.bucket as string) || ""}
                        onChange={(e) => setConnectionFields({ ...connectionFields, bucket: e.target.value })}
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label>Access Key</Label>
                      <Input
                        placeholder="AKIAIOSFODNN7EXAMPLE"
                        value={(connectionFields.access_key as string) || ""}
                        onChange={(e) => setConnectionFields({ ...connectionFields, access_key: e.target.value })}
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label>Secret Key</Label>
                      <Input
                        type="password"
                        placeholder="••••••••"
                        value={(connectionFields.secret_key as string) || ""}
                        onChange={(e) => setConnectionFields({ ...connectionFields, secret_key: e.target.value })}
                      />
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="grid gap-2">
                      <Label>Base URL *</Label>
                      <Input
                        placeholder="https://api.example.com/v1"
                        value={(connectionFields.base_url as string) || ""}
                        onChange={(e) => setConnectionFields({ ...connectionFields, base_url: e.target.value })}
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label>Authentication Type</Label>
                      <Select
                        value={(connectionFields.auth_type as string) || "none"}
                        onValueChange={(v) => setConnectionFields({ ...connectionFields, auth_type: v })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="none">None</SelectItem>
                          <SelectItem value="api_key">API Key</SelectItem>
                          <SelectItem value="bearer">Bearer Token</SelectItem>
                          <SelectItem value="basic">Basic Auth</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    {connectionFields.auth_type === "api_key" && (
                      <>
                        <div className="grid gap-2">
                          <Label>API Key Header</Label>
                          <Input
                            placeholder="X-API-Key"
                            value={(connectionFields.api_key_header as string) || ""}
                            onChange={(e) => setConnectionFields({ ...connectionFields, api_key_header: e.target.value })}
                          />
                        </div>
                        <div className="grid gap-2">
                          <Label>API Key</Label>
                          <Input
                            type="password"
                            placeholder="••••••••"
                            value={(connectionFields.api_key as string) || ""}
                            onChange={(e) => setConnectionFields({ ...connectionFields, api_key: e.target.value })}
                          />
                        </div>
                      </>
                    )}
                    {connectionFields.auth_type === "bearer" && (
                      <div className="grid gap-2">
                        <Label>Bearer Token</Label>
                        <Input
                          type="password"
                          placeholder="••••••••"
                          value={(connectionFields.bearer_token as string) || ""}
                          onChange={(e) => setConnectionFields({ ...connectionFields, bearer_token: e.target.value })}
                        />
                      </div>
                    )}
                    {connectionFields.auth_type === "basic" && (
                      <>
                        <div className="grid gap-2">
                          <Label>Username</Label>
                          <Input
                            placeholder="username"
                            value={(connectionFields.username as string) || ""}
                            onChange={(e) => setConnectionFields({ ...connectionFields, username: e.target.value })}
                          />
                        </div>
                        <div className="grid gap-2">
                          <Label>Password</Label>
                          <Input
                            type="password"
                            placeholder="••••••••"
                            value={(connectionFields.password as string) || ""}
                            onChange={(e) => setConnectionFields({ ...connectionFields, password: e.target.value })}
                          />
                        </div>
                      </>
                    )}
                  </div>
                )}
              </div>
            </ScrollArea>
          )}

          {/* Step 3: Details */}
          {step === "details" && (
            <div className="space-y-4">
              <div className="grid gap-2">
                <Label htmlFor="name">Name *</Label>
                <Input
                  id="name"
                  placeholder="My Database Connection"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  placeholder="Brief description of this data source..."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label>Scope</Label>
                  <Select
                    value={formData.is_global ? "global" : "project"}
                    onValueChange={(v) =>
                      setFormData({
                        ...formData,
                        is_global: v === "global",
                        project_id: v === "global" ? "" : formData.project_id,
                      })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="global">
                        <div className="flex items-center gap-2">
                          <Globe className="size-4" />
                          Global
                        </div>
                      </SelectItem>
                      <SelectItem value="project">
                        <div className="flex items-center gap-2">
                          <FolderClosed className="size-4" />
                          Project
                        </div>
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {!formData.is_global && (
                  <div className="grid gap-2">
                    <Label>Project</Label>
                    <Select
                      value={formData.project_id}
                      onValueChange={(v) => setFormData({ ...formData, project_id: v })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select project..." />
                      </SelectTrigger>
                      <SelectContent>
                        {projects?.items.map((project) => (
                          <SelectItem key={project.id} value={project.id}>
                            {project.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Step 4: Test & Create */}
          {step === "test" && (
            <div className="space-y-6">
              {/* Summary */}
              <div className="p-4 rounded-lg border bg-muted/30">
                <h4 className="font-medium mb-3">Connection Summary</h4>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-muted-foreground">Name:</span>
                    <span className="ml-2 font-medium">{formData.name}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Type:</span>
                    <span className="ml-2 font-medium capitalize">{sourceType.replace("_", " ")}</span>
                  </div>
                  {sourceType === "database" && (
                    <div>
                      <span className="text-muted-foreground">Database:</span>
                      <span className="ml-2 font-medium">{selectedDbConfig?.name}</span>
                    </div>
                  )}
                  <div>
                    <span className="text-muted-foreground">Scope:</span>
                    <span className="ml-2 font-medium">{formData.is_global ? "Global" : "Project"}</span>
                  </div>
                </div>
              </div>

              {/* Test Connection */}
              <div className="text-center py-4">
                <Button
                  variant="outline"
                  size="lg"
                  onClick={handleTestConnection}
                  disabled={isTesting}
                  className="gap-2"
                >
                  {isTesting ? (
                    <>
                      <Loader2 className="size-4 animate-spin" />
                      Testing Connection...
                    </>
                  ) : (
                    <>
                      <RefreshCw className="size-4" />
                      Test Connection
                    </>
                  )}
                </Button>

                {testResult && (
                  <div
                    className={`mt-4 p-4 rounded-lg flex items-center gap-3 ${
                      testResult.success
                        ? "bg-green-500/10 text-green-600 border border-green-500/20"
                        : "bg-red-500/10 text-red-600 border border-red-500/20"
                    }`}
                  >
                    {testResult.success ? (
                      <CheckCircle2 className="size-5" />
                    ) : (
                      <XCircle className="size-5" />
                    )}
                    <span>{testResult.message}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        <DialogFooter className="flex justify-between">
          <div>
            {step !== "type" && (
              <Button variant="outline" onClick={prevStep}>
                <ChevronLeft className="size-4 mr-1" />
                Back
              </Button>
            )}
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            {step === "test" ? (
              <Button onClick={handleSubmit} disabled={isSubmitting}>
                {isSubmitting ? (
                  <>
                    <Loader2 className="size-4 mr-2 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Plus className="size-4 mr-2" />
                    Create Data Source
                  </>
                )}
              </Button>
            ) : (
              <Button onClick={nextStep} disabled={!canProceed()}>
                Next
                <ChevronRight className="size-4 ml-1" />
              </Button>
            )}
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default function DataSourcesPage() {
  const [typeFilter, setTypeFilter] = React.useState<string>("all");
  const [scopeFilter, setScopeFilter] = React.useState<string>("all");
  const [searchQuery, setSearchQuery] = React.useState("");
  const [createDialogOpen, setCreateDialogOpen] = React.useState(false);
  const [testingIds, setTestingIds] = React.useState<Set<string>>(new Set());
  const [schemaBrowserOpen, setSchemaBrowserOpen] = React.useState(false);
  const [selectedDataSource, setSelectedDataSource] = React.useState<DataSource | null>(null);

  const { data, isLoading, mutate } = useDataSources({
    source_type: typeFilter === "all" ? undefined : typeFilter,
    is_global: scopeFilter === "all" ? undefined : scopeFilter === "global",
  });

  const handleViewSchema = (dataSource: DataSource) => {
    setSelectedDataSource(dataSource);
    setSchemaBrowserOpen(true);
  };

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8080/api/v1/datasources/${id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        toast.success(`Data source "${name}" deleted`);
        mutate();
      } else {
        toast.error("Failed to delete data source");
      }
    } catch (error) {
      toast.error("Failed to delete data source");
    }
  };

  const handleTest = async (id: string) => {
    setTestingIds(prev => new Set([...prev, id]));
    try {
      const response = await fetch(`http://localhost:8080/api/v1/datasources/${id}/test`, {
        method: 'POST',
      });

      const result = await response.json();
      if (result.success) {
        toast.success("Connection successful");
      } else {
        toast.error(result.message || "Connection failed");
      }
      mutate();
    } catch (error) {
      toast.error("Failed to test connection");
    } finally {
      setTestingIds(prev => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  };

  const handlePromote = async (id: string, name: string) => {
    if (!confirm(`Promote "${name}" to a global data source?`)) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8080/api/v1/datasources/${id}/promote`, {
        method: 'POST',
      });

      if (response.ok) {
        toast.success(`"${name}" is now a global data source`);
        mutate();
      } else {
        toast.error("Failed to promote data source");
      }
    } catch (error) {
      toast.error("Failed to promote data source");
    }
  };

  const filteredDataSources = React.useMemo(() => {
    if (!data?.items) return [];
    if (!searchQuery) return data.items;

    const query = searchQuery.toLowerCase();
    return data.items.filter(
      (ds) =>
        ds.name.toLowerCase().includes(query) ||
        ds.description.toLowerCase().includes(query) ||
        ds.tags.some((t) => t.toLowerCase().includes(query))
    );
  }, [data?.items, searchQuery]);

  const globalSources = filteredDataSources.filter(ds => ds.is_global);
  const projectSources = filteredDataSources.filter(ds => !ds.is_global);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Data Sources</h1>
          <p className="text-muted-foreground">
            Manage database connections, file stores, and API integrations
          </p>
        </div>
        <Button onClick={() => setCreateDialogOpen(true)}>
          <Plus className="size-4 mr-2" />
          New Data Source
        </Button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Sources</p>
                <p className="text-2xl font-bold">{data?.total || 0}</p>
              </div>
              <Database className="size-8 text-muted-foreground/30" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Global Sources</p>
                <p className="text-2xl font-bold">{globalSources.length}</p>
              </div>
              <Globe className="size-8 text-muted-foreground/30" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Connected</p>
                <p className="text-2xl font-bold text-green-500">
                  {filteredDataSources.filter(ds => ds.last_test_success).length}
                </p>
              </div>
              <CheckCircle2 className="size-8 text-green-500/30" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Databases</p>
                <p className="text-2xl font-bold">
                  {filteredDataSources.filter(ds => ds.source_type === 'database').length}
                </p>
              </div>
              <Table2 className="size-8 text-muted-foreground/30" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
          <Input
            placeholder="Search data sources..."
            className="pl-9"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="w-40">
            <Filter className="size-4 mr-2" />
            <SelectValue placeholder="Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            <SelectItem value="database">Database</SelectItem>
            <SelectItem value="file_store">File Store</SelectItem>
            <SelectItem value="api">API</SelectItem>
          </SelectContent>
        </Select>
        <Select value={scopeFilter} onValueChange={setScopeFilter}>
          <SelectTrigger className="w-40">
            <Globe className="size-4 mr-2" />
            <SelectValue placeholder="Scope" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Scopes</SelectItem>
            <SelectItem value="global">Global</SelectItem>
            <SelectItem value="project">Project</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Tabs for Global vs Project */}
      <Tabs defaultValue="all" className="space-y-4">
        <TabsList>
          <TabsTrigger value="all">All ({filteredDataSources.length})</TabsTrigger>
          <TabsTrigger value="global">Global ({globalSources.length})</TabsTrigger>
          <TabsTrigger value="project">Project ({projectSources.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="all">
          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <Card key={i}>
                  <CardHeader>
                    <Skeleton className="h-6 w-3/4" />
                    <Skeleton className="h-4 w-1/2" />
                  </CardHeader>
                  <CardContent>
                    <Skeleton className="h-4 w-1/4" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : filteredDataSources.length === 0 ? (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-12">
                  <Database className="size-12 mx-auto mb-4 opacity-50" />
                  <h3 className="text-lg font-semibold mb-2">No data sources found</h3>
                  <p className="text-muted-foreground mb-4">
                    {searchQuery
                      ? "Try a different search term"
                      : "Create your first data source to connect to databases, file stores, or APIs"}
                  </p>
                  {!searchQuery && (
                    <Button onClick={() => setCreateDialogOpen(true)}>
                      <Plus className="size-4 mr-2" />
                      Create Data Source
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredDataSources.map((ds) => (
                <DataSourceCard
                  key={ds.id}
                  dataSource={ds}
                  onDelete={() => handleDelete(ds.id, ds.name)}
                  onTest={() => handleTest(ds.id)}
                  onPromote={() => handlePromote(ds.id, ds.name)}
                  onViewSchema={() => handleViewSchema(ds)}
                  isTestingConnection={testingIds.has(ds.id)}
                />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="global">
          {globalSources.length === 0 ? (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-12">
                  <Globe className="size-12 mx-auto mb-4 opacity-50" />
                  <h3 className="text-lg font-semibold mb-2">No global data sources</h3>
                  <p className="text-muted-foreground mb-4">
                    Global data sources are available to all projects
                  </p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {globalSources.map((ds) => (
                <DataSourceCard
                  key={ds.id}
                  dataSource={ds}
                  onDelete={() => handleDelete(ds.id, ds.name)}
                  onTest={() => handleTest(ds.id)}
                  onPromote={() => handlePromote(ds.id, ds.name)}
                  onViewSchema={() => handleViewSchema(ds)}
                  isTestingConnection={testingIds.has(ds.id)}
                />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="project">
          {projectSources.length === 0 ? (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-12">
                  <FolderClosed className="size-12 mx-auto mb-4 opacity-50" />
                  <h3 className="text-lg font-semibold mb-2">No project data sources</h3>
                  <p className="text-muted-foreground mb-4">
                    Project-scoped data sources are only available within their associated project
                  </p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {projectSources.map((ds) => (
                <DataSourceCard
                  key={ds.id}
                  dataSource={ds}
                  onDelete={() => handleDelete(ds.id, ds.name)}
                  onTest={() => handleTest(ds.id)}
                  onPromote={() => handlePromote(ds.id, ds.name)}
                  onViewSchema={() => handleViewSchema(ds)}
                  isTestingConnection={testingIds.has(ds.id)}
                />
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Create Dialog */}
      <CreateDataSourceDialog 
        open={createDialogOpen} 
        onOpenChange={setCreateDialogOpen}
        onCreated={() => mutate()}
      />

      {/* Schema Browser Dialog */}
      {selectedDataSource && (
        <SchemaBrowserDialog
          dataSourceId={selectedDataSource.id}
          dataSourceName={selectedDataSource.name}
          open={schemaBrowserOpen}
          onOpenChange={setSchemaBrowserOpen}
        />
      )}
    </div>
  );
}



