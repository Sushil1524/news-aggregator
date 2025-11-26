import { Clock, TrendingUp, Flame } from "lucide-react";
import { Button } from "@/components/ui/button";

type SortOption = "hot" | "new" | "top";

interface FeedTabsProps {
  selected: SortOption;
  onSelect: (option: SortOption) => void;
}

export const FeedTabs = ({ selected, onSelect }: FeedTabsProps) => {
  return (
    <div className="flex gap-2">
      <Button
        variant={selected === "hot" ? "filled" : "ghost"}
        size="sm"
        onClick={() => onSelect("hot")}
        className="gap-2"
      >
        <Flame className="h-4 w-4" />
        Hot
      </Button>
      <Button
        variant={selected === "new" ? "filled" : "ghost"}
        size="sm"
        onClick={() => onSelect("new")}
        className="gap-2"
      >
        <Clock className="h-4 w-4" />
        New
      </Button>
      <Button
        variant={selected === "top" ? "filled" : "ghost"}
        size="sm"
        onClick={() => onSelect("top")}
        className="gap-2"
      >
        <TrendingUp className="h-4 w-4" />
        Top
      </Button>
    </div>
  );
};
