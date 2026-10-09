export function DualRange({
  min,
  max,
  step,
  low,
  high,
  minLabel,
  maxLabel,
  onChange,
}: {
  min: number;
  max: number;
  step: number;
  low: number;
  high: number;
  minLabel: string;
  maxLabel: string;
  onChange: (low: number, high: number) => void;
}) {
  const span = max - min || 1;
  const left = ((low - min) / span) * 100;
  const width = ((high - low) / span) * 100;
  const lowOnTop = low === high && low > (min + max) / 2;

  return (
    <div className="dual-range">
      <div className="dual-range-track" />
      <div className="dual-range-fill" style={{ left: `${left}%`, width: `${width}%` }} />
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={low}
        aria-label={minLabel}
        style={{ zIndex: lowOnTop ? 5 : 3 }}
        onChange={(event) => onChange(Math.min(Number(event.target.value), high), high)}
      />
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={high}
        aria-label={maxLabel}
        style={{ zIndex: lowOnTop ? 4 : 5 }}
        onChange={(event) => onChange(low, Math.max(Number(event.target.value), low))}
      />
    </div>
  );
}
