"use client";

import * as React from "react";
import dynamic from "next/dynamic";
import { cn } from "@/lib/utils";

const Stage = dynamic(
  () => import("react-konva").then((mod) => mod.Stage),
  { ssr: false }
);
const Layer = dynamic(
  () => import("react-konva").then((mod) => mod.Layer),
  { ssr: false }
);
const Rect = dynamic(
  () => import("react-konva").then((mod) => mod.Rect),
  { ssr: false }
);
const Circle = dynamic(
  () => import("react-konva").then((mod) => mod.Circle),
  { ssr: false }
);
const Line = dynamic(
  () => import("react-konva").then((mod) => mod.Line),
  { ssr: false }
);
const Text = dynamic(
  () => import("react-konva").then((mod) => mod.Text),
  { ssr: false }
);
const Group = dynamic(
  () => import("react-konva").then((mod) => mod.Group),
  { ssr: false }
);

export interface TopologyNode {
  id: string;
  label: string;
  type: string;
  x?: number;
  y?: number;
  status?: string;
}

export interface TopologyEdge {
  from: string;
  to: string;
}

export interface InfraTopologyProps {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
  width?: number;
  height?: number;
  className?: string;
}

const STATUS_COLORS: Record<string, string> = {
  healthy: "#22c55e",
  warning: "#eab308",
  critical: "#ef4444",
  unknown: "#6b7280",
};

function getStatusColor(status?: string): string {
  return STATUS_COLORS[status ?? "unknown"] ?? STATUS_COLORS.unknown;
}

const RECT_TYPES = new Set(["service", "database", "queue", "storage"]);
const NODE_SIZE = 30;

function autoLayout(nodes: TopologyNode[], width: number, height: number): Map<string, { x: number; y: number }> {
  const positions = new Map<string, { x: number; y: number }>();
  const cols = Math.max(1, Math.ceil(Math.sqrt(nodes.length)));
  const spacingX = width / (cols + 1);
  const rows = Math.ceil(nodes.length / cols);
  const spacingY = height / (rows + 1);

  nodes.forEach((node, i) => {
    const col = i % cols;
    const row = Math.floor(i / cols);
    positions.set(node.id, {
      x: node.x ?? spacingX * (col + 1),
      y: node.y ?? spacingY * (row + 1),
    });
  });

  return positions;
}

export function InfraTopology({
  nodes,
  edges,
  width = 800,
  height = 500,
  className,
}: InfraTopologyProps) {
  const [positions, setPositions] = React.useState<Map<string, { x: number; y: number }>>(
    () => autoLayout(nodes, width, height)
  );
  const [scale, setScale] = React.useState(1);
  const [stagePos, setStagePos] = React.useState({ x: 0, y: 0 });
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  React.useEffect(() => {
    setPositions(autoLayout(nodes, width, height));
  }, [nodes, width, height]);

  const handleWheel = React.useCallback(
    (e: { evt: WheelEvent; target: unknown }) => {
      e.evt.preventDefault();
      const scaleBy = 1.08;
      const newScale =
        e.evt.deltaY < 0 ? scale * scaleBy : scale / scaleBy;
      setScale(Math.max(0.3, Math.min(3, newScale)));
    },
    [scale]
  );

  const handleDragEnd = React.useCallback(
    (id: string, x: number, y: number) => {
      setPositions((prev) => {
        const next = new Map(prev);
        next.set(id, { x, y });
        return next;
      });
    },
    []
  );

  if (!mounted) {
    return (
      <div
        className={cn(
          "flex items-center justify-center rounded-lg border border-border bg-background",
          className
        )}
        style={{ width, height }}
      >
        <span className="text-sm text-muted-foreground">Loading topology...</span>
      </div>
    );
  }

  return (
    <div className={cn("rounded-lg border border-border bg-background overflow-hidden", className)}>
      <Stage
        width={width}
        height={height}
        scaleX={scale}
        scaleY={scale}
        x={stagePos.x}
        y={stagePos.y}
        draggable
        onWheel={handleWheel}
        onDragEnd={(e: { target: { x: () => number; y: () => number } }) => {
          setStagePos({ x: e.target.x(), y: e.target.y() });
        }}
      >
        <Layer>
          {edges.map((edge) => {
            const fromPos = positions.get(edge.from);
            const toPos = positions.get(edge.to);
            if (!fromPos || !toPos) return null;
            return (
              <Line
                key={`${edge.from}-${edge.to}`}
                points={[fromPos.x, fromPos.y, toPos.x, toPos.y]}
                stroke="#4b5563"
                strokeWidth={1.5}
                opacity={0.6}
              />
            );
          })}

          {nodes.map((node) => {
            const pos = positions.get(node.id);
            if (!pos) return null;
            const color = getStatusColor(node.status);
            const isRect = RECT_TYPES.has(node.type);

            return (
              <Group
                key={node.id}
                x={pos.x}
                y={pos.y}
                draggable
                onDragEnd={(e: { target: { x: () => number; y: () => number } }) => {
                  handleDragEnd(node.id, e.target.x(), e.target.y());
                }}
              >
                {isRect ? (
                  <Rect
                    offsetX={NODE_SIZE / 2}
                    offsetY={NODE_SIZE / 2}
                    width={NODE_SIZE}
                    height={NODE_SIZE}
                    fill={color}
                    cornerRadius={4}
                    shadowColor="black"
                    shadowBlur={4}
                    shadowOpacity={0.3}
                  />
                ) : (
                  <Circle
                    radius={NODE_SIZE / 2}
                    fill={color}
                    shadowColor="black"
                    shadowBlur={4}
                    shadowOpacity={0.3}
                  />
                )}
                <Text
                  text={node.label}
                  y={NODE_SIZE / 2 + 6}
                  fontSize={11}
                  fill="#d1d5db"
                  align="center"
                  offsetX={40}
                  width={80}
                />
              </Group>
            );
          })}
        </Layer>
      </Stage>
    </div>
  );
}
