import { useEffect, useRef, useState } from "react";
import { FileText, BookOpen, Menu } from "lucide-react";
import { MessageBubble } from "./MessageBubble";
import { TypingIndicator } from "./TypingIndicator";
import { ChatInput } from "./ChatInput";
import { DocumentPanel } from "../documents/DocumentPanel";
import { useMessages, useSendMessage } from "../../hooks/useMessages";
import { useConversation } from "../../hooks/useConversations";
import { Spinner } from "../ui/Spinner";
import { EmptyState } from "../ui/EmptyState";
import type { MessageWithSources } from "../../types";

interface Props { conversationId: string; onToggleSidebar?: () => void }

export function ChatWindow({ conversationId, onToggleSidebar }: Props) {
  const { data: conv } = useConversation(conversationId);
  const { data: messages, isLoading } = useMessages(conversationId);
  const { mutate: sendMsg, isPending, pendingResponse } = useSendMessage(conversationId);
  const [showDocs, setShowDocs] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Build enriched message list, attaching sources from last response
  const enrichedMessages: MessageWithSources[] = (messages ?? []).map((m) => {
    if (pendingResponse && m.id === pendingResponse.message.id) {
      return {
        ...m,
        sources: pendingResponse.sources,
        retrieval: pendingResponse.retrieval,
      };
    }
    return m;
  });

  // Scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [enrichedMessages.length, isPending]);

  const handleSend = (content: string) => {
    sendMsg(content);
  };

  return (
    <div className="flex h-full">
      {/* Main chat column */}
      <div className="flex flex-col flex-1 min-w-0">
        {/* Conversation header */}
        <div className="flex items-center justify-between gap-2 px-3 sm:px-5 py-3 border-b border-base-700 bg-base-900">
          <div className="flex items-center gap-2 min-w-0 flex-1">
            {onToggleSidebar && (
              <button
                onClick={onToggleSidebar}
                aria-label="Toggle conversation list"
                className="lg:hidden p-2 -ml-1 sm:-ml-2 rounded-lg text-slate-400 hover:text-white hover:bg-base-800 transition-colors shrink-0"
              >
                <Menu className="w-4 h-4" />
              </button>
            )}
            <div className="min-w-0">
              <h1 className="text-sm font-semibold text-white truncate">{conv?.title ?? "Conversation"}</h1>
              {conv?.summary && (
                <p className="text-xs text-slate-500 mt-0.5 truncate max-w-md" title={conv.summary}>
                  {conv.summary}
                </p>
              )}
            </div>
          </div>
          <button
            onClick={() => setShowDocs((v) => !v)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all shrink-0 ${
              showDocs
                ? "bg-indigo-500/20 text-indigo-400 border border-indigo-500/30"
                : "text-slate-400 hover:text-white hover:bg-base-800 border border-transparent"
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            Documents
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto scrollbar-thin px-3 sm:px-5 py-3 sm:py-5 space-y-4 sm:space-y-5">
          {isLoading ? (
            <div className="flex justify-center py-16"><Spinner size="lg" /></div>
          ) : !enrichedMessages.length ? (
            <EmptyState
              icon={<BookOpen />}
              title="Ask anything about your documents"
              description="Upload PDFs, Word docs, or text files using the Documents panel, then start a conversation."
              action={
                <button
                  onClick={() => setShowDocs(true)}
                  className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors"
                >
                  Open Documents →
                </button>
              }
            />
          ) : (
            <>
              {enrichedMessages.map((msg) => (
                <MessageBubble key={msg.id} message={msg} />
              ))}
              {isPending && <TypingIndicator />}
            </>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <ChatInput
          onSend={handleSend}
          onUploadClick={() => setShowDocs(true)}
          loading={isPending}
        />
      </div>

      {/* Documents panel */}
      {showDocs && (
        <div className="fixed inset-0 z-40 bg-base-900 md:static md:inset-auto md:z-auto md:w-72 md:shrink-0 md:border-l md:border-base-700 animate-slide-up flex flex-col shadow-2xl shadow-black/50">
          <DocumentPanel
            conversationId={conversationId}
            onClose={() => setShowDocs(false)}
          />
        </div>
      )}
    </div>
  );
}
