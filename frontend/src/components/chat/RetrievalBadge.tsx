import { Zap, ZapOff } from "lucide-react";
import { Badge } from "../ui/Badge";
import { strategyLabel, strategyColor } from "../../utils/format";

interface Props { used: boolean; strategy: string }

export function RetrievalBadge({ used, strategy }: Props) {
  if (!used) {
    return (
      <Badge className="text-slate-600 bg-base-800 border-base-700">
        <ZapOff className="w-2.5 h-2.5" />No retrieval
      </Badge>
    );
  }
  return (
    <Badge className={strategyColor(strategy)}>
      <Zap className="w-2.5 h-2.5" />{strategyLabel(strategy)} search
    </Badge>
  );
}
