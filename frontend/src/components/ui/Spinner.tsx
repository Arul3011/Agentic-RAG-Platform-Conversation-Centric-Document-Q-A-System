interface SpinnerProps { size?: "sm" | "md" | "lg"; className?: string }
export function Spinner({ size = "md", className = "" }: SpinnerProps) {
  const sz = { sm: "w-3 h-3", md: "w-5 h-5", lg: "w-8 h-8" }[size];
  return <div className={`${sz} ${className} rounded-full border-2 border-base-600 border-t-indigo-500 animate-spin`} />;
}
