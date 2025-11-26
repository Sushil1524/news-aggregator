import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BookOpen, GraduationCap, FileText, Lock } from "lucide-react";
import { Link } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";

const studyTools = [
  { icon: BookOpen, label: "Daily Vocabulary Practice", path: "/vocab-practice" },
  { icon: GraduationCap, label: "Vocabulary Quiz", path: "/study-tools/vocabulary" },
  { icon: FileText, label: "Historical Summary", path: "/study-tools/summary" },
];

export const StudyToolsCard = () => {
  const { isAuthenticated } = useAuth();

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="text-base">Study Tools</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {studyTools.map((tool, index) => {
          const Icon = tool.icon;
          return (
            <Link
              key={index}
              to={isAuthenticated ? tool.path : "/auth?tab=register"}
              className="flex items-center justify-between p-3 rounded-md hover:bg-surface-variant/50 transition-colors group"
            >
              <div className="flex items-center gap-3">
                <Icon className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
                <span className="text-sm text-foreground">{tool.label}</span>
              </div>
              {!isAuthenticated && <Lock className="h-4 w-4 text-muted-foreground" />}
            </Link>
          );
        })}
        {!isAuthenticated && (
          <div className="pt-3 border-t border-border">
            <Button variant="text" size="sm" asChild className="w-full">
              <Link to="/auth?tab=register">Sign up to access study tools</Link>
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
