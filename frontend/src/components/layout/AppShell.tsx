import { useState } from "react";
import { ConversationList } from "../conversations/ConversationList";
import { ChatWindow } from "../chat/ChatWindow";
import { EmptyState } from "../ui/EmptyState";
import { MessageSquare } from "lucide-react";

export function AppShell() {
  const [activeConvId, setActiveConvId] = useState<string | null>(null);

  return (
    <div className="flex h-full bg-base-900">
      <div className="w-60 shrink-0 border-r border-base-700 bg-base-950 flex flex-col">
        <ConversationList activeId={activeConvId} onSelect={setActiveConvId} />
      </div>
      <div className="flex-1 min-w-0">
        {activeConvId ? (
          <ChatWindow conversationId={activeConvId} />
        ) : (
          <div className="flex h-full items-center justify-center">
            <EmptyState
              icon={<MessageSquare />}
              title="No conversation selected"
              description="Choose a conversation from the sidebar or create a new one to get started."
            />
          </div>
        )}
      </div>
    </div>
  );
}
