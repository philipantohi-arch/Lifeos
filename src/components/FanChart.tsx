/**
 * Fan chart: the 10th–90th percentile band of simulated futures with the
 * median path — honest uncertainty, not a single fake-precise line.
 */

import type { GoalForecast } from '../engine/types';

interface Props {
  forecast: GoalForecast;
  startValue: number;
  target: number;
  unit: string;
  height?: number;
}

export function FanChart({ forecast, startValue, target, unit, height = 220 }: Props) {
  const width = 720;
  const pad = { top: 14, right: 12, bottom: 26, left: 56 };
  const pts = [{ dayOffset: 0, p10: startValue, p50: startValue, p90: startValue }, ...forecast.fan];

  const allVals = pts.flatMap((p) => [p.p10, p.p90]).concat(target);
  const lo = Math.min(...allVals) * 0.985;
  const hi = Math.max(...allVals) * 1.015;
  const maxDay = pts[pts.length - 1].dayOffset || 1;

  const x = (d: number) => pad.left + (d / maxDay) * (width - pad.left - pad.right);
  const y = (v: number) => pad.top + (1 - (v - lo) / Math.max(hi - lo, 1e-9)) * (height - pad.top - pad.bottom);

  const fmt = (v: number) =>
    unit === '$' ? `$${Math.round(v).toLocaleString()}` : `${Math.round(v * 10) / 10}`;

  const band =
    pts.map((p) => `${x(p.dayOffset)},${y(p.p90)}`).join(' ') +
    ' ' +
    [...pts].reverse().map((p) => `${x(p.dayOffset)},${y(p.p10)}`).join(' ');
  const median = pts.map((p) => `${x(p.dayOffset)},${y(p.p50)}`).join(' ');

  const gridLines = 4;
  const xLabel = (d: number) => (d >= 360 ? `${Math.round(d / 30)}mo` : d >= 60 ? `${Math.round(d / 30)}mo` : `${d}d`);

  return (
    <div className="trend-chart">
      <svg viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none" style={{ width: '100%', height }}>
        {Array.from({ length: gridLines + 1 }, (_, i) => {
          const v = lo + ((hi - lo) * i) / gridLines;
          return (
            <g key={i}>
              <line x1={pad.left} x2={width - pad.right} y1={y(v)} y2={y(v)} stroke="var(--grid)" strokeWidth={1} />
              <text x={pad.left - 8} y={y(v) + 4} textAnchor="end" className="chart-tick">
                {fmt(v)}
              </text>
            </g>
          );
        })}
        <polygon points={band} fill="var(--accent)" opacity={0.16} />
        <polyline points={median} fill="none" stroke="var(--accent)" strokeWidth={2.5} strokeLinejoin="round" />
        <line
          x1={pad.left}
          x2={width - pad.right}
          y1={y(target)}
          y2={y(target)}
          stroke="var(--green)"
          strokeWidth={1.5}
          strokeDasharray="6 5"
        />
        <text x={width - pad.right} y={y(target) - 6} textAnchor="end" className="chart-tick" fill="var(--green)">
          target {fmt(target)}
        </text>
        {pts
          .filter((_, i) => i > 0 && i % Math.ceil((pts.length - 1) / 4) === 0)
          .map((p) => (
            <text key={p.dayOffset} x={x(p.dayOffset)} y={height - 6} textAnchor="middle" className="chart-tick">
              {xLabel(p.dayOffset)}
            </text>
          ))}
      </svg>
      <div className="chart-legend">
        <span className="legend-item">
          <span className="legend-swatch" style={{ background: 'var(--accent)' }} />
          Median of {forecast.runs.toLocaleString()} simulated futures
        </span>
        <span className="legend-item">
          <span className="legend-swatch" style={{ background: 'var(--accent)', opacity: 0.3 }} />
          10th–90th percentile band
        </span>
      </div>
    </div>
  );
}
