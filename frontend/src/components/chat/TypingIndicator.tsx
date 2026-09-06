export function TypingIndicator() {
  return (
    <div className="flex items-start gap-2 sm:gap-3">
      <div className="w-6 h-6 sm:w-7 sm:h-7 rounded-full bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center shrink-0 mt-0.5">
        <span className="text-indigo-400 text-xs font-bold">AI</span>
      </div>
      <div className="bg-base-800 border border-base-700 rounded-2xl rounded-tl-sm px-4 py-3">
        <div className="flex items-center gap-1.5">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse-dot"
              style={{ animationDelay: `${i * 0.16}s` }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
