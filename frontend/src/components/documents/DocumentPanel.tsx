import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { FileText, Upload, Trash2, CheckCircle, AlertCircle, Loader2, X } from "lucide-react";
import { useDocuments, useUploadDocument, useDeleteDocument } from "../../hooks/useDocuments";
import { Spinner } from "../ui/Spinner";
import { Button } from "../ui/Button";
import { formatFileSize, formatRelativeTime, fileTypeIcon, processingStepLabel, processingDetail, estimateRemaining } from "../../utils/format";
import type { Document } from "../../types";

interface Props { conversationId: string; onClose?: () => void }

function StatusIcon({ status }: { status: Document["status"] }) {
  if (status === "ready") return <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />;
  if (status === "error") return <AlertCircle className="w-3.5 h-3.5 text-rose-400" />;
  if (status === "processing" || status === "pending")
    return <Loader2 className="w-3.5 h-3.5 text-indigo-400 animate-spin" />;
  return null;
}

function StatusLabel({ status }: { status: Document["status"] }) {
  const map = {
    ready: "text-emerald-400",
    error: "text-rose-400",
    processing: "text-indigo-400",
    pending: "text-slate-400",
  };
  return <span className={`text-xs font-medium ${map[status]}`}>{status}</span>;
}

function ProcessingProgress({ doc }: { doc: Document }) {
  const prog = doc.metadata?.processing_progress;
  const percent = prog?.percent ?? 0;
  const clamped = Math.max(0, Math.min(100, percent));
  const step = prog?.step ?? "Processing";
  const detail = processingDetail(prog?.chunks_processed, prog?.chunks_total);
  const remaining = estimateRemaining(doc.created_at, clamped);

  return (
    <div className="mt-1.5 space-y-1">
      <div className="flex items-center gap-1.5 text-xs">
        <Loader2 className="w-3 h-3 text-indigo-400 animate-spin shrink-0" />
        <span className="text-indigo-400 font-medium truncate">{processingStepLabel(step)}</span>
        <span className="text-slate-500 ml-auto shrink-0">{Math.round(clamped)}%</span>
      </div>
      <div className="w-full bg-base-700 rounded-full h-1.5 overflow-hidden">
        <div
          className="bg-indigo-500 h-full rounded-full transition-all duration-500"
          style={{ width: `${clamped}%` }}
        />
      </div>
      {(detail || remaining) && (
        <p className="text-xs text-slate-500 truncate">
          {detail}
          {detail && remaining ? " · " : ""}
          {remaining && `${remaining} remaining`}
        </p>
      )}
    </div>
  );
}

export function DocumentPanel({ conversationId, onClose }: Props) {
  const { data: docs, isLoading } = useDocuments(conversationId);
  const upload = useUploadDocument(conversationId);
  const del = useDeleteDocument(conversationId);
  const [dragError, setDragError] = useState("");

  const onDrop = useCallback(
    async (accepted: File[], rejected: { file: File }[]) => {
      setDragError("");
      if (rejected.length) {
        setDragError("Only PDF, DOCX, TXT, and MD files up to 25 MB are accepted.");
        return;
      }
      for (const file of accepted) {
        try { await upload.mutateAsync(file); }
        catch (e: unknown) { setDragError((e as Error).message); }
      }
    },
    [upload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "text/plain": [".txt"],
      "text/markdown": [".md"],
    },
    maxSize: 25 * 1024 * 1024,
    multiple: true,
  });

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-base-700">
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-indigo-400" />
          <span className="text-sm font-semibold text-white">Documents</span>
          {docs && (
            <span className="px-1.5 py-0.5 rounded-full bg-base-700 text-xs text-slate-400 font-mono">
              {docs.length}
            </span>
          )}
        </div>
        {onClose && (
          <button onClick={onClose} className="text-slate-500 hover:text-white transition-colors">
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Drop zone */}
      <div className="px-3 pt-3">
        <div
          {...getRootProps()}
          className={`relative border-2 border-dashed rounded-xl p-4 text-center transition-all duration-200 cursor-pointer ${
            isDragActive
              ? "border-indigo-500 bg-indigo-500/10 glow-indigo"
              : "border-base-600 hover:border-base-500 hover:bg-base-800"
          }`}
        >
          <input {...getInputProps()} />
          {upload.isPending ? (
            <div className="flex flex-col items-center gap-2">
              <Spinner />
              <p className="text-xs text-slate-400">
                Uploading{upload.progress > 0 ? ` ${upload.progress}%` : "…"}
              </p>
              {upload.progress > 0 && (
                <div className="w-full bg-base-700 rounded-full h-1">
                  <div
                    className="bg-indigo-500 h-1 rounded-full transition-all"
                    style={{ width: `${upload.progress}%` }}
                  />
                </div>
              )}
            </div>
          ) : (
            <div className="flex flex-col items-center gap-1.5">
              <Upload className={`w-5 h-5 ${isDragActive ? "text-indigo-400" : "text-slate-500"}`} />
              <p className="text-xs font-medium text-slate-400">
                {isDragActive ? "Drop to upload" : "Drag files or click to browse"}
              </p>
              <p className="text-xs text-slate-600">PDF · DOCX · TXT · MD · max 25 MB</p>
            </div>
          )}
        </div>
        {dragError && (
          <p className="mt-2 text-xs text-rose-400 flex items-center gap-1">
            <AlertCircle className="w-3 h-3 shrink-0" />{dragError}
          </p>
        )}
        {upload.isError && (
          <p className="mt-2 text-xs text-rose-400 flex items-center gap-1">
            <AlertCircle className="w-3 h-3 shrink-0" />{(upload.error as Error)?.message}
          </p>
        )}
      </div>

      {/* Document list */}
      <div className="flex-1 overflow-y-auto scrollbar-thin px-3 py-3 space-y-2">
        {isLoading ? (
          <div className="flex justify-center py-6"><Spinner /></div>
        ) : !docs?.length ? (
          <div className="py-6 text-center">
            <p className="text-xs text-slate-500">No documents uploaded yet.</p>
            <p className="text-xs text-slate-600 mt-0.5">Upload files to start asking questions.</p>
          </div>
        ) : (
          docs.map((doc) => (
            <div
              key={doc.id}
              className="group flex items-start gap-2.5 p-2.5 rounded-lg bg-base-800 border border-base-700 hover:border-base-600 transition-colors"
            >
              <span className="text-base mt-0.5">{fileTypeIcon(doc.file_type)}</span>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-slate-300 truncate" title={doc.file_name}>
                  {doc.file_name}
                </p>
                {doc.status === "processing" || doc.status === "pending" ? (
                  <ProcessingProgress doc={doc} />
                ) : (
                  <>
                    <div className="flex items-center gap-2 mt-1">
                      <StatusIcon status={doc.status} />
                      <StatusLabel status={doc.status} />
                      <span className="text-xs text-slate-600">·</span>
                      <span className="text-xs text-slate-600">{formatFileSize(doc.file_size)}</span>
                    </div>
                    <p className="text-xs text-slate-600 mt-0.5">{formatRelativeTime(doc.created_at)}</p>
                  </>
                )}
              </div>
              <button
                onClick={() => {
                  if (confirm(`Remove "${doc.file_name}" from this conversation?`))
                    del.mutate(doc.id);
                }}
                aria-label={`Remove ${doc.file_name}`}
                className="opacity-40 sm:opacity-0 sm:group-hover:opacity-100 p-2 sm:p-1 rounded text-slate-600 hover:text-rose-400 transition-all shrink-0"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
