import { apiClient } from "./client";
import type { Conversation, Message, ChatResponse } from "../types";

export const conversationsApi = {
  list: async (): Promise<Conversation[]> => {
    const { data } = await apiClient.get("/conversations");
    return data;
  },

  create: async (title?: string): Promise<Conversation> => {
    const { data } = await apiClient.post("/conversations", {
      title: title || "New Conversation",
    });
    return data;
  },

  get: async (id: string): Promise<Conversation> => {
    const { data } = await apiClient.get(`/conversations/${id}`);
    return data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/conversations/${id}`);
  },

  getMessages: async (id: string): Promise<Message[]> => {
    const { data } = await apiClient.get(`/conversations/${id}/messages`);
    return data;
  },

  sendMessage: async (id: string, content: string): Promise<ChatResponse> => {
    const { data } = await apiClient.post(`/conversations/${id}/messages`, {
      content,
    });
    return data;
  },
};
