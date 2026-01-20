"use client";

import * as React from "react";
import {
  Database,
  ChevronRight,
  ChevronLeft,
  Check,
  AlertCircle,
  Loader2,
  Copy,
  Eye,
  EyeOff,
  Table,
  Columns,
  Key,
  RefreshCw,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";

// Database driver configurations
const DATABASE_DRIVERS = {
  postgresql: {
    name: "PostgreSQL",
    icon: "🐘",
    defaultPort: 5432,
    fields: ["host", "port", "database", "username", "password", "ssl"],
    connectionString: (config: Record<string, string>) =>
      `postgresql://${config.username}:****@${config.host}:${config.port}/${config.database}`,
  },
  mysql: {
    name: "MySQL",
    icon: "🐬",
    defaultPort: 3306,
    fields: ["host", "port", "database", "username", "password", "ssl"],
    connectionString: (config: Record<string, string>) =>
      `mysql://${config.username}:****@${config.host}:${config.port}/${config.database}`,
  },
  mongodb: {
    name: "MongoDB",
    icon: "🍃",
    defaultPort: 27017,
    fields: ["host", "port", "database", "username", "password", "replica_set", "auth_source"],
    connectionString: (config: Record<string, string>) =>
      `mongodb://${config.username}:****@${config.host}:${config.port}/${config.database}`,
  },
  redis: {
    name: "Redis",
    icon: "🔴",
    defaultPort: 6379,
    fields: ["host", "port", "database", "password", "ssl"],
    connectionString: (config: Record<string, string>) =>
      `redis://${config.host}:${config.port}/${config.database || 0}`,
  },
  elasticsearch: {
    name: "Elasticsearch",
    icon: "🔍",
    defaultPort: 9200,
    fields: ["host", "port", "username", "password", "ssl", "api_key"],
    connectionString: (config: Record<string, string>) =>
      `${config.ssl ? 'https' : 'http'}://${config.host}:${config.port}`,
  },
  bigquery: {
    name: "BigQuery",
    icon: "☁️",
    defaultPort: 0,
    fields: ["project_id", "dataset", "credentials_file"],
    connectionString: (config: Record<string, string>) =>
      `bigquery://${config.project_id}/${config.dataset || ''}`,
  },
  snowflake: {
    name: "Snowflake",
    icon: "❄️",
    defaultPort: 443,
    fields: ["account", "warehouse", "database", "schema", "username", "password", "role"],
    connectionString: (config: Record<string, string>) =>
      `snowflake://${config.account}/${config.database}/${config.schema}`,
  },
  sqlite: {
    name: "SQLite",
    icon: "📁",
    defaultPort: 0,
    fields: ["database_path"],
    connectionString: (config: Record<string, string>) =>
      `sqlite:///${config.database_path}`,
  },
};

type DriverKey = keyof typeof DATABASE_DRIVERS;

interface ConnectionConfig {
  driver: DriverKey;
  host: string;
  port: string;
  database: string;
  username: string;
  password: string;
  ssl: boolean;
  [key: string]: string | boolean;
}

interface SchemaTable {
  name: string;
  columns: Array<{
    name: string;
    data_type: string;
    nullable: boolean;
    primary_key: boolean;
  }>;
  row_count?: number;
}

interface DatabaseWizardProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onComplete: (data: {
    name: string;
    driver: string;
    connection_config: Record<string, unknown>;
    description: string;
  }) => void;
  initialConfig?: Partial<ConnectionConfig>;
}

export function DatabaseWizard({
  open,
  onOpenChange,
  onComplete,
  initialConfig,
}: DatabaseWizardProps) {
  const [step, setStep] = React.useState(1);
  const [showPassword, setShowPassword] = React.useState(false);
  const [isTestingConnection, setIsTestingConnection] = React.useState(false);
  const [testResult, setTestResult] = React.useState<{
    success: boolean;
    message: string;
    latency_ms?: number;
  } | null>(null);
  const [discoveredSchema, setDiscoveredSchema] = React.useState<SchemaTable[] | null>(null);
  const [isDiscoveringSchema, setIsDiscoveringSchema] = React.useState(false);

  const [config, setConfig] = React.useState<ConnectionConfig>({
    driver: "postgresql",
    host: "localhost",
    port: "5432",
    database: "",
    username: "",
    password: "",
    ssl: false,
    ...initialConfig,
  });

  const [metadata, setMetadata] = React.useState({
    name: "",
    description: "",
  });

  const currentDriver = DATABASE_DRIVERS[config.driver];

  const handleDriverChange = (driver: DriverKey) => {
    const driverConfig = DATABASE_DRIVERS[driver];
    setConfig((prev) => ({
      ...prev,
      driver,
      port: String(driverConfig.defaultPort),
    }));
    setTestResult(null);
    setDiscoveredSchema(null);
  };

  const handleConfigChange = (field: string, value: string | boolean) => {
    setConfig((prev) => ({ ...prev, [field]: value }));
    setTestResult(null);
  };

  const handleTestConnection = async () => {
    setIsTestingConnection(true);
    setTestResult(null);

    try {
      // Build connection config
      const connectionConfig: Record<string, unknown> = {
        driver: config.driver,
        host: config.host,
        port: parseInt(config.port) || undefined,
        database: config.database,
        username: config.username,
        password: config.password,
        ssl: config.ssl,
      };

      // Add driver-specific fields
      Object.entries(config).forEach(([key, value]) => {
        if (value && !["driver", "host", "port", "database", "username", "password", "ssl"].includes(key)) {
          connectionConfig[key] = value;
        }
      });

      const response = await fetch("http://localhost:8080/api/v1/datasources/test-connection", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source_type: "database",
          connection_config: connectionConfig,
        }),
      });

      const result = await response.json();
      setTestResult({
        success: result.success,
        message: result.message,
        latency_ms: result.latency_ms,
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
      setIsTestingConnection(false);
    }
  };

  const handleDiscoverSchema = async () => {
    setIsDiscoveringSchema(true);

    try {
      const connectionConfig: Record<string, unknown> = {
        driver: config.driver,
        host: config.host,
        port: parseInt(config.port) || undefined,
        database: config.database,
        username: config.username,
        password: config.password,
      };

      const response = await fetch("http://localhost:8080/api/v1/datasources/discover-schema", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source_type: "database",
          connection_config: connectionConfig,
        }),
      });

      const result = await response.json();
      if (result.tables) {
        setDiscoveredSchema(result.tables);
        toast.success(`Discovered ${result.tables.length} tables`);
      }
    } catch (error) {
      toast.error("Failed to discover schema");
    } finally {
      setIsDiscoveringSchema(false);
    }
  };

  const handleComplete = () => {
    const connectionConfig: Record<string, unknown> = {
      driver: config.driver,
      host: config.host,
      port: parseInt(config.port) || undefined,
      database: config.database,
      username: config.username,
      password: config.password,
      ssl: config.ssl,
    };

    // Add driver-specific fields
    Object.entries(config).forEach(([key, value]) => {
      if (value && !["driver", "host", "port", "database", "username", "password", "ssl"].includes(key)) {
        connectionConfig[key] = value;
      }
    });

    onComplete({
      name: metadata.name || `${currentDriver.name} - ${config.database || config.host}`,
      driver: config.driver,
      connection_config: connectionConfig,
      description: metadata.description,
    });

    // Reset state
    setStep(1);
    setTestResult(null);
    setDiscoveredSchema(null);
    onOpenChange(false);
  };

  const canProceed = () => {
    switch (step) {
      case 1:
        return config.driver;
      case 2:
        if (config.driver === "sqlite") return !!config.database;
        if (config.driver === "bigquery") return !!config.project_id;
        return config.host && config.database;
      case 3:
        return testResult?.success;
      case 4:
        return metadata.name;
      default:
        return false;
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Database className="size-5" />
            Database Connection Wizard
          </DialogTitle>
          <DialogDescription>
            Step {step} of 4: {
              step === 1 ? "Select Database Type" :
              step === 2 ? "Configure Connection" :
              step === 3 ? "Test & Discover" :
              "Finalize"
            }
          </DialogDescription>
        </DialogHeader>

        {/* Progress Steps */}
        <div className="flex items-center justify-between mb-4">
          {[1, 2, 3, 4].map((s) => (
            <div key={s} className="flex items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  s === step
                    ? "bg-primary text-primary-foreground"
                    : s < step
                    ? "bg-green-500 text-white"
                    : "bg-muted text-muted-foreground"
                }`}
              >
                {s < step ? <Check className="size-4" /> : s}
              </div>
              {s < 4 && (
                <div
                  className={`w-16 h-1 mx-2 ${
                    s < step ? "bg-green-500" : "bg-muted"
                  }`}
                />
              )}
            </div>
          ))}
        </div>

        {/* Step 1: Select Driver */}
        {step === 1 && (
          <div className="grid grid-cols-2 gap-3">
            {Object.entries(DATABASE_DRIVERS).map(([key, driver]) => (
              <Card
                key={key}
                className={`cursor-pointer transition-all ${
                  config.driver === key
                    ? "border-primary ring-2 ring-primary/20"
                    : "hover:border-muted-foreground/50"
                }`}
                onClick={() => handleDriverChange(key as DriverKey)}
              >
                <CardContent className="p-4 flex items-center gap-3">
                  <span className="text-2xl">{driver.icon}</span>
                  <div>
                    <p className="font-medium">{driver.name}</p>
                    <p className="text-xs text-muted-foreground">
                      Port {driver.defaultPort || "N/A"}
                    </p>
                  </div>
                  {config.driver === key && (
                    <Check className="ml-auto size-5 text-primary" />
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Step 2: Configure Connection */}
        {step === 2 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-2xl">{currentDriver.icon}</span>
              <span className="font-medium">{currentDriver.name}</span>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {currentDriver.fields.includes("host") && (
                <div className="space-y-2">
                  <Label htmlFor="host">Host</Label>
                  <Input
                    id="host"
                    placeholder="localhost"
                    value={config.host}
                    onChange={(e) => handleConfigChange("host", e.target.value)}
                  />
                </div>
              )}

              {currentDriver.fields.includes("port") && (
                <div className="space-y-2">
                  <Label htmlFor="port">Port</Label>
                  <Input
                    id="port"
                    placeholder={String(currentDriver.defaultPort)}
                    value={config.port}
                    onChange={(e) => handleConfigChange("port", e.target.value)}
                  />
                </div>
              )}

              {currentDriver.fields.includes("database") && (
                <div className="space-y-2">
                  <Label htmlFor="database">Database</Label>
                  <Input
                    id="database"
                    placeholder="mydb"
                    value={config.database}
                    onChange={(e) => handleConfigChange("database", e.target.value)}
                  />
                </div>
              )}

              {currentDriver.fields.includes("database_path") && (
                <div className="space-y-2 col-span-2">
                  <Label htmlFor="database_path">Database Path</Label>
                  <Input
                    id="database_path"
                    placeholder="/path/to/database.db"
                    value={config.database_path as string || ""}
                    onChange={(e) => handleConfigChange("database_path", e.target.value)}
                  />
                </div>
              )}

              {currentDriver.fields.includes("username") && (
                <div className="space-y-2">
                  <Label htmlFor="username">Username</Label>
                  <Input
                    id="username"
                    placeholder="user"
                    value={config.username}
                    onChange={(e) => handleConfigChange("username", e.target.value)}
                  />
                </div>
              )}

              {currentDriver.fields.includes("password") && (
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      value={config.password}
                      onChange={(e) => handleConfigChange("password", e.target.value)}
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      className="absolute right-0 top-0"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? (
                        <EyeOff className="size-4" />
                      ) : (
                        <Eye className="size-4" />
                      )}
                    </Button>
                  </div>
                </div>
              )}

              {currentDriver.fields.includes("project_id") && (
                <div className="space-y-2">
                  <Label htmlFor="project_id">Project ID</Label>
                  <Input
                    id="project_id"
                    placeholder="my-gcp-project"
                    value={config.project_id as string || ""}
                    onChange={(e) => handleConfigChange("project_id", e.target.value)}
                  />
                </div>
              )}

              {currentDriver.fields.includes("account") && (
                <div className="space-y-2">
                  <Label htmlFor="account">Account</Label>
                  <Input
                    id="account"
                    placeholder="xy12345.us-east-1"
                    value={config.account as string || ""}
                    onChange={(e) => handleConfigChange("account", e.target.value)}
                  />
                </div>
              )}

              {currentDriver.fields.includes("warehouse") && (
                <div className="space-y-2">
                  <Label htmlFor="warehouse">Warehouse</Label>
                  <Input
                    id="warehouse"
                    placeholder="COMPUTE_WH"
                    value={config.warehouse as string || ""}
                    onChange={(e) => handleConfigChange("warehouse", e.target.value)}
                  />
                </div>
              )}
            </div>

            {/* Connection String Preview */}
            <div className="mt-4 p-3 bg-muted rounded-lg">
              <div className="flex items-center justify-between mb-1">
                <Label className="text-xs text-muted-foreground">Connection String</Label>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    navigator.clipboard.writeText(currentDriver.connectionString(config as Record<string, string>));
                    toast.success("Copied to clipboard");
                  }}
                >
                  <Copy className="size-3 mr-1" />
                  Copy
                </Button>
              </div>
              <code className="text-xs break-all">
                {currentDriver.connectionString(config as Record<string, string>)}
              </code>
            </div>
          </div>
        )}

        {/* Step 3: Test & Discover */}
        {step === 3 && (
          <div className="space-y-4">
            {/* Test Connection */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm">Connection Test</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-4">
                  <Button
                    onClick={handleTestConnection}
                    disabled={isTestingConnection}
                  >
                    {isTestingConnection ? (
                      <Loader2 className="size-4 mr-2 animate-spin" />
                    ) : (
                      <RefreshCw className="size-4 mr-2" />
                    )}
                    Test Connection
                  </Button>

                  {testResult && (
                    <div className={`flex items-center gap-2 ${
                      testResult.success ? "text-green-500" : "text-red-500"
                    }`}>
                      {testResult.success ? (
                        <Check className="size-4" />
                      ) : (
                        <AlertCircle className="size-4" />
                      )}
                      <span className="text-sm">{testResult.message}</span>
                      {testResult.latency_ms && (
                        <Badge variant="secondary" className="text-xs">
                          {testResult.latency_ms.toFixed(0)}ms
                        </Badge>
                      )}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Schema Discovery */}
            {testResult?.success && (
              <Card>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm">Schema Discovery</CardTitle>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleDiscoverSchema}
                      disabled={isDiscoveringSchema}
                    >
                      {isDiscoveringSchema ? (
                        <Loader2 className="size-4 mr-2 animate-spin" />
                      ) : (
                        <Table className="size-4 mr-2" />
                      )}
                      Discover Schema
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  {discoveredSchema ? (
                    <ScrollArea className="h-48">
                      <div className="space-y-2">
                        {discoveredSchema.map((table) => (
                          <div
                            key={table.name}
                            className="p-2 border rounded-lg"
                          >
                            <div className="flex items-center gap-2 mb-1">
                              <Table className="size-4 text-muted-foreground" />
                              <span className="font-medium">{table.name}</span>
                              {table.row_count !== undefined && (
                                <Badge variant="secondary" className="text-xs">
                                  {table.row_count.toLocaleString()} rows
                                </Badge>
                              )}
                            </div>
                            <div className="flex flex-wrap gap-1 ml-6">
                              {table.columns.slice(0, 5).map((col) => (
                                <Badge
                                  key={col.name}
                                  variant="outline"
                                  className="text-xs gap-1"
                                >
                                  {col.primary_key && <Key className="size-3" />}
                                  <Columns className="size-3" />
                                  {col.name}
                                  <span className="text-muted-foreground">
                                    ({col.data_type})
                                  </span>
                                </Badge>
                              ))}
                              {table.columns.length > 5 && (
                                <Badge variant="secondary" className="text-xs">
                                  +{table.columns.length - 5} more
                                </Badge>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </ScrollArea>
                  ) : (
                    <p className="text-sm text-muted-foreground">
                      Click &quot;Discover Schema&quot; to preview tables and columns
                    </p>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* Step 4: Finalize */}
        {step === 4 && (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Data Source Name *</Label>
              <Input
                id="name"
                placeholder={`${currentDriver.name} - ${config.database || config.host}`}
                value={metadata.name}
                onChange={(e) => setMetadata({ ...metadata, name: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                placeholder="Brief description of this data source..."
                value={metadata.description}
                onChange={(e) => setMetadata({ ...metadata, description: e.target.value })}
                rows={3}
              />
            </div>

            {/* Summary */}
            <Card className="bg-muted/50">
              <CardContent className="pt-4">
                <h4 className="font-medium mb-2">Connection Summary</h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">Driver:</span>
                    <span>{currentDriver.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">Host:</span>
                    <span>{config.host || "N/A"}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">Database:</span>
                    <span>{config.database || "N/A"}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">Status:</span>
                    <Badge className="bg-green-500 text-white">Connected</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        <DialogFooter className="flex justify-between">
          <Button
            variant="outline"
            onClick={() => setStep((s) => Math.max(1, s - 1))}
            disabled={step === 1}
          >
            <ChevronLeft className="size-4 mr-1" />
            Back
          </Button>

          {step < 4 ? (
            <Button
              onClick={() => setStep((s) => s + 1)}
              disabled={!canProceed()}
            >
              Next
              <ChevronRight className="size-4 ml-1" />
            </Button>
          ) : (
            <Button onClick={handleComplete} disabled={!canProceed()}>
              <Check className="size-4 mr-1" />
              Create Data Source
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// Schema Browser Component
interface SchemaBrowserProps {
  sourceId: string;
  onTableSelect?: (table: string) => void;
}

export function SchemaBrowser({ sourceId, onTableSelect }: SchemaBrowserProps) {
  const [schema, setSchema] = React.useState<SchemaTable[] | null>(null);
  const [isLoading, setIsLoading] = React.useState(false);
  const [selectedTable, setSelectedTable] = React.useState<string | null>(null);
  const [searchQuery, setSearchQuery] = React.useState("");

  const loadSchema = React.useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8080/api/v1/datasources/${sourceId}/schema`
      );
      const data = await response.json();
      if (data.tables) {
        setSchema(data.tables);
      }
    } catch (error) {
      toast.error("Failed to load schema");
    } finally {
      setIsLoading(false);
    }
  }, [sourceId]);

  React.useEffect(() => {
    if (sourceId) {
      loadSchema();
    }
  }, [sourceId, loadSchema]);

  const filteredTables = React.useMemo(() => {
    if (!schema) return [];
    if (!searchQuery) return schema;
    const query = searchQuery.toLowerCase();
    return schema.filter(
      (t) =>
        t.name.toLowerCase().includes(query) ||
        t.columns.some((c) => c.name.toLowerCase().includes(query))
    );
  }, [schema, searchQuery]);

  const selectedTableData = selectedTable
    ? schema?.find((t) => t.name === selectedTable)
    : null;

  return (
    <div className="flex h-[400px] border rounded-lg overflow-hidden">
      {/* Table List */}
      <div className="w-1/3 border-r flex flex-col">
        <div className="p-2 border-b">
          <Input
            placeholder="Search tables..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="h-8"
          />
        </div>
        <ScrollArea className="flex-1">
          {isLoading ? (
            <div className="p-4 text-center text-muted-foreground">
              <Loader2 className="size-6 mx-auto animate-spin mb-2" />
              Loading schema...
            </div>
          ) : filteredTables.length === 0 ? (
            <div className="p-4 text-center text-muted-foreground">
              No tables found
            </div>
          ) : (
            <div className="p-1">
              {filteredTables.map((table) => (
                <button
                  key={table.name}
                  className={`w-full text-left p-2 rounded text-sm hover:bg-muted ${
                    selectedTable === table.name ? "bg-muted" : ""
                  }`}
                  onClick={() => {
                    setSelectedTable(table.name);
                    onTableSelect?.(table.name);
                  }}
                >
                  <div className="flex items-center gap-2">
                    <Table className="size-4 text-muted-foreground" />
                    <span className="truncate">{table.name}</span>
                  </div>
                  <div className="ml-6 text-xs text-muted-foreground">
                    {table.columns.length} columns
                    {table.row_count !== undefined && ` • ${table.row_count.toLocaleString()} rows`}
                  </div>
                </button>
              ))}
            </div>
          )}
        </ScrollArea>
      </div>

      {/* Column Details */}
      <div className="flex-1 flex flex-col">
        {selectedTableData ? (
          <>
            <div className="p-3 border-b bg-muted/30">
              <h3 className="font-medium">{selectedTableData.name}</h3>
              <p className="text-xs text-muted-foreground">
                {selectedTableData.columns.length} columns
              </p>
            </div>
            <ScrollArea className="flex-1">
              <table className="w-full text-sm">
                <thead className="bg-muted/50 sticky top-0">
                  <tr>
                    <th className="text-left p-2">Column</th>
                    <th className="text-left p-2">Type</th>
                    <th className="text-left p-2">Nullable</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedTableData.columns.map((column) => (
                    <tr key={column.name} className="border-b hover:bg-muted/30">
                      <td className="p-2">
                        <div className="flex items-center gap-2">
                          {column.primary_key && (
                            <Key className="size-3 text-yellow-500" />
                          )}
                          <span>{column.name}</span>
                        </div>
                      </td>
                      <td className="p-2">
                        <Badge variant="outline" className="text-xs">
                          {column.data_type}
                        </Badge>
                      </td>
                      <td className="p-2">
                        {column.nullable ? (
                          <span className="text-muted-foreground">Yes</span>
                        ) : (
                          <span className="font-medium">No</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </ScrollArea>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-muted-foreground">
            Select a table to view columns
          </div>
        )}
      </div>
    </div>
  );
}
