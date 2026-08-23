import { Plus, MessageSquare, Trash2 } from "lucide-react";
import { useConversations, useCreateConversation, useDeleteConversation } from "../../hooks/useConversations";
import { Spinner } from "../ui/Spinner";
import { Button } from "../ui/Button";
import { formatRelativeTime, truncate } from "../../utils/format";

interface Props {
  activeId: string | null;
  onSelect: (id: string | null) => void;
}

export function ConversationList({ activeId, onSelect }: Props) {
  const { data: conversations, isLoading } = useConversations();
  const create = useCreateConversation();
  const del = useDeleteConversation();

  const handleNew = async () => {
    const conv = await create.mutateAsync("New Conversation");
    onSelect(conv.id);
  };

  const handleDelete = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (confirm("Delete this conversation and all its documents?")) {
      del.mutate(id);
      if (activeId === id) onSelect(null);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-4 py-4 border-b border-base-700">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-md bg-indigo-500/20 flex items-center justify-center">
            <span className="text-indigo-400 text-xs font-bold">R</span>
          </div>
          <span className="text-sm font-semibold text-white">Agentic RAG</span>
        </div>
        <Button variant="primary" size="sm" onClick={handleNew} loading={create.isPending}>
          <Plus className="w-3.5 h-3.5" />New
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto scrollbar-thin py-2">
        {isLoading ? (
          <div className="flex justify-center py-8"><Spinner /></div>
        ) : !conversations?.length ? (
          <div className="px-4 py-8 text-center">
            <MessageSquare className="w-8 h-8 text-base-600 mx-auto mb-2" />
            <p className="text-sm text-slate-500">No conversations yet</p>
            <p className="text-xs text-base-600 mt-1">Click New to start</p>
          </div>
        ) : (
          conversations.map((conv) => {
            const isActive = conv.id === activeId;
            return (
              <div
                key={conv.id}
                role="button"
                tabIndex={0}
                onClick={() => onSelect(conv.id)}
                onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") onSelect(conv.id); }}
                className={`w-full group flex items-center gap-3 px-4 py-3 text-left transition-colors duration-100 cursor-pointer ${
                  isActive ? "bg-indigo-500/10 border-r-2 border-indigo-500" : "hover:bg-base-800"
                }`}
              >
                <MessageSquare className={`w-4 h-4 shrink-0 ${isActive ? "text-indigo-400" : "text-base-500"}`} />
                <div className="flex-1 min-w-0">
                  <p className={`text-sm font-medium truncate ${isActive ? "text-white" : "text-slate-300"}`}>
                    {truncate(conv.title, 30)}
                  </p>
                  <p className="text-xs text-slate-500 mt-0.5">{formatRelativeTime(conv.updated_at)}</p>
                </div>
                <button
                  onClick={(e) => handleDelete(e, conv.id)}
                  className="opacity-0 group-hover:opacity-100 p-1 rounded text-base-500 hover:text-rose-400 transition-all"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            );
          })
        )}
      </div>

      <div className="px-4 py-3 border-t border-base-700">
        <p className="text-xs text-base-600">
          {conversations?.length ?? 0} conversation{conversations?.length !== 1 ? "s" : ""}
        </p>
      </div>
    </div>
  );
}
