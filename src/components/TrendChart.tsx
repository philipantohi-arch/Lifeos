/** Lightweight SVG area/line chart — no charting dependency needed. */

interface Series {
  values: number[];
  color: string;
  label: string;
  fill?: boolean;
}

interface Props {
  series: Series[];
  height?: number;
  min?: number;
  max?: number;
  xLabels?: string[];
  yFormat?: (v: number) => string;
}

export function TrendChart({ series, height = 220, min, max, xLabels, yFormat }: Props) {
  const width = 720;
  const pad = { top: 12, right: 12, bottom: 24, left: 44 };
  const all = series.flatMap((s) => s.values);
  const lo = min ?? Math.floor(Math.min(...all) * 0.97);
  const hi = max ?? Math.ceil(Math.max(...all) * 1.03);
  const n = Math.max(...series.map((s) => s.values.length));

  const x = (i: number) => pad.left + (i / Math.max(n - 1, 1)) * (width - pad.left - pad.right);
  const y = (v: number) => pad.top + (1 - (v - lo) / Math.max(hi - lo, 1e-9)) * (height - pad.top - pad.bottom);

  const fmt = yFormat ?? ((v: number) => String(Math.round(v)));
  const gridLines = 4;

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
        {series.map((s, si) => {
          const pts = s.values.map((v, i) => `${x(i)},${y(v)}`).join(' ');
          const area = `${x(0)},${y(lo)} ${pts} ${x(s.values.length - 1)},${y(lo)}`;
          return (
            <g key={si}>
              {s.fill && <polygon points={area} fill={s.color} opacity={0.12} />}
              <polyline points={pts} fill="none" stroke={s.color} strokeWidth={2.5} strokeLinejoin="round" />
            </g>
          );
        })}
        {xLabels &&
          xLabels.map((lbl, i) => {
            const idx = Math.round((i / Math.max(xLabels.length - 1, 1)) * (n - 1));
            return (
              <text key={i} x={x(idx)} y={height - 6} textAnchor="middle" className="chart-tick">
                {lbl}
              </text>
            );
          })}
      </svg>
      <div className="chart-legend">
        {series.map((s) => (
          <span key={s.label} className="legend-item">
            <span className="legend-swatch" style={{ background: s.color }} />
            {s.label}
          </span>
        ))}
      </div>
    </div>
  );
}
