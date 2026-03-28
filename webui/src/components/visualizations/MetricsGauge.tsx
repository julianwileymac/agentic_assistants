"use client";

import * as React from "react";
import dynamic from "next/dynamic";
import type { EChartsOption } from "echarts";
import { cn } from "@/lib/utils";

const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false });

export interface MetricsGaugeProps {
  value: number;
  max?: number;
  title?: string;
  unit?: string;
  thresholds?: { warning: number; critical: number };
  className?: string;
}

export function MetricsGauge({
  value,
  max = 100,
  title,
  unit = "",
  thresholds = { warning: 60, critical: 85 },
  className,
}: MetricsGaugeProps) {
  const warningPct = thresholds.warning / max;
  const criticalPct = thresholds.critical / max;

  const option = React.useMemo<EChartsOption>(
    () => ({
      backgroundColor: "transparent",
      series: [
        {
          type: "gauge",
          startAngle: 200,
          endAngle: -20,
          min: 0,
          max,
          center: ["50%", "60%"],
          radius: "90%",
          progress: { show: true, width: 14 },
          pointer: {
            length: "55%",
            width: 5,
            itemStyle: { color: "auto" },
          },
          axisLine: {
            lineStyle: {
              width: 14,
              color: [
                [warningPct, "#22c55e"],
                [criticalPct, "#eab308"],
                [1, "#ef4444"],
              ],
            },
          },
          axisTick: {
            distance: -18,
            length: 4,
            lineStyle: { color: "#6b7280", width: 1 },
          },
          splitLine: {
            distance: -22,
            length: 8,
            lineStyle: { color: "#6b7280", width: 1.5 },
          },
          axisLabel: {
            color: "#9ca3af",
            distance: 24,
            fontSize: 10,
          },
          detail: {
            valueAnimation: true,
            formatter: `{value}${unit ? " " + unit : ""}`,
            color: "#e5e7eb",
            fontSize: 20,
            fontWeight: 700,
            offsetCenter: [0, "25%"],
          },
          title: title
            ? {
                offsetCenter: [0, "45%"],
                fontSize: 12,
                color: "#9ca3af",
                fontWeight: 400,
              }
            : { show: false },
          data: [{ value, name: title ?? "" }],
        },
      ],
    }),
    [value, max, title, unit, warningPct, criticalPct]
  );

  return (
    <div className={cn("w-full", className)}>
      <ReactECharts
        option={option}
        style={{ height: 220, width: "100%" }}
        opts={{ renderer: "canvas" }}
        notMerge
      />
    </div>
  );
}
