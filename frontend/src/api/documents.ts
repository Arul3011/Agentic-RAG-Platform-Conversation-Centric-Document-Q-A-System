import { apiClient } from "./client";
import type { Document } from "../types";

export const documentsApi = {
  list: async (conversationId: string): Promise<Document[]> => {
    const { data } = await apiClient.get(
      `/conversations/${conversationId}/documents`
    );
    return data;
  },

  get: async (conversationId: string, documentId: string): Promise<Document> => {
    const { data } = await apiClient.get(
      `/conversations/${conversationId}/documents/${documentId}`
    );
    return data;
  },

  upload: async (
    conversationId: string,
    file: File,
    onProgress?: (pct: number) => void
  ): Promise<Document> => {
    const form = new FormData();
    form.append("file", file);
    const { data } = await apiClient.post(
      `/conversations/${conversationId}/documents`,
      form,
      {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (e) => {
          if (onProgress && e.total) {
            onProgress(Math.round((e.loaded / e.total) * 100));
          }
        },
      }
    );
    return data;
  },

  delete: async (documentId: string): Promise<void> => {
    await apiClient.delete(`/conversations/documents/${documentId}`);
  },
};
