interface Props<T extends string> {
  options: { id: T; label: string }[];
  value: T;
  onChange: (v: T) => void;
}

export function Segments<T extends string>({ options, value, onChange }: Props<T>) {
  return (
    <div className="segments">
      {options.map((o) => (
        <button
          key={o.id}
          className={`segment ${o.id === value ? 'active' : ''}`}
          onClick={() => onChange(o.id)}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}
