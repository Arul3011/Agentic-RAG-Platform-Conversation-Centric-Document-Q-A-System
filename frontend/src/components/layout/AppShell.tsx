import { useState } from "react";
import { ConversationList } from "../conversations/ConversationList";
import { ChatWindow } from "../chat/ChatWindow";
import { EmptyState } from "../ui/EmptyState";
import { MessageSquare, Menu } from "lucide-react";

export function AppShell() {
  const [activeConvId, setActiveConvId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => setSidebarOpen((v) => !v);

  const handleSelect = (id: string | null) => {
    setActiveConvId(id);
    setSidebarOpen(false);
  };

  return (
    <div className="flex h-full bg-base-900">
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/60 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-72 max-w-[85vw] flex flex-col border-r border-base-700 bg-base-950 transform transition-transform duration-300 ease-in-out lg:static lg:z-auto lg:w-60 lg:max-w-none lg:translate-x-0 lg:transition-none ${
          sidebarOpen ? "translate-x-0 shadow-2xl shadow-black/50" : "-translate-x-full"
        }`}
      >
        <ConversationList activeId={activeConvId} onSelect={handleSelect} onClose={() => setSidebarOpen(false)} />
      </aside>
      <div className="flex-1 min-w-0">
        {activeConvId ? (
          <ChatWindow conversationId={activeConvId} onToggleSidebar={toggleSidebar} />
        ) : (
          <div className="flex flex-col h-full">
            <div className="flex items-center gap-2 px-3 sm:px-5 py-3 border-b border-base-700 bg-base-900 lg:hidden">
              <button
                onClick={toggleSidebar}
                aria-label="Toggle conversation list"
                className="p-2 -ml-1 sm:-ml-2 rounded-lg text-slate-400 hover:text-white hover:bg-base-800 transition-colors"
              >
                <Menu className="w-4 h-4" />
              </button>
              <h2 className="text-sm font-semibold text-white truncate">Conversations</h2>
            </div>
            <div className="flex-1 flex items-center justify-center min-h-0">
              <EmptyState
                icon={<MessageSquare />}
                title="No conversation selected"
                description="Choose a conversation from the sidebar or create a new one to get started."
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
