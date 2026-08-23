import { Spinner } from "./Spinner";
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "ghost" | "danger"; size?: "sm" | "md"; loading?: boolean;
}
export function Button({ variant = "ghost", size = "md", loading, children, className = "", ...props }: ButtonProps) {
  const base = "inline-flex items-center gap-2 font-medium transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-offset-base-900 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed";
  const variants = {
    primary: "bg-indigo-500 hover:bg-indigo-600 text-white focus:ring-indigo-500 shadow-lg shadow-indigo-500/20",
    ghost: "text-slate-400 hover:text-white hover:bg-base-700 focus:ring-base-600",
    danger: "text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 focus:ring-rose-500",
  };
  const sizes = { sm: "px-2.5 py-1.5 text-xs", md: "px-3.5 py-2 text-sm" };
  return (
    <button className={`${base} ${variants[variant]} ${sizes[size]} ${className}`} disabled={loading || props.disabled} {...props}>
      {loading && <Spinner size="sm" />}{children}
    </button>
  );
}
