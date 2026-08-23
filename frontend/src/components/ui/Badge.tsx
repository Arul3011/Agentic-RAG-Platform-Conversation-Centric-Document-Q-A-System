interface BadgeProps { children: React.ReactNode; className?: string }
export function Badge({ children, className = "" }: BadgeProps) {
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded border text-xs font-mono font-medium ${className}`}>
      {children}
    </span>
  );
}
