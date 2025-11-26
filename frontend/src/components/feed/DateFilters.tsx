import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { SlidersHorizontal, Check } from "lucide-react";
import { cn } from "@/lib/utils";

export type DateFilter = "all" | "last_hour" | "today" | "this_week" | "this_month" | "this_year";

type Props = {
  selectedFilter: DateFilter;
  onFilterChange: (filter: DateFilter) => void;
};

const filterOptions = [
  { value: "all" as const, label: "All time" },
  { value: "last_hour" as const, label: "Last hour" },
  { value: "today" as const, label: "Today" },
  { value: "this_week" as const, label: "This week" },
  { value: "this_month" as const, label: "This month" },
  { value: "this_year" as const, label: "This year" },
];

export const DateFilters = ({ selectedFilter, onFilterChange }: Props) => {
  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="outlined" size="icon" className="relative">
          <SlidersHorizontal className="h-4 w-4" />
          {selectedFilter !== "all" && (
            <span className="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-primary" />
          )}
        </Button>
      </SheetTrigger>
      <SheetContent side="right" className="w-[280px]">
        <SheetHeader>
          <SheetTitle>Search filters</SheetTitle>
        </SheetHeader>
        <div className="mt-6 space-y-1">
          <h3 className="text-sm font-semibold mb-3 text-muted-foreground uppercase">
            Upload Date
          </h3>
          <div className="space-y-1">
            {filterOptions.map((option) => (
              <Button
                key={option.value}
                variant="ghost"
                className={cn(
                  "w-full justify-between text-left font-normal",
                  selectedFilter === option.value && "bg-accent"
                )}
                onClick={() => onFilterChange(option.value)}
              >
                {option.label}
                {selectedFilter === option.value && (
                  <Check className="h-4 w-4" />
                )}
              </Button>
            ))}
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
};
