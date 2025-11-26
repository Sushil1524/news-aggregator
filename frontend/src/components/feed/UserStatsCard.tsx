import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart3, BookOpen, Clock, TrendingUp } from "lucide-react";
import { useState, useEffect } from "react";
import { analyticsAPI } from "@/lib/api";

export const UserStatsCard = () => {
  const [stats, setStats] = useState<{
    username: string;
    points: number;
    streak: number;
    articles_read_total: number;
    articles_read_last_week: number;
    vocab_words_added: number;
    reading_history: Array<{
      timestamp: string;
      article_id: string;
      reading_time_seconds?: number | null;
    }>;
  } | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadUserStats();
  }, []);

  const loadUserStats = async () => {
    try {
      const data = await analyticsAPI.getUserDashboard();
      setStats(data);
    } catch (error) {
      console.error("Failed to load user stats:", error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <BarChart3 className="h-5 w-5 text-primary" />
            Your Stats
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Loading...</p>
        </CardContent>
      </Card>
    );
  }

  if (!stats) {
    return null;
  }

  return (
    <Card className="bg-card border-border hover:shadow-elevation-2 transition-all duration-300">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <BarChart3 className="h-5 w-5 text-primary" />
          Your Stats
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-muted-foreground">
              <BookOpen className="h-4 w-4" />
              <span className="text-xs">Articles Read</span>
            </div>
            <p className="text-2xl font-bold text-foreground">{stats.articles_read_total}</p>
          </div>
          
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-muted-foreground">
              <TrendingUp className="h-4 w-4" />
              <span className="text-xs">Streak</span>
            </div>
            <p className="text-2xl font-bold text-foreground">{stats.streak}</p>
          </div>
        </div>

        <div className="space-y-1">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Clock className="h-4 w-4" />
            <span className="text-xs">This Week</span>
          </div>
          <p className="text-lg font-semibold text-foreground">{stats.articles_read_last_week} articles</p>
        </div>

        <div className="pt-3 border-t border-border">
          <p className="text-xs text-muted-foreground mb-1">Total Points</p>
          <p className="text-sm font-medium text-primary">{stats.points}</p>
        </div>
      </CardContent>
    </Card>
  );
};
