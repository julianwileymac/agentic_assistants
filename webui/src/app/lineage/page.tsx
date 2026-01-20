"use client";

import * as React from "react";
import {
  GitBranch,
  FileText,
  Link,
  Github,
  Cloud,
  Tag,
  Search,
  Filter,
  RefreshCw,
  ChevronRight,
  ChevronDown,
  Clock,
  CheckCircle,
  AlertCircle,
  ArrowRight,
  Layers,
  Database,
  Activity,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
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
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";

interface ProcessingStep {
  step_id: string;
  step_type: string;
  step_name: string;
  timestamp: string;
  duration_ms: number;
  config: Record<string, any>;
  metrics: Record<string, any>;
  error?: string;
}

interface DocumentLineage {
  document_id: string;
  source_uri: string;
  source_type: string;
  collection: string;
  ingestion_pipeline: string;
  ingestion_timestamp: string;
  processing_steps: ProcessingStep[];
  parent_documents: string[];
  child_documents: string[];
  tags: string[];
  metadata: Record<string, any>;
  project_id?: string;
  user_id?: string;
  version: number;
  is_deleted: boolean;
}

interface TagStats {
  tag: string;
  document_count: number;
  parent_tag?: string;
}

interface CollectionStats {
  collection: string;
  document_count: number;
  source_distribution: Record<string, number>;
  processing_steps: Record<string, number>;
  last_ingestion?: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function LineagePage() {
  const [activeTab, setActiveTab] = React.useState("documents");
  const [documents, setDocuments] = React.useState<DocumentLineage[]>([]);
  const [tagStats, setTagStats] = React.useState<TagStats[]>([]);
  const [tagHierarchy, setTagHierarchy] = React.useState<Record<string, string[]>>({});
  const [collectionStats, setCollectionStats] = React.useState<CollectionStats | null>(null);
  const [loading, setLoading] = React.useState(true);

  // Filters
  const [searchQuery, setSearchQuery] = React.useState("");
  const [selectedCollection, setSelectedCollection] = React.useState("all");
  const [selectedSourceType, setSelectedSourceType] = React.useState("all");
  const [selectedTags, setSelectedTags] = React.useState<string[]>([]);

  // Detail view
  const [selectedDocument, setSelectedDocument] = React.useState<DocumentLineage | null>(null);
  const [detailDialogOpen, setDetailDialogOpen] = React.useState(false);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const body: any = {};
      if (selectedCollection !== "all") body.collection = selectedCollection;
      if (selectedSourceType !== "all") body.source_type = selectedSourceType;
      if (selectedTags.length > 0) body.tags = selectedTags;

      const response = await fetch(`${API_URL}/api/lineage/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (response.ok) {
        setDocuments(await response.json());
      }
    } catch (error) {
      console.error("Error fetching documents:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTagStats = async () => {
    try {
      const response = await fetch(`${API_URL}/api/lineage/tags/stats`);
      if (response.ok) {
        setTagStats(await response.json());
      }
    } catch (error) {
      console.error("Error fetching tag stats:", error);
    }
  };

  const fetchTagHierarchy = async () => {
    try {
      const response = await fetch(`${API_URL}/api/lineage/tags/hierarchy`);
      if (response.ok) {
        const data = await response.json();
        setTagHierarchy(data.hierarchy || {});
      }
    } catch (error) {
      console.error("Error fetching tag hierarchy:", error);
    }
  };

  const fetchCollectionStats = async (collection: string) => {
    try {
      const response = await fetch(`${API_URL}/api/lineage/collection/${collection}/stats`);
      if (response.ok) {
        setCollectionStats(await response.json());
      }
    } catch (error) {
      console.error("Error fetching collection stats:", error);
    }
  };

  React.useEffect(() => {
    fetchDocuments();
    fetchTagStats();
    fetchTagHierarchy();
  }, [selectedCollection, selectedSourceType, selectedTags]);

  const viewDocumentDetails = async (docId: string) => {
    try {
      const response = await fetch(`${API_URL}/api/lineage/document/${docId}`);
      if (response.ok) {
        setSelectedDocument(await response.json());
        setDetailDialogOpen(true);
      }
    } catch (error) {
      toast.error(`Error: ${error}`);
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString();
  };

  const getSourceIcon = (sourceType: string) => {
    switch (sourceType) {
      case "file":
        return <FileText className="h-4 w-4" />;
      case "url":
        return <Link className="h-4 w-4" />;
      case "github":
        return <Github className="h-4 w-4" />;
      case "s3":
        return <Cloud className="h-4 w-4" />;
      default:
        return <Database className="h-4 w-4" />;
    }
  };

  const getStepIcon = (stepType: string) => {
    switch (stepType) {
      case "ingest":
        return <FileText className="h-3 w-3" />;
      case "chunk":
        return <Layers className="h-3 w-3" />;
      case "embed":
        return <Activity className="h-3 w-3" />;
      case "index":
        return <Database className="h-3 w-3" />;
      default:
        return <CheckCircle className="h-3 w-3" />;
    }
  };

  const filteredDocuments = documents.filter((doc) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      doc.source_uri.toLowerCase().includes(query) ||
      doc.document_id.toLowerCase().includes(query) ||
      doc.tags.some((t) => t.toLowerCase().includes(query))
    );
  });

  // Calculate stats
  const stats = {
    total: documents.length,
    bySource: documents.reduce((acc, doc) => {
      acc[doc.source_type] = (acc[doc.source_type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>),
    byCollection: documents.reduce((acc, doc) => {
      acc[doc.collection] = (acc[doc.collection] || 0) + 1;
      return acc;
    }, {} as Record<string, number>),
  };

  const collections = Array.from(new Set(documents.map((d) => d.collection)));

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Document Lineage</h1>
          <p className="text-muted-foreground">
            Track document provenance, processing history, and relationships
          </p>
        </div>
        <Button onClick={fetchDocuments}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Documents
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Collections
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{collections.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Tags in Use
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{tagStats.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Source Types
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Object.keys(stats.bySource).length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="documents">Documents</TabsTrigger>
          <TabsTrigger value="tags">Tags</TabsTrigger>
          <TabsTrigger value="collections">Collections</TabsTrigger>
        </TabsList>

        <TabsContent value="documents" className="space-y-4">
          {/* Filters */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    placeholder="Search documents..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <Select
                  value={selectedCollection}
                  onValueChange={setSelectedCollection}
                >
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Collection" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Collections</SelectItem>
                    {collections.map((col) => (
                      <SelectItem key={col} value={col}>
                        {col}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Select
                  value={selectedSourceType}
                  onValueChange={setSelectedSourceType}
                >
                  <SelectTrigger className="w-[150px]">
                    <SelectValue placeholder="Source" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Sources</SelectItem>
                    <SelectItem value="file">File</SelectItem>
                    <SelectItem value="url">URL</SelectItem>
                    <SelectItem value="github">GitHub</SelectItem>
                    <SelectItem value="s3">S3</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Documents Table */}
          <Card>
            <CardHeader>
              <CardTitle>Document Lineage</CardTitle>
              <CardDescription>
                {filteredDocuments.length} documents tracked
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Source</TableHead>
                    <TableHead>Collection</TableHead>
                    <TableHead>Processing Steps</TableHead>
                    <TableHead>Tags</TableHead>
                    <TableHead>Ingested</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredDocuments.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center py-8">
                        <div className="text-muted-foreground">
                          {loading ? "Loading..." : "No documents found"}
                        </div>
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredDocuments.map((doc) => (
                      <TableRow
                        key={doc.document_id}
                        className="cursor-pointer hover:bg-muted/50"
                        onClick={() => viewDocumentDetails(doc.document_id)}
                      >
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {getSourceIcon(doc.source_type)}
                            <div>
                              <div className="font-medium truncate max-w-[250px]">
                                {doc.source_uri.split("/").pop() || doc.source_uri}
                              </div>
                              <div className="text-xs text-muted-foreground">
                                {doc.source_type}
                              </div>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{doc.collection}</Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1">
                            {doc.processing_steps.slice(0, 4).map((step, i) => (
                              <div
                                key={step.step_id}
                                className="flex items-center"
                                title={step.step_name}
                              >
                                <div
                                  className={`p-1 rounded ${
                                    step.error
                                      ? "bg-red-100 text-red-600"
                                      : "bg-green-100 text-green-600"
                                  }`}
                                >
                                  {getStepIcon(step.step_type)}
                                </div>
                                {i < doc.processing_steps.length - 1 &&
                                  i < 3 && (
                                    <ArrowRight className="h-3 w-3 text-muted-foreground mx-1" />
                                  )}
                              </div>
                            ))}
                            {doc.processing_steps.length > 4 && (
                              <span className="text-xs text-muted-foreground ml-1">
                                +{doc.processing_steps.length - 4}
                              </span>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex flex-wrap gap-1">
                            {doc.tags.slice(0, 2).map((tag) => (
                              <Badge
                                key={tag}
                                variant="secondary"
                                className="text-xs"
                              >
                                {tag}
                              </Badge>
                            ))}
                            {doc.tags.length > 2 && (
                              <Badge variant="secondary" className="text-xs">
                                +{doc.tags.length - 2}
                              </Badge>
                            )}
                          </div>
                        </TableCell>
                        <TableCell className="text-muted-foreground text-sm">
                          {formatDate(doc.ingestion_timestamp)}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tags" className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            {/* Tag Stats */}
            <Card>
              <CardHeader>
                <CardTitle>Tag Statistics</CardTitle>
                <CardDescription>
                  Document counts by tag
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[400px]">
                  <div className="space-y-2">
                    {tagStats.map((stat) => (
                      <div
                        key={stat.tag}
                        className="flex items-center justify-between p-2 rounded-lg hover:bg-muted/50"
                      >
                        <div className="flex items-center gap-2">
                          <Tag className="h-4 w-4 text-muted-foreground" />
                          <span className="font-medium">{stat.tag}</span>
                          {stat.parent_tag && (
                            <span className="text-xs text-muted-foreground">
                              (child of {stat.parent_tag})
                            </span>
                          )}
                        </div>
                        <Badge variant="secondary">
                          {stat.document_count} docs
                        </Badge>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Tag Hierarchy */}
            <Card>
              <CardHeader>
                <CardTitle>Tag Hierarchy</CardTitle>
                <CardDescription>
                  Parent-child tag relationships
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[400px]">
                  <div className="space-y-2">
                    {Object.entries(tagHierarchy).map(([parent, children]) => (
                      <Collapsible key={parent}>
                        <CollapsibleTrigger className="flex items-center gap-2 p-2 rounded-lg hover:bg-muted/50 w-full">
                          <ChevronRight className="h-4 w-4" />
                          <span className="font-medium">{parent}</span>
                          <Badge variant="outline" className="ml-auto">
                            {children.length} children
                          </Badge>
                        </CollapsibleTrigger>
                        <CollapsibleContent>
                          <div className="pl-8 space-y-1">
                            {children.map((child) => (
                              <div
                                key={child}
                                className="flex items-center gap-2 p-1 text-sm"
                              >
                                <Tag className="h-3 w-3 text-muted-foreground" />
                                {child}
                              </div>
                            ))}
                          </div>
                        </CollapsibleContent>
                      </Collapsible>
                    ))}
                    {Object.keys(tagHierarchy).length === 0 && (
                      <div className="text-muted-foreground text-center py-4">
                        No tag hierarchies defined
                      </div>
                    )}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="collections" className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            {collections.map((col) => (
              <Card
                key={col}
                className="cursor-pointer hover:border-primary"
                onClick={() => fetchCollectionStats(col)}
              >
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Database className="h-5 w-5" />
                    {col}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {stats.byCollection[col] || 0}
                  </div>
                  <div className="text-sm text-muted-foreground">documents</div>
                </CardContent>
              </Card>
            ))}
          </div>

          {collectionStats && (
            <Card>
              <CardHeader>
                <CardTitle>Collection: {collectionStats.collection}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-medium mb-2">Source Distribution</h4>
                    <div className="space-y-1">
                      {Object.entries(collectionStats.source_distribution).map(
                        ([source, count]) => (
                          <div
                            key={source}
                            className="flex items-center justify-between"
                          >
                            <div className="flex items-center gap-2">
                              {getSourceIcon(source)}
                              <span className="capitalize">{source}</span>
                            </div>
                            <span className="text-muted-foreground">{count}</span>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2">Processing Steps</h4>
                    <div className="space-y-1">
                      {Object.entries(collectionStats.processing_steps).map(
                        ([step, count]) => (
                          <div
                            key={step}
                            className="flex items-center justify-between"
                          >
                            <span className="capitalize">{step}</span>
                            <span className="text-muted-foreground">{count}</span>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                </div>
                {collectionStats.last_ingestion && (
                  <div className="text-sm text-muted-foreground">
                    Last ingestion: {formatDate(collectionStats.last_ingestion)}
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      {/* Document Detail Dialog */}
      <Dialog open={detailDialogOpen} onOpenChange={setDetailDialogOpen}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <GitBranch className="h-5 w-5" />
              Document Lineage
            </DialogTitle>
            <DialogDescription>
              {selectedDocument?.source_uri}
            </DialogDescription>
          </DialogHeader>
          {selectedDocument && (
            <div className="space-y-4">
              {/* Document Info */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground">
                    Source Type
                  </h4>
                  <div className="flex items-center gap-2 mt-1">
                    {getSourceIcon(selectedDocument.source_type)}
                    <span className="capitalize">
                      {selectedDocument.source_type}
                    </span>
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground">
                    Collection
                  </h4>
                  <Badge variant="outline" className="mt-1">
                    {selectedDocument.collection}
                  </Badge>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground">
                    Pipeline
                  </h4>
                  <p className="mt-1">
                    {selectedDocument.ingestion_pipeline || "N/A"}
                  </p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground">
                    Ingested
                  </h4>
                  <p className="mt-1">
                    {formatDate(selectedDocument.ingestion_timestamp)}
                  </p>
                </div>
              </div>

              {/* Tags */}
              <div>
                <h4 className="text-sm font-medium text-muted-foreground mb-2">
                  Tags
                </h4>
                <div className="flex flex-wrap gap-2">
                  {selectedDocument.tags.length > 0 ? (
                    selectedDocument.tags.map((tag) => (
                      <Badge key={tag} variant="secondary">
                        {tag}
                      </Badge>
                    ))
                  ) : (
                    <span className="text-muted-foreground">No tags</span>
                  )}
                </div>
              </div>

              {/* Processing Steps */}
              <div>
                <h4 className="text-sm font-medium text-muted-foreground mb-2">
                  Processing History
                </h4>
                <ScrollArea className="h-[200px]">
                  <div className="space-y-2">
                    {selectedDocument.processing_steps.map((step, i) => (
                      <div
                        key={step.step_id}
                        className="flex items-start gap-3 p-3 rounded-lg bg-muted/50"
                      >
                        <div
                          className={`p-2 rounded ${
                            step.error
                              ? "bg-red-100 text-red-600"
                              : "bg-green-100 text-green-600"
                          }`}
                        >
                          {step.error ? (
                            <AlertCircle className="h-4 w-4" />
                          ) : (
                            <CheckCircle className="h-4 w-4" />
                          )}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between">
                            <span className="font-medium">{step.step_name}</span>
                            <span className="text-xs text-muted-foreground">
                              {step.duration_ms.toFixed(0)}ms
                            </span>
                          </div>
                          <div className="text-xs text-muted-foreground mt-1">
                            {formatDate(step.timestamp)}
                          </div>
                          {Object.keys(step.metrics).length > 0 && (
                            <div className="flex gap-2 mt-2">
                              {Object.entries(step.metrics).map(([k, v]) => (
                                <Badge key={k} variant="outline" className="text-xs">
                                  {k}: {String(v)}
                                </Badge>
                              ))}
                            </div>
                          )}
                          {step.error && (
                            <div className="text-sm text-red-600 mt-2">
                              {step.error}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </div>

              {/* Relationships */}
              {(selectedDocument.parent_documents.length > 0 ||
                selectedDocument.child_documents.length > 0) && (
                <div className="grid grid-cols-2 gap-4">
                  {selectedDocument.parent_documents.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-muted-foreground mb-2">
                        Parent Documents
                      </h4>
                      <div className="space-y-1">
                        {selectedDocument.parent_documents.map((id) => (
                          <div
                            key={id}
                            className="text-sm text-muted-foreground truncate"
                          >
                            {id}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  {selectedDocument.child_documents.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-muted-foreground mb-2">
                        Child Documents (Chunks)
                      </h4>
                      <div className="space-y-1">
                        {selectedDocument.child_documents.slice(0, 5).map((id) => (
                          <div
                            key={id}
                            className="text-sm text-muted-foreground truncate"
                          >
                            {id}
                          </div>
                        ))}
                        {selectedDocument.child_documents.length > 5 && (
                          <div className="text-sm text-muted-foreground">
                            +{selectedDocument.child_documents.length - 5} more
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
