import { FileText, Hash, BarChart2 } from "lucide-react";
import { Badge } from "../ui/Badge";
import { strategyLabel, strategyColor } from "../../utils/format";
import type { SourceInfo } from "../../types";

interface Props { sources: SourceInfo[] }

export function SourceCards({ sources }: Props) {
  if (!sources.length) return null;
  return (
    <div className="mt-3 animate-slide-up">
      <p className="text-xs text-slate-500 mb-2 flex items-center gap-1.5">
        <FileText className="w-3 h-3" />
        {sources.length} source{sources.length !== 1 ? "s" : ""} retrieved
      </p>
      <div className="flex flex-wrap gap-2">
        {sources.map((src) => (
          <div
            key={src.chunk_id}
            className="flex items-center gap-2 px-2.5 py-2 rounded-lg bg-base-800 border border-base-700 hover:border-indigo-500/40 hover:glow-indigo transition-all duration-200 group"
          >
            <span className="text-sm">📄</span>
            <div className="min-w-0">
              <p className="text-xs font-medium text-slate-300 truncate max-w-[140px]" title={src.document_name}>
                {src.document_name}
              </p>
              <div className="flex items-center gap-1.5 mt-0.5">
                {src.page_number && (
                  <span className="text-xs text-slate-600 flex items-center gap-0.5">
                    <Hash className="w-2.5 h-2.5" />p.{src.page_number}
                  </span>
                )}
                {src.similarity_score !== undefined && (
                  <span className="text-xs text-slate-600 flex items-center gap-0.5">
                    <BarChart2 className="w-2.5 h-2.5" />
                    {(src.similarity_score * 100).toFixed(0)}%
                  </span>
                )}
              </div>
            </div>
            <Badge className={strategyColor(src.retrieval_strategy)}>
              {strategyLabel(src.retrieval_strategy)}
            </Badge>
          </div>
        ))}
      </div>
    </div>
  );
}
