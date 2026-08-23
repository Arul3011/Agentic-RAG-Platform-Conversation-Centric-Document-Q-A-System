export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function formatRelativeTime(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const mins = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  return date.toLocaleDateString();
}

export function truncate(str: string, max: number): string {
  return str.length > max ? str.slice(0, max) + "…" : str;
}

export function strategyLabel(strategy: string): string {
  const map: Record<string, string> = {
    vector: "Semantic",
    keyword: "Keyword",
    metadata: "Metadata",
    hybrid: "Hybrid",
    none: "No retrieval",
  };
  return map[strategy] ?? strategy;
}

export function strategyColor(strategy: string): string {
  const map: Record<string, string> = {
    vector: "text-indigo-400 bg-indigo-400/10 border-indigo-400/20",
    keyword: "text-emerald-400 bg-emerald-400/10 border-emerald-400/20",
    metadata: "text-amber-400 bg-amber-400/10 border-amber-400/20",
    hybrid: "text-indigo-400 bg-indigo-400/10 border-indigo-400/20",
    none: "text-slate-400 bg-slate-400/10 border-slate-400/20",
  };
  return map[strategy] ?? "text-slate-400 bg-slate-400/10 border-slate-400/20";
}

export function fileTypeIcon(fileType: string): string {
  const map: Record<string, string> = {
    pdf: "📄",
    docx: "📝",
    txt: "📃",
    md: "📋",
  };
  return map[fileType] ?? "📁";
}
