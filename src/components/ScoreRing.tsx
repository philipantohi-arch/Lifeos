interface Props {
  score: number;
  delta: number;
  size?: number;
  label?: string;
}

export function ScoreRing({ score, delta, size = 200, label = 'Life Score' }: Props) {
  const stroke = size * 0.055;
  const r = (size - stroke) / 2 - 4;
  const c = 2 * Math.PI * r;
  const filled = c * (score / 100);

  const color = score >= 75 ? 'var(--green)' : score >= 55 ? 'var(--amber)' : 'var(--red)';

  return (
    <div className="score-ring" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <defs>
          <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="var(--accent)" />
            <stop offset="100%" stopColor={color} />
          </linearGradient>
        </defs>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="var(--ring-track)"
          strokeWidth={stroke}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="url(#ringGrad)"
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={`${filled} ${c - filled}`}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          className="ring-fill"
        />
      </svg>
      <div className="score-ring-center">
        <div className="score-value">{score}</div>
        <div className="score-label">{label}</div>
        <div className={`score-delta ${delta >= 0 ? 'up' : 'down'}`}>
          {delta >= 0 ? '▲' : '▼'} {Math.abs(delta).toFixed(1)} today
        </div>
      </div>
    </div>
  );
}
