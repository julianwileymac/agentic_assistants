"use client";

import * as React from "react";
import dynamic from "next/dynamic";
import type { EChartsOption } from "echarts";
import { cn } from "@/lib/utils";

const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false });

export interface TimeSeriesDataPoint {
  time: string;
  value: number;
  series?: string;
}

export interface TimeSeriesChartProps {
  data: TimeSeriesDataPoint[];
  title?: string;
  height?: number;
  theme?: "dark" | "light";
  showLegend?: boolean;
  className?: string;
}

function groupBySeries(data: TimeSeriesDataPoint[]) {
  const groups = new Map<string, { time: string; value: number }[]>();
  for (const point of data) {
    const key = point.series ?? "default";
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)!.push({ time: point.time, value: point.value });
  }
  return groups;
}

export function TimeSeriesChart({
  data,
  title,
  height = 400,
  theme = "dark",
  showLegend = true,
  className,
}: TimeSeriesChartProps) {
  const grouped = React.useMemo(() => groupBySeries(data), [data]);
  const seriesNames = React.useMemo(() => Array.from(grouped.keys()), [grouped]);

  const isDark = theme === "dark";

  const option = React.useMemo<EChartsOption>(() => {
    const allTimes = Array.from(
      new Set(data.map((d) => d.time))
    ).sort();

    const series = seriesNames.map((name) => {
      const points = grouped.get(name)!;
      const timeValueMap = new Map(points.map((p) => [p.time, p.value]));
      return {
        name: name === "default" ? (title ?? "Value") : name,
        type: "line" as const,
        smooth: true,
        symbol: "circle",
        symbolSize: 4,
        showSymbol: false,
        areaStyle: { opacity: 0.15 },
        emphasis: { focus: "series" as const },
        data: allTimes.map((t) => timeValueMap.get(t) ?? null),
      };
    });

    return {
      backgroundColor: "transparent",
      title: title
        ? {
            text: title,
            left: "center",
            textStyle: {
              color: isDark ? "#e5e7eb" : "#1f2937",
              fontSize: 14,
              fontWeight: 600,
            },
          }
        : undefined,
      tooltip: {
        trigger: "axis",
        backgroundColor: isDark ? "#1f2937" : "#ffffff",
        borderColor: isDark ? "#374151" : "#e5e7eb",
        textStyle: { color: isDark ? "#e5e7eb" : "#1f2937" },
        axisPointer: { type: "cross" },
      },
      legend: showLegend
        ? {
            bottom: 35,
            textStyle: { color: isDark ? "#9ca3af" : "#6b7280" },
            data: series.map((s) => s.name),
          }
        : undefined,
      grid: {
        left: 50,
        right: 20,
        top: title ? 50 : 20,
        bottom: showLegend ? 80 : 50,
        containLabel: false,
      },
      xAxis: {
        type: "category",
        boundaryGap: false,
        data: allTimes,
        axisLine: { lineStyle: { color: isDark ? "#4b5563" : "#d1d5db" } },
        axisLabel: { color: isDark ? "#9ca3af" : "#6b7280", fontSize: 11 },
        splitLine: { show: false },
      },
      yAxis: {
        type: "value",
        axisLine: { show: false },
        axisLabel: { color: isDark ? "#9ca3af" : "#6b7280", fontSize: 11 },
        splitLine: {
          lineStyle: { color: isDark ? "#374151" : "#e5e7eb", type: "dashed" },
        },
      },
      dataZoom: [
        {
          type: "inside",
          start: 0,
          end: 100,
        },
        {
          type: "slider",
          start: 0,
          end: 100,
          height: 20,
          bottom: 5,
          borderColor: isDark ? "#4b5563" : "#d1d5db",
          backgroundColor: isDark ? "#1f2937" : "#f3f4f6",
          fillerColor: isDark
            ? "rgba(59,130,246,0.25)"
            : "rgba(59,130,246,0.15)",
          handleStyle: { color: isDark ? "#60a5fa" : "#3b82f6" },
          textStyle: { color: isDark ? "#9ca3af" : "#6b7280" },
        },
      ],
      series,
    };
  }, [data, grouped, seriesNames, title, isDark, showLegend]);

  return (
    <div className={cn("w-full", className)}>
      <ReactECharts
        option={option}
        style={{ height, width: "100%" }}
        opts={{ renderer: "canvas" }}
        notMerge
      />
    </div>
  );
}
