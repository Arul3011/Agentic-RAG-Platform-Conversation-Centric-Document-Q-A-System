import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { conversationsApi } from "../api/conversations";
import type { Message, MessageWithSources, ChatResponse } from "../types";
import { useState, useCallback } from "react";

export function useMessages(conversationId: string | null) {
  return useQuery({
    queryKey: ["messages", conversationId],
    queryFn: () => conversationsApi.getMessages(conversationId!),
    enabled: !!conversationId,
    staleTime: 0,
  });
}

export function useSendMessage(conversationId: string | null) {
  const qc = useQueryClient();
  const [pendingResponse, setPendingResponse] = useState<ChatResponse | null>(null);

  const mutation = useMutation({
    mutationFn: (content: string) =>
      conversationsApi.sendMessage(conversationId!, content),
    onMutate: async (content) => {
      await qc.cancelQueries({ queryKey: ["messages", conversationId] });

      const previousMessages = qc.getQueryData<Message[]>(["messages", conversationId]);

      qc.setQueryData<Message[]>(["messages", conversationId], (old) => [
        ...(old ?? []),
        {
          id: `optimistic-${Date.now()}`,
          conversation_id: conversationId!,
          role: "user",
          content,
          created_at: new Date().toISOString(),
        },
      ]);

      return { previousMessages };
    },
    onError: (_err, _content, context) => {
      if (context?.previousMessages) {
        qc.setQueryData(["messages", conversationId], context.previousMessages);
      }
    },
    onSuccess: (data) => {
      setPendingResponse(data);
      qc.invalidateQueries({ queryKey: ["messages", conversationId] });
      qc.invalidateQueries({ queryKey: ["conversations"] });
    },
  });

  const clearPending = useCallback(() => setPendingResponse(null), []);

  return { ...mutation, pendingResponse, clearPending };
}
