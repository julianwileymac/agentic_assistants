"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  FolderKanban,
  Bot,
  GitBranch,
  Puzzle,
  FlaskConical,
  Activity,
  Settings,
  Book,
  ExternalLink,
  ChevronRight,
  Database,
  Server,
  Layers,
  Box,
  HardDrive,
  Brain,
  Cpu,
  Sliders,
  Rocket,
  Tag,
  GraduationCap,
  Target,
  BookOpen,
  ClipboardCheck,
  Sparkles,
  BarChart3,
  MessageSquare,
  Zap,
  Code2,
  ListTodo,
  Search,
  Table2,
  Workflow,
  FileBox,
  Terminal,
  Shield,
  MemoryStick,
  Archive,
  Upload,
  RefreshCw,
  AlertTriangle,
  Network,
  Gauge,
} from "lucide-react";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from "@/components/ui/sidebar";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Button } from "@/components/ui/button";
import { openJupyterLab, getMlflowUrl } from "@/lib/api";
import { getBackendUrl, getExternalToolUrl } from "@/lib/api-client";

const mainNavItems = [
  {
    title: "Dashboard",
    url: "/",
    icon: Home,
  },
  {
    title: "Projects",
    url: "/projects",
    icon: FolderKanban,
  },
  {
    title: "Agents",
    url: "/agents",
    icon: Bot,
  },
  {
    title: "Flows",
    url: "/flows",
    icon: GitBranch,
  },
  {
    title: "Components",
    url: "/library",
    icon: Puzzle,
  },
  {
    title: "Pipelines",
    url: "/pipelines",
    icon: Workflow,
  },
];

const observabilityItems = [
  {
    title: "Experiments",
    url: "/experiments",
    icon: FlaskConical,
  },
  {
    title: "Monitoring",
    url: "/monitoring",
    icon: Activity,
  },
  {
    title: "Error Browser",
    url: "/errors",
    icon: AlertTriangle,
  },
  {
    title: "Lineage",
    url: "/lineage",
    icon: Network,
  },
];

const learningItems = [
  {
    title: "Learning Hub",
    url: "/learning",
    icon: GraduationCap,
  },
  {
    title: "Goals",
    url: "/learning/goals",
    icon: Target,
  },
  {
    title: "Active Topics",
    url: "/learning/topics",
    icon: BookOpen,
  },
  {
    title: "Evaluations",
    url: "/learning/evaluations",
    icon: ClipboardCheck,
  },
];

const assistantItems = [
  {
    title: "Assistant",
    url: "/assistant",
    icon: Sparkles,
  },
  {
    title: "Chat",
    url: "/assistant/chat",
    icon: MessageSquare,
  },
  {
    title: "Analytics",
    url: "/assistant/analytics",
    icon: BarChart3,
  },
];

const modelItems = [
  {
    title: "Models",
    url: "/models",
    icon: Brain,
  },
  {
    title: "Ollama",
    url: "/models/ollama",
    icon: Cpu,
  },
  {
    title: "HuggingFace",
    url: "/huggingface",
    icon: Layers,
  },
  {
    title: "Training",
    url: "/models/training",
    icon: Cpu,
  },
  {
    title: "Tuning & RLHF",
    url: "/models/tuning",
    icon: Sliders,
  },
  {
    title: "Deployment",
    url: "/models/deployment",
    icon: Rocket,
  },
  {
    title: "Nemotron",
    url: "/models/nemotron",
    icon: Gauge,
  },
];

const dataItems = [
  {
    title: "Data Sources",
    url: "/datasources",
    icon: Database,
  },
  {
    title: "Training Data",
    url: "/data/training",
    icon: Database,
  },
  {
    title: "Tags & Lineage",
    url: "/data/tags",
    icon: Tag,
  },
  {
    title: "Knowledge Bases",
    url: "/knowledge",
    icon: Book,
  },
  {
    title: "Document Stores",
    url: "/document-stores",
    icon: FileBox,
  },
];

const catalogItems = [
  {
    title: "Data Catalog",
    url: "/catalog",
    icon: Search,
  },
  {
    title: "Iceberg Tables",
    url: "/iceberg",
    icon: Table2,
  },
];

const dbtItems = [
  {
    title: "dbt Models",
    url: "/dbt",
    icon: Code2,
  },
];

const toolsItems = [
  {
    title: "Execution",
    url: "/execution",
    icon: Terminal,
  },
  {
    title: "Cybersecurity",
    url: "/cybersec",
    icon: Shield,
  },
  {
    title: "Memory Store",
    url: "/memory",
    icon: MemoryStick,
  },
  {
    title: "Solution Cache",
    url: "/cache",
    icon: Archive,
  },
  {
    title: "Upload & Import",
    url: "/upload",
    icon: Upload,
  },
  {
    title: "Session Sync",
    url: "/sync",
    icon: RefreshCw,
  },
];

const resourceItems = [
  {
    title: "Documentation",
    url: "/docs",
    icon: Book,
  },
  {
    title: "Settings",
    url: "/settings",
    icon: Settings,
  },
];

const dagsterItems = [
  {
    title: "Dashboard",
    url: "/dagster",
    icon: Zap,
  },
  {
    title: "Develop",
    url: "/dagster/develop",
    icon: Code2,
  },
  {
    title: "Jobs",
    url: "/dagster/jobs",
    icon: ListTodo,
  },
];

const infrastructureItems = [
  {
    title: "Kubernetes",
    url: "/kubernetes",
    icon: Server,
  },
  {
    title: "Deployments",
    url: "/kubernetes/deployments",
    icon: Layers,
  },
  {
    title: "Model Serving",
    url: "/kubernetes/models",
    icon: Box,
  },
  {
    title: "Storage",
    url: "/kubernetes/storage",
    icon: HardDrive,
  },
];

function ConnectionStatus() {
  const [status, setStatus] = React.useState<'checking' | 'connected' | 'disconnected'>('checking');
  const backendUrl = getBackendUrl();

  React.useEffect(() => {
    const check = async () => {
      try {
        const resp = await fetch(`${backendUrl}/ready`, { signal: AbortSignal.timeout(3000) });
        setStatus(resp.ok ? 'connected' : 'disconnected');
      } catch {
        setStatus('disconnected');
      }
    };
    check();
    const interval = setInterval(check, 30000);
    return () => clearInterval(interval);
  }, [backendUrl]);

  return (
    <SidebarMenuButton size="sm" tooltip={`Backend: ${backendUrl}`}>
      <div className="flex items-center gap-2">
        <div className={`size-2 rounded-full ${status === 'connected' ? 'bg-green-500' : status === 'disconnected' ? 'bg-red-500' : 'bg-yellow-500 animate-pulse'}`} />
        <span className="text-xs text-muted-foreground">
          {status === 'connected' ? 'Connected' : status === 'disconnected' ? 'Disconnected' : 'Checking...'}
        </span>
      </div>
    </SidebarMenuButton>
  );
}

export function AppSidebar() {
  const pathname = usePathname();

  return (
    <Sidebar variant="sidebar" collapsible="icon">
      <SidebarHeader className="border-b border-sidebar-border">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <Link href="/">
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 text-white font-bold text-sm">
                  AG
                </div>
                <div className="flex flex-col gap-0.5 leading-none">
                  <span className="font-semibold">Agentic</span>
                  <span className="text-xs text-muted-foreground">Control Panel</span>
                </div>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        {/* Main Navigation */}
        <SidebarGroup>
          <SidebarGroupLabel>Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {mainNavItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    asChild
                    isActive={
                      item.url === "/"
                        ? pathname === "/"
                        : pathname.startsWith(item.url)
                    }
                    tooltip={item.title}
                  >
                    <Link href={item.url}>
                      <item.icon className="size-4" />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Framework Assistant */}
        <SidebarGroup>
          <Collapsible defaultOpen className="group/collapsible">
            <SidebarGroupLabel asChild>
              <CollapsibleTrigger className="flex w-full items-center">
                Assistant
                <ChevronRight className="ml-auto size-4 transition-transform group-data-[state=open]/collapsible:rotate-90" />
              </CollapsibleTrigger>
            </SidebarGroupLabel>
            <CollapsibleContent>
              <SidebarGroupContent>
                <SidebarMenu>
                  {assistantItems.map((item) => (
                    <SidebarMenuItem key={item.title}>
                      <SidebarMenuButton
                        asChild
                        isActive={
                          item.url === "/assistant"
                            ? pathname === "/assistant"
                            : pathname.startsWith(item.url)
                        }
                        tooltip={item.title}
                      >
                        <Link href={item.url}>
                          <item.icon className="size-4" />
                          <span>{item.title}</span>
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </CollapsibleContent>
          </Collapsible>
        </SidebarGroup>

        {/* Models & Training */}
        <SidebarGroup>
          <Collapsible defaultOpen className="group/collapsible">
            <SidebarGroupLabel asChild>
              <CollapsibleTrigger className="flex w-full items-center">
                Models
                <ChevronRight className="ml-auto size-4 transition-transform group-data-[state=open]/collapsible:rotate-90" />
              </CollapsibleTrigger>
            </SidebarGroupLabel>
            <CollapsibleContent>
              <SidebarGroupContent>
                <SidebarMenu>
                  {modelItems.map((item) => (
                    <SidebarMenuItem key={item.title}>
                      <SidebarMenuButton
                        asChild
                        isActive={
                          item.url === "/models"
                            ? pathname === "/models"
                            : pathname.startsWith(item.url)
                        }
                        tooltip={item.title}
                      >
                        <Link href={item.url}>
                          <item.icon className="size-4" />
                          <span>{item.title}</span>
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </CollapsibleContent>
          </Collapsible>
        </SidebarGroup>

        {/* Observability */}
        <SidebarGroup>
          <SidebarGroupLabel>Observability</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {observabilityItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    asChild
                    isActive={pathname.startsWith(item.url)}
                    tooltip={item.title}
                  >
                    <Link href={item.url}>
                      <item.icon className="size-4" />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Learning */}
        <SidebarGroup>
          <Collapsible defaultOpen className="group/collapsible">
            <SidebarGroupLabel asChild>
              <CollapsibleTrigger className="flex w-full items-center">
                Learning
                <ChevronRight className="ml-auto size-4 transition-transform group-data-[state=open]/collapsible:rotate-90" />
              </CollapsibleTrigger>
            </SidebarGroupLabel>
            <CollapsibleContent>
              <SidebarGroupContent>
                <SidebarMenu>
                  {learningItems.map((item) => (
                    <SidebarMenuItem key={item.title}>
                      <SidebarMenuButton
                        asChild
                        isActive={
                          item.url === "/learning"
                            ? pathname === "/learning"
                            : pathname.startsWith(item.url)
                        }
                        tooltip={item.title}
                      >
                        <Link href={item.url}>
                          <item.icon className="size-4" />
                          <span>{item.title}</span>
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </CollapsibleContent>
          </Collapsible>
        </SidebarGroup>

        {/* Data & Resources */}
        <SidebarGroup>
          <Collapsible defaultOpen className="group/collapsible">
            <SidebarGroupLabel asChild>
              <CollapsibleTrigger className="flex w-full items-center">
                Data
                <ChevronRight className="ml-auto size-4 transition-transform group-data-[state=open]/collapsible:rotate-90" />
              </CollapsibleTrigger>
            </SidebarGroupLabel>
            <CollapsibleContent>
              <SidebarGroupContent>
                <SidebarMenu>
                  {dataItems.map((item) => (
                    <SidebarMenuItem key={item.title}>
                      <SidebarMenuButton
                        asChild
                        isActive={pathname.startsWith(item.url)}
                        tooltip={item.title}
                      >
                        <Link href={item.url}>
                          <item.icon className="size-4" />
                          <span>{item.title}</span>
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </CollapsibleContent>
          </Collapsible>
        </SidebarGroup>

        {/* Data Catalog */}
        <SidebarGroup>
          <Collapsible defaultOpen className="group/collapsible">
            <SidebarGroupLabel asChild>
              <CollapsibleTrigger className="flex w-full items-center">
                Data Catalog
                <ChevronRight className="ml-auto size-4 transition-transform group-data-[state=open]/collapsible:rotate-90" />
              </CollapsibleTrigger>
            </SidebarGroupLabel>
            <CollapsibleContent>
              <SidebarGroupContent>
                <SidebarMenu>
                  {catalogItems.map((item) => (
                    <SidebarMenuItem key={item.title}>
                      <SidebarMenuButton
                        asChild
                        isActive={pathname.startsWith(item.url)}
                        tooltip={item.title}
                      >
                        <Link href={item.url}>
                          <item.icon className="size-4" />
                          <span>{item.title}</span>
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </CollapsibleContent>
          </Collapsible>
        </SidebarGroup>

        {/* Orchestration: Dagster + dbt */}
        <SidebarGroup>
          <Collapsible defaultOpen className="group/collapsible">
            <SidebarGroupLabel asChild>
              <CollapsibleTrigger className="flex w-full items-center">
                Orchestration
                <ChevronRight className="ml-auto size-4 transition-transform group-data-[state=open]/collapsible:rotate-90" />
              </CollapsibleTrigger>
            </SidebarGroupLabel>
            <CollapsibleContent>
              <SidebarGroupContent>
                <SidebarMenu>
                  {dagsterItems.map((item) => (
                    <SidebarMenuItem key={item.title}>
                      <SidebarMenuButton
                        asChild
                        isActive={
                          item.url === "/dagster"
                            ? pathname === "/dagster"
                            : pathname.startsWith(item.url)
                        }
                        tooltip={item.title}
                      >
                        <Link href={item.url}>
                          <item.icon className="size-4" />
                          <span>{item.title}</span>
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                  {dbtItems.map((item) => (
                    <SidebarMenuItem key={item.title}>
                      <SidebarMenuButton
                        asChild
                        isActive={pathname.startsWith(item.url)}
                        tooltip={item.title}
                      >
                        <Link href={item.url}>
                          <item.icon className="size-4" />
                          <span>{item.title}</span>
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </CollapsibleContent>
          </Collapsible>
        </SidebarGroup>

        {/* Tools & Services */}
        <SidebarGroup>
          <Collapsible className="group/collapsible">
            <SidebarGroupLabel asChild>
              <CollapsibleTrigger className="flex w-full items-center">
                Tools
                <ChevronRight className="ml-auto size-4 transition-transform group-data-[state=open]/collapsible:rotate-90" />
              </CollapsibleTrigger>
            </SidebarGroupLabel>
            <CollapsibleContent>
              <SidebarGroupContent>
                <SidebarMenu>
                  {toolsItems.map((item) => (
                    <SidebarMenuItem key={item.title}>
                      <SidebarMenuButton
                        asChild
                        isActive={pathname.startsWith(item.url)}
                        tooltip={item.title}
                      >
                        <Link href={item.url}>
                          <item.icon className="size-4" />
                          <span>{item.title}</span>
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </CollapsibleContent>
          </Collapsible>
        </SidebarGroup>

        {/* Settings */}
        <SidebarGroup>
          <SidebarGroupLabel>System</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {resourceItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    asChild
                    isActive={pathname.startsWith(item.url)}
                    tooltip={item.title}
                  >
                    <Link href={item.url}>
                      <item.icon className="size-4" />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Infrastructure */}
        <SidebarGroup>
          <Collapsible defaultOpen className="group/collapsible">
            <SidebarGroupLabel asChild>
              <CollapsibleTrigger className="flex w-full items-center">
                Infrastructure
                <ChevronRight className="ml-auto size-4 transition-transform group-data-[state=open]/collapsible:rotate-90" />
              </CollapsibleTrigger>
            </SidebarGroupLabel>
            <CollapsibleContent>
              <SidebarGroupContent>
                <SidebarMenu>
                  {infrastructureItems.map((item) => (
                    <SidebarMenuItem key={item.title}>
                      <SidebarMenuButton
                        asChild
                        isActive={
                          item.url === "/kubernetes"
                            ? pathname === "/kubernetes"
                            : pathname.startsWith(item.url)
                        }
                        tooltip={item.title}
                      >
                        <Link href={item.url}>
                          <item.icon className="size-4" />
                          <span>{item.title}</span>
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </CollapsibleContent>
          </Collapsible>
        </SidebarGroup>

        {/* External Links */}
        <SidebarGroup>
          <Collapsible defaultOpen className="group/collapsible">
            <SidebarGroupLabel asChild>
              <CollapsibleTrigger className="flex w-full items-center">
                External Tools
                <ChevronRight className="ml-auto size-4 transition-transform group-data-[state=open]/collapsible:rotate-90" />
              </CollapsibleTrigger>
            </SidebarGroupLabel>
            <CollapsibleContent>
              <SidebarGroupContent>
                <SidebarMenu>
                  <SidebarMenuItem>
                    <SidebarMenuButton
                      onClick={() => openJupyterLab()}
                      tooltip="Open JupyterLab"
                    >
                      <ExternalLink className="size-4" />
                      <span>JupyterLab</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                  <SidebarMenuItem>
                    <SidebarMenuButton
                      onClick={() => window.open(getMlflowUrl(), '_blank')}
                      tooltip="Open MLFlow UI"
                    >
                      <ExternalLink className="size-4" />
                      <span>MLFlow UI</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                  <SidebarMenuItem>
                    <SidebarMenuButton
                      onClick={() => window.open(getExternalToolUrl('dagster'), '_blank')}
                      tooltip="Open Dagster UI"
                    >
                      <ExternalLink className="size-4" />
                      <span>Dagster UI</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                  <SidebarMenuItem>
                    <SidebarMenuButton
                      onClick={() => window.open(getExternalToolUrl('datahub'), '_blank')}
                      tooltip="Open DataHub UI"
                    >
                      <ExternalLink className="size-4" />
                      <span>DataHub UI</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                </SidebarMenu>
              </SidebarGroupContent>
            </CollapsibleContent>
          </Collapsible>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t border-sidebar-border">
        <SidebarMenu>
          <SidebarMenuItem>
            <ConnectionStatus />
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>

      <SidebarRail />
    </Sidebar>
  );
}

