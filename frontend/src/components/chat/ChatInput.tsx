import { useState, useRef, useCallback } from "react";
import { Send, Paperclip } from "lucide-react";
import { Spinner } from "../ui/Spinner";

interface Props {
  onSend: (content: string) => void;
  onUploadClick: () => void;
  disabled?: boolean;
  loading?: boolean;
}

export function ChatInput({ onSend, onUploadClick, disabled, loading }: Props) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = useCallback(() => {
    const trimmed = value.trim();
    if (!trimmed || loading || disabled) return;
    onSend(trimmed);
    setValue("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }, [value, loading, disabled, onSend]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value);
    const el = e.target;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 160) + "px";
  };

  const canSend = value.trim().length > 0 && !loading && !disabled;

  return (
    <div className="border-t border-base-700 px-3 sm:px-4 py-2.5 sm:py-3 bg-base-900">
      <div className={`flex items-end gap-1.5 sm:gap-2 bg-base-800 border rounded-2xl px-2 sm:px-3 py-2 transition-colors duration-150 ${
        disabled ? "border-base-700 opacity-60" : "border-base-600 focus-within:border-indigo-500/50"
      }`}>
        <button
          onClick={onUploadClick}
          disabled={disabled}
          title="Upload document"
          aria-label="Upload document"
          className="p-2 sm:p-1.5 rounded-lg text-slate-500 hover:text-indigo-400 hover:bg-indigo-500/10 transition-colors disabled:opacity-40 shrink-0"
        >
          <Paperclip className="w-4 h-4" />
        </button>

        <textarea
          ref={textareaRef}
          value={value}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          disabled={disabled || loading}
          placeholder={disabled ? "Select a conversation to start" : "Ask anything about your documents…"}
          rows={1}
          className="flex-1 bg-transparent text-sm text-white placeholder-slate-600 resize-none outline-none leading-relaxed py-1 min-h-[24px] max-h-[160px] scrollbar-thin"
        />

        <button
          onClick={handleSend}
          disabled={!canSend}
          aria-label="Send message"
          className={`p-2 sm:p-1.5 rounded-lg transition-all duration-150 shrink-0 ${
            canSend
              ? "bg-indigo-500 text-white hover:bg-indigo-600 shadow-lg shadow-indigo-500/30"
              : "text-slate-600"
          }`}
        >
          {loading ? <Spinner size="sm" className="border-t-white" /> : <Send className="w-4 h-4" />}
        </button>
      </div>
      <p className="text-xs text-slate-700 mt-2 text-center hidden sm:block">
        Enter to send · Shift+Enter for new line · Attach documents with 📎
      </p>
    </div>
  );
}
