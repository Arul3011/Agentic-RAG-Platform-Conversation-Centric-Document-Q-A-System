import ReactMarkdown from "react-markdown";
import { User } from "lucide-react";
import { SourceCards } from "./SourceCard";
import { RetrievalBadge } from "./RetrievalBadge";
import { formatRelativeTime } from "../../utils/format";
import type { MessageWithSources } from "../../types";

interface Props { message: MessageWithSources }

export function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex items-start gap-2 sm:gap-3 justify-end animate-slide-up">
        <div className="max-w-[85%] sm:max-w-[75%]">
          <div className="bg-indigo-500/20 border border-indigo-500/30 rounded-2xl rounded-tr-sm px-3.5 sm:px-4 py-2.5 sm:py-3">
            <p className="text-sm text-white leading-relaxed whitespace-pre-wrap">{message.content}</p>
          </div>
          <p className="text-xs text-slate-600 mt-1 text-right">{formatRelativeTime(message.created_at)}</p>
        </div>
        <div className="w-6 h-6 sm:w-7 sm:h-7 rounded-full bg-base-700 border border-base-600 flex items-center justify-center shrink-0 mt-0.5">
          <User className="w-3 h-3 sm:w-3.5 sm:h-3.5 text-slate-400" />
        </div>
      </div>
    );
  }

  const retrieval = message.retrieval;
  const sources = message.sources ?? [];

  return (
    <div className="flex items-start gap-2 sm:gap-3 animate-slide-up">
      <div className="w-6 h-6 sm:w-7 sm:h-7 rounded-full bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center shrink-0 mt-0.5">
        <span className="text-indigo-400 text-xs font-bold">AI</span>
      </div>
      <div className="flex-1 min-w-0 max-w-full md:max-w-[80%]">
        <div className="bg-base-800 border border-base-700 rounded-2xl rounded-tl-sm px-3.5 sm:px-4 py-2.5 sm:py-3">
          <div className="text-sm text-slate-200 leading-relaxed prose-invert">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
          {sources.length > 0 && <SourceCards sources={sources} />}
        </div>
        <div className="flex items-center gap-2 mt-1.5">
          <p className="text-xs text-slate-600">{formatRelativeTime(message.created_at)}</p>
          {retrieval && (
            <>
              <span className="text-slate-700">·</span>
              <RetrievalBadge used={retrieval.used} strategy={retrieval.strategy} />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
