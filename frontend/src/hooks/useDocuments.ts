import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { documentsApi } from "../api/documents";
import { useState } from "react";

export function useDocuments(conversationId: string | null) {
  return useQuery({
    queryKey: ["documents", conversationId],
    queryFn: () => documentsApi.list(conversationId!),
    enabled: !!conversationId,
    staleTime: 30_000,
    refetchInterval: (query) => {
      const docs = query.state.data;
      const hasProcessing = docs?.some(
        (d) => d.status === "pending" || d.status === "processing"
      );
      return hasProcessing ? 3000 : false;
    },
  });
}

export function useUploadDocument(conversationId: string | null) {
  const qc = useQueryClient();
  const [progress, setProgress] = useState(0);

  const mutation = useMutation({
    mutationFn: (file: File) =>
      documentsApi.upload(conversationId!, file, setProgress),
    onSuccess: () => {
      setProgress(0);
      qc.invalidateQueries({ queryKey: ["documents", conversationId] });
    },
    onError: () => setProgress(0),
  });

  return { ...mutation, progress };
}

export function useDeleteDocument(conversationId: string | null) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => documentsApi.delete(id),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ["documents", conversationId] }),
  });
}
