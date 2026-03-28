"use client";

import * as React from "react";
import * as d3 from "d3";
import { cn } from "@/lib/utils";

export interface TreeNodeData {
  id: string;
  name: string;
  children?: TreeNodeData[];
  metadata?: Record<string, unknown>;
}

export interface DependencyTreeProps {
  data: TreeNodeData;
  width?: number;
  height?: number;
  className?: string;
  onNodeClick?: (node: TreeNodeData) => void;
}

interface LayoutNode {
  id: string;
  name: string;
  x: number;
  y: number;
  depth: number;
  children?: LayoutNode[];
  _children?: LayoutNode[];
  metadata?: Record<string, unknown>;
  original: TreeNodeData;
}

interface LayoutLink {
  source: LayoutNode;
  target: LayoutNode;
}

function computeLayout(
  root: TreeNodeData,
  width: number,
  height: number
): { nodes: LayoutNode[]; links: LayoutLink[] } {
  const hierarchy = d3
    .hierarchy(root, (d) => d.children)
    .sort((a, b) => d3.ascending(a.data.name, b.data.name));

  const treeLayout = d3
    .tree<TreeNodeData>()
    .size([height - 80, width - 200]);

  const treeRoot = treeLayout(hierarchy);

  const nodes: LayoutNode[] = treeRoot.descendants().map((d) => ({
    id: d.data.id,
    name: d.data.name,
    x: d.y + 100,
    y: d.x + 40,
    depth: d.depth,
    metadata: d.data.metadata,
    original: d.data,
    children: d.children?.map((c) => ({
      id: c.data.id,
      name: c.data.name,
      x: c.y + 100,
      y: c.x + 40,
      depth: c.depth,
      metadata: c.data.metadata,
      original: c.data,
    })) as LayoutNode[] | undefined,
  }));

  const links: LayoutLink[] = treeRoot.links().map((l) => ({
    source: nodes.find((n) => n.id === l.source.data.id)!,
    target: nodes.find((n) => n.id === l.target.data.id)!,
  }));

  return { nodes, links };
}

function linkPath(source: LayoutNode, target: LayoutNode): string {
  const mx = (source.x + target.x) / 2;
  return `M${source.x},${source.y} C${mx},${source.y} ${mx},${target.y} ${target.x},${target.y}`;
}

const NODE_RADIUS = 8;
const COLLAPSE_INDICATOR_RADIUS = 4;

export function DependencyTree({
  data,
  width = 800,
  height = 500,
  className,
  onNodeClick,
}: DependencyTreeProps) {
  const [collapsedIds, setCollapsedIds] = React.useState<Set<string>>(
    new Set()
  );
  const [hoveredId, setHoveredId] = React.useState<string | null>(null);

  const prunedData = React.useMemo(() => {
    function prune(node: TreeNodeData): TreeNodeData {
      if (collapsedIds.has(node.id)) {
        return { ...node, children: undefined };
      }
      return {
        ...node,
        children: node.children?.map(prune),
      };
    }
    return prune(data);
  }, [data, collapsedIds]);

  const { nodes, links } = React.useMemo(
    () => computeLayout(prunedData, width, height),
    [prunedData, width, height]
  );

  const hasChildren = React.useCallback(
    (id: string): boolean => {
      function find(node: TreeNodeData): TreeNodeData | null {
        if (node.id === id) return node;
        for (const child of node.children ?? []) {
          const found = find(child);
          if (found) return found;
        }
        return null;
      }
      const node = find(data);
      return !!node?.children?.length;
    },
    [data]
  );

  const toggleCollapse = React.useCallback(
    (id: string) => {
      setCollapsedIds((prev) => {
        const next = new Set(prev);
        if (next.has(id)) next.delete(id);
        else next.add(id);
        return next;
      });
    },
    []
  );

  const handleNodeClick = React.useCallback(
    (node: LayoutNode) => {
      if (hasChildren(node.id)) {
        toggleCollapse(node.id);
      }
      onNodeClick?.(node.original);
    },
    [hasChildren, toggleCollapse, onNodeClick]
  );

  const depthColors = [
    "#3b82f6",
    "#8b5cf6",
    "#ec4899",
    "#f97316",
    "#10b981",
    "#06b6d4",
  ];

  return (
    <div className={cn("w-full overflow-auto rounded-lg border border-border bg-background", className)}>
      <svg
        width={width}
        height={height}
        viewBox={`0 0 ${width} ${height}`}
        className="select-none"
      >
        <defs>
          <filter id="dep-tree-glow">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <g className="links">
          {links.map((link) => (
            <path
              key={`${link.source.id}-${link.target.id}`}
              d={linkPath(link.source, link.target)}
              fill="none"
              stroke={
                hoveredId === link.source.id || hoveredId === link.target.id
                  ? "#60a5fa"
                  : "#4b5563"
              }
              strokeWidth={
                hoveredId === link.source.id || hoveredId === link.target.id
                  ? 2
                  : 1.5
              }
              strokeOpacity={0.6}
              style={{
                transition: "stroke 200ms, stroke-width 200ms",
              }}
            />
          ))}
        </g>

        <g className="nodes">
          {nodes.map((node) => {
            const color = depthColors[node.depth % depthColors.length];
            const isHovered = hoveredId === node.id;
            const isCollapsed = collapsedIds.has(node.id);
            const expandable = hasChildren(node.id);

            return (
              <g
                key={node.id}
                style={{
                  cursor: expandable ? "pointer" : "default",
                  transition: "transform 300ms ease",
                }}
                onMouseEnter={() => setHoveredId(node.id)}
                onMouseLeave={() => setHoveredId(null)}
                onClick={() => handleNodeClick(node)}
              >
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={isHovered ? NODE_RADIUS + 2 : NODE_RADIUS}
                  fill={color}
                  stroke={isHovered ? "#ffffff" : "transparent"}
                  strokeWidth={2}
                  filter={isHovered ? "url(#dep-tree-glow)" : undefined}
                  style={{ transition: "r 200ms, stroke 200ms" }}
                />

                {expandable && isCollapsed && (
                  <circle
                    cx={node.x + NODE_RADIUS + 5}
                    cy={node.y}
                    r={COLLAPSE_INDICATOR_RADIUS}
                    fill="none"
                    stroke={color}
                    strokeWidth={1.5}
                    strokeDasharray="2 2"
                  />
                )}

                <text
                  x={node.x}
                  y={node.y - NODE_RADIUS - 6}
                  textAnchor="middle"
                  fill={isHovered ? "#f3f4f6" : "#9ca3af"}
                  fontSize={12}
                  fontWeight={isHovered ? 600 : 400}
                  style={{ transition: "fill 200ms" }}
                >
                  {node.name}
                </text>
              </g>
            );
          })}
        </g>
      </svg>
    </div>
  );
}
