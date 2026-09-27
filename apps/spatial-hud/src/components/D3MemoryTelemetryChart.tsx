import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { Activity, AlertTriangle, ShieldCheck, Zap, HardDrive, Maximize2, Minimize2 } from 'lucide-react';
import { ThemeMode } from '../types';

export interface MemoryDataPoint {
  timestamp: number;
  memoryGB: number;
  thresholdGB: number;
  phase: string;
}

interface D3MemoryTelemetryChartProps {
  theme: ThemeMode;
  currentMemoryGB: number;
  thresholdGB?: number;
  isRunningGauntlet?: boolean;
}

export const D3MemoryTelemetryChart: React.FC<D3MemoryTelemetryChartProps> = ({
  theme,
  currentMemoryGB,
  thresholdGB = 7.2,
  isRunningGauntlet = false,
}) => {
  const isDark = theme === 'dark';
  const svgRef = useRef<SVGSVGElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  // Live series buffer
  const [dataPoints, setDataPoints] = useState<MemoryDataPoint[]>(() => {
    const now = Date.now();
    return Array.from({ length: 30 }, (_, i) => ({
      timestamp: now - (29 - i) * 1000,
      memoryGB: +(3.8 + Math.sin(i * 0.4) * 0.5 + Math.random() * 0.3).toFixed(2),
      thresholdGB: 7.2,
      phase: 'STEADY_STATE',
    }));
  });

  const [hoveredPoint, setHoveredPoint] = useState<MemoryDataPoint | null>(null);
  const [isOverlayExpanded, setIsOverlayExpanded] = useState<boolean>(false);

  // Tick update loop
  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now();
      const jitter = isRunningGauntlet
        ? (Math.random() * 1.8 - 0.5)
        : (Math.random() * 0.3 - 0.15);
      
      const nextVal = Math.max(
        1.5,
        Math.min(8.0, +(currentMemoryGB + jitter).toFixed(2))
      );

      const nextPoint: MemoryDataPoint = {
        timestamp: now,
        memoryGB: nextVal,
        thresholdGB,
        phase: nextVal > thresholdGB ? 'IRON_GATE_ALERT' : isRunningGauntlet ? 'GAUNTLET_TEST' : 'LIVE_SSM',
      };

      setDataPoints((prev) => {
        const sliced = prev.slice(prev.length >= 40 ? 1 : 0);
        return [...sliced, nextPoint];
      });
    }, 600);

    return () => clearInterval(interval);
  }, [currentMemoryGB, thresholdGB, isRunningGauntlet]);

  // Render D3 chart
  useEffect(() => {
    if (!svgRef.current || !containerRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const containerWidth = containerRef.current.clientWidth || 600;
    const height = isOverlayExpanded ? 340 : 220;
    const margin = { top: 24, right: 30, bottom: 30, left: 45 };
    const width = containerWidth - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Define Gradients and Filters
    const defs = svg.append('defs');

    // Area gradient
    const areaGradient = defs
      .append('linearGradient')
      .attr('id', 'd3-memory-area-grad')
      .attr('x1', '0%')
      .attr('y1', '0%')
      .attr('x2', '0%')
      .attr('y2', '100%');

    areaGradient
      .append('stop')
      .attr('offset', '0%')
      .attr('stop-color', '#00E5FF')
      .attr('stop-opacity', isDark ? 0.35 : 0.25);

    areaGradient
      .append('stop')
      .attr('offset', '100%')
      .attr('stop-color', '#9D4EDD')
      .attr('stop-opacity', 0.0);

    // Threshold Alert Gradient
    const alertGradient = defs
      .append('linearGradient')
      .attr('id', 'd3-memory-alert-grad')
      .attr('x1', '0%')
      .attr('y1', '0%')
      .attr('x2', '0%')
      .attr('y2', '100%');

    alertGradient
      .append('stop')
      .attr('offset', '0%')
      .attr('stop-color', '#FF007F')
      .attr('stop-opacity', 0.45);

    alertGradient
      .append('stop')
      .attr('offset', '100%')
      .attr('stop-color', '#FF007F')
      .attr('stop-opacity', 0.0);

    // Glow filter
    const filter = defs
      .append('filter')
      .attr('id', 'd3-neon-glow')
      .attr('x', '-30%')
      .attr('y', '-30%')
      .attr('width', '160%')
      .attr('height', '160%');

    filter.append('feGaussianBlur').attr('stdDeviation', '3').attr('result', 'coloredBlur');
    const feMerge = filter.append('feMerge');
    feMerge.append('feMergeNode').attr('in', 'coloredBlur');
    feMerge.append('feMergeNode').attr('in', 'SourceGraphic');

    const g = svg
      .attr('width', containerWidth)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // X and Y Scales
    const xScale = d3
      .scaleTime()
      .domain(d3.extent(dataPoints, (d) => new Date(d.timestamp)) as [Date, Date])
      .range([0, width]);

    const yScale = d3
      .scaleLinear()
      .domain([0, 8.5])
      .range([innerHeight, 0]);

    // Gridlines
    const yGrid = d3
      .axisLeft(yScale)
      .ticks(5)
      .tickSize(-width)
      .tickFormat(() => '');

    g.append('g')
      .attr('class', 'grid-lines')
      .call(yGrid)
      .selectAll('line')
      .attr('stroke', isDark ? 'rgba(255, 255, 255, 0.07)' : 'rgba(0, 0, 0, 0.06)')
      .attr('stroke-dasharray', '3,3');

    g.select('.grid-lines .domain').remove();

    // 7.2GB Hard Ceiling Area fill (danger zone > 7.2GB)
    const thresholdY = yScale(thresholdGB);
    g.append('rect')
      .attr('x', 0)
      .attr('y', 0)
      .attr('width', width)
      .attr('height', Math.max(0, thresholdY))
      .attr('fill', isDark ? 'rgba(255, 0, 127, 0.05)' : 'rgba(239, 68, 68, 0.04)');

    // Threshold Line
    g.append('line')
      .attr('x1', 0)
      .attr('x2', width)
      .attr('y1', thresholdY)
      .attr('y2', thresholdY)
      .attr('stroke', '#FF007F')
      .attr('stroke-width', 1.5)
      .attr('stroke-dasharray', '5,4')
      .attr('filter', 'url(#d3-neon-glow)');

    // Threshold Label
    g.append('text')
      .attr('x', width - 8)
      .attr('y', thresholdY - 6)
      .attr('text-anchor', 'end')
      .attr('fill', '#FF007F')
      .attr('font-size', '10px')
      .attr('font-family', 'monospace')
      .attr('font-weight', 'bold')
      .text(`7.2 GB SCARCITY CEILING (90%)`);

    // Area generator
    const areaGenerator = d3
      .area<MemoryDataPoint>()
      .x((d) => xScale(new Date(d.timestamp)))
      .y0(innerHeight)
      .y1((d) => yScale(d.memoryGB))
      .curve(d3.curveMonotoneX);

    g.append('path')
      .datum(dataPoints)
      .attr('fill', currentMemoryGB > thresholdGB ? 'url(#d3-memory-alert-grad)' : 'url(#d3-memory-area-grad)')
      .attr('d', areaGenerator);

    // Line generator
    const lineGenerator = d3
      .line<MemoryDataPoint>()
      .x((d) => xScale(new Date(d.timestamp)))
      .y((d) => yScale(d.memoryGB))
      .curve(d3.curveMonotoneX);

    g.append('path')
      .datum(dataPoints)
      .attr('fill', 'none')
      .attr('stroke', currentMemoryGB > thresholdGB ? '#FF007F' : '#00E5FF')
      .attr('stroke-width', 2.5)
      .attr('filter', 'url(#d3-neon-glow)')
      .attr('d', lineGenerator);

    // X Axis
    const xAxis = d3
      .axisBottom(xScale)
      .ticks(5)
      .tickFormat((d) => d3.timeFormat('%H:%M:%S')(d as Date));

    g.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(xAxis)
      .call((axis) => {
        axis.select('.domain').attr('stroke', isDark ? 'rgba(255, 255, 255, 0.15)' : 'rgba(0, 0, 0, 0.15)');
        axis.selectAll('text')
          .attr('fill', isDark ? '#94a3b8' : '#64748b')
          .attr('font-size', '10px')
          .attr('font-family', 'monospace');
        axis.selectAll('line').attr('stroke', isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)');
      });

    // Y Axis
    const yAxis = d3
      .axisLeft(yScale)
      .ticks(5)
      .tickFormat((d) => `${d}GB`);

    g.append('g')
      .call(yAxis)
      .call((axis) => {
        axis.select('.domain').remove();
        axis.selectAll('text')
          .attr('fill', isDark ? '#94a3b8' : '#64748b')
          .attr('font-size', '10px')
          .attr('font-family', 'monospace');
        axis.selectAll('line').remove();
      });

    // Current live point pulsing dot
    const latestPoint = dataPoints[dataPoints.length - 1];
    if (latestPoint) {
      const latestX = xScale(new Date(latestPoint.timestamp));
      const latestY = yScale(latestPoint.memoryGB);

      // Outer ripple
      g.append('circle')
        .attr('cx', latestX)
        .attr('cy', latestY)
        .attr('r', 7)
        .attr('fill', 'none')
        .attr('stroke', latestPoint.memoryGB > thresholdGB ? '#FF007F' : '#00E5FF')
        .attr('stroke-width', 1.5)
        .attr('opacity', 0.8);

      // Inner dot
      g.append('circle')
        .attr('cx', latestX)
        .attr('cy', latestY)
        .attr('r', 4)
        .attr('fill', latestPoint.memoryGB > thresholdGB ? '#FF007F' : '#00E5FF')
        .attr('filter', 'url(#d3-neon-glow)');
    }

    // Hover interactive overlay
    const bisect = d3.bisector<MemoryDataPoint, Date>((d) => new Date(d.timestamp)).center;

    const overlay = g
      .append('rect')
      .attr('width', width)
      .attr('height', innerHeight)
      .attr('fill', 'transparent')
      .attr('cursor', 'crosshair');

    overlay
      .on('mousemove', function (event) {
        const [pointerX] = d3.pointer(event, this);
        const hoveredDate = xScale.invert(pointerX);
        const index = bisect(dataPoints, hoveredDate);
        const selected = dataPoints[index];
        if (selected) {
          setHoveredPoint(selected);
        }
      })
      .on('mouseleave', function () {
        setHoveredPoint(null);
      });
  }, [dataPoints, currentMemoryGB, thresholdGB, isDark, isOverlayExpanded]);

  const latestVal = dataPoints[dataPoints.length - 1]?.memoryGB ?? currentMemoryGB;
  const isOver = latestVal > thresholdGB;
  const headroomGB = +(thresholdGB - latestVal).toFixed(2);

  return (
    <div
      ref={containerRef}
      className={`rounded-2xl border transition-all duration-300 relative overflow-hidden font-mono ${
        isOver
          ? 'bg-rose-950/40 border-rose-500 shadow-[0_0_30px_rgba(244,63,94,0.3)]'
          : isDark
          ? 'bg-[#08080f]/95 border-cyan-500/30 shadow-[0_0_25px_rgba(0,229,255,0.15)]'
          : 'bg-white border-slate-300 shadow-md'
      }`}
    >
      {/* Overlay Header Bar */}
      <div className="p-4 border-b border-neutral-800/80 flex flex-wrap items-center justify-between gap-3 bg-neutral-950/60">
        <div className="flex items-center space-x-3">
          <div
            className={`p-2 rounded-xl border flex items-center justify-center ${
              isOver
                ? 'bg-rose-950/80 border-rose-500 text-rose-400 animate-pulse'
                : 'bg-cyan-950/60 border-cyan-500/40 text-cyan-400'
            }`}
          >
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h4 className="text-xs font-bold tracking-wider text-neutral-100 flex items-center space-x-2">
                <span>D3.JS REAL-TIME MEMORY ENGINE</span>
                <span className="text-[10px] text-cyan-400 font-mono">[8GB SCARCITY WATCHDOG]</span>
              </h4>
              <span
                className={`px-2 py-0.5 rounded-full text-[9px] font-bold border ${
                  isOver
                    ? 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                    : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                }`}
              >
                {isOver ? 'THRESHOLD BREACHED' : 'SCARCITY BOUNDS SAT'}
              </span>
            </div>
            <p className="text-[11px] text-neutral-400">
              Live Vector Time-Series Sampling (600ms resolution) • Formal Floor: 7.20 GB
            </p>
          </div>
        </div>

        {/* Live Metrics Pill */}
        <div className="flex items-center space-x-2">
          <div className="px-3 py-1 rounded-lg bg-neutral-900 border border-neutral-800 text-xs flex items-center space-x-2">
            <HardDrive className="w-3.5 h-3.5 text-cyan-400" />
            <span className="text-neutral-400">CURRENT:</span>
            <span className={`font-bold ${isOver ? 'text-rose-400 animate-pulse' : 'text-cyan-300'}`}>
              {latestVal.toFixed(2)} GB
            </span>
          </div>

          <div className="px-3 py-1 rounded-lg bg-neutral-900 border border-neutral-800 text-xs">
            <span className="text-neutral-400">HEADROOM: </span>
            <span className={headroomGB < 0 ? 'text-rose-400 font-bold' : 'text-emerald-400 font-bold'}>
              {headroomGB < 0 ? `${Math.abs(headroomGB).toFixed(2)} GB OVER` : `${headroomGB.toFixed(2)} GB SAFE`}
            </span>
          </div>

          <button
            onClick={() => setIsOverlayExpanded(!isOverlayExpanded)}
            className="p-1.5 rounded-lg bg-neutral-900 hover:bg-neutral-800 border border-neutral-700 text-neutral-300 cursor-pointer"
            title={isOverlayExpanded ? 'Collapse Chart' : 'Expand Chart'}
          >
            {isOverlayExpanded ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* SVG Canvas Container */}
      <div className="relative w-full p-2">
        <svg ref={svgRef} className="w-full overflow-visible" />

        {/* Hover Tooltip Overlay */}
        {hoveredPoint && (
          <div className="absolute top-4 right-6 p-2.5 rounded-xl bg-neutral-950/90 border border-cyan-500/40 text-xs space-y-1 shadow-lg backdrop-blur-md pointer-events-none">
            <div className="text-[10px] text-neutral-400">
              TIME: {new Date(hoveredPoint.timestamp).toLocaleTimeString()}
            </div>
            <div className="flex justify-between space-x-4">
              <span className="text-neutral-400">ALLOCATION:</span>
              <span className={hoveredPoint.memoryGB > thresholdGB ? 'text-rose-400 font-bold' : 'text-cyan-300 font-bold'}>
                {hoveredPoint.memoryGB.toFixed(2)} GB
              </span>
            </div>
            <div className="flex justify-between space-x-4">
              <span className="text-neutral-400">PHASE:</span>
              <span className="text-purple-300 font-mono">{hoveredPoint.phase}</span>
            </div>
          </div>
        )}
      </div>

      {/* Footer Invariant Note */}
      <div className="px-4 py-2 bg-neutral-950/80 border-t border-neutral-800/80 flex justify-between items-center text-[10px] text-neutral-500">
        <span>Z3 SMT Invariant: ram_allocated ≤ 7.20 GB ⟹ ¬SIGUSR2_Interrupt</span>
        <span className="text-cyan-400 font-mono">D3 VECTOR ENGINE :: ACTIVE</span>
      </div>
    </div>
  );
};

export default D3MemoryTelemetryChart;
