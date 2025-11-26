import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { Sparkles, TrendingUp, BookOpen } from "lucide-react";

export const JoinCard = () => {
  const { isAuthenticated } = useAuth();

  if (isAuthenticated) return null;

  return (
    <Card className="bg-card border-border hover:shadow-elevation-2 transition-all duration-300">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Sparkles className="h-5 w-5 text-primary" />
          Join IntelliNews
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-muted-foreground">
          Track your reading progress, build vocabulary, and access personalized study tools.
        </p>
        <div className="space-y-2">
          <div className="flex items-start gap-2">
            <TrendingUp className="h-4 w-4 text-primary mt-0.5" />
            <span className="text-xs text-foreground">Progress Tracking</span>
          </div>
          <div className="flex items-start gap-2">
            <BookOpen className="h-4 w-4 text-primary mt-0.5" />
            <span className="text-xs text-foreground">Vocabulary Builder</span>
          </div>
        </div>
        <Button variant="filled" size="sm" className="w-full" asChild>
          <Link to="/auth?tab=register">Sign Up Free</Link>
        </Button>
      </CardContent>
    </Card>
  );
};
