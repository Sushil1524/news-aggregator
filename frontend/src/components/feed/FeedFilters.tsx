import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  X, 
  Newspaper, 
  Cpu, 
  Landmark, 
  Briefcase, 
  Stethoscope, 
  Trophy, 
  Film, 
  FlaskConical, 
  Gavel, 
  GraduationCap, 
  Leaf, 
  Plane, 
  Coffee, 
  Scroll, 
  Globe,
  LayoutGrid
} from "lucide-react";
import { cn } from "@/lib/utils";

const categories = [
  "Technology",
  "Politics",
  "Business",
  "Health",
  "Sports",
  "Entertainment",
  "Science",
  "Crime",
  "Education",
  "Environment",
  "Travel",
  "Lifestyle",
  "Obituary",
  "General",
];

const categoryIcons: Record<string, React.ElementType> = {
  "Technology": Cpu,
  "Politics": Landmark,
  "Business": Briefcase,
  "Health": Stethoscope,
  "Sports": Trophy,
  "Entertainment": Film,
  "Science": FlaskConical,
  "Crime": Gavel,
  "Education": GraduationCap,
  "Environment": Leaf,
  "Travel": Plane,
  "Lifestyle": Coffee,
  "Obituary": Scroll,
  "General": Globe,
};

type Props = {
  selectedCategory?: string;
  onCategoryChange: (category?: string) => void;
  vertical?: boolean;
};

export const FeedFilters = ({ selectedCategory, onCategoryChange, vertical = false }: Props) => {
  return (
    <div className="space-y-2">
      {!vertical && (
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold">Filter by Category</h3>
          {selectedCategory && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onCategoryChange(undefined)}
              className="h-8 gap-1 text-xs hover:text-destructive transition-colors"
            >
              Clear
              <X className="h-3 w-3" />
            </Button>
          )}
        </div>
      )}
      
      <div className={cn(
        "flex gap-1",
        vertical ? "flex-col" : "flex-wrap"
      )}>
        {/* All News Button */}
        <button
          onClick={() => onCategoryChange(undefined)}
          className={cn(
            "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 group",
            !selectedCategory 
              ? "bg-primary/10 text-primary" 
              : "text-muted-foreground hover:bg-surface-variant/50 hover:text-foreground",
            vertical ? "w-full justify-start" : "rounded-full border border-transparent"
          )}
        >
          <LayoutGrid className={cn(
            "h-4 w-4",
            !selectedCategory ? "text-primary" : "text-muted-foreground group-hover:text-primary"
          )} />
          All News
        </button>

        {categories.map((category) => {
          const Icon = categoryIcons[category] || Globe;
          const isSelected = selectedCategory === category;
          
          return (
            <button
              key={category}
              onClick={() => onCategoryChange(isSelected ? undefined : category)}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 group",
                isSelected 
                  ? "bg-primary/10 text-primary" 
                  : "text-muted-foreground hover:bg-surface-variant/50 hover:text-foreground",
                vertical ? "w-full justify-start" : "rounded-full border border-transparent"
              )}
            >
              <Icon className={cn(
                "h-4 w-4",
                isSelected ? "text-primary" : "text-muted-foreground group-hover:text-primary"
              )} />
              {category}
            </button>
          );
        })}
      </div>
    </div>
  );
};
