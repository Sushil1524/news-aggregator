import { Header } from "@/components/Header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/hooks/useAuth";
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { analyticsAPI } from "@/lib/api";
import { BarChart3, BookOpen, Clock, TrendingUp, Calendar, ExternalLink } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

export default function Analytics() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
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
    if (!isAuthenticated) {
      navigate("/auth?tab=login");
      return;
    }
    loadUserStats();
  }, [isAuthenticated, navigate]);

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
      <div className="min-h-screen bg-background">
        <Header />
        <main className="container py-8">
          <p className="text-center text-muted-foreground">Loading analytics...</p>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container py-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-2">Analytics Dashboard</h1>
          <p className="text-muted-foreground mb-8">
            Track your reading habits and progress
          </p>

          {stats && (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Articles</CardTitle>
                  <BookOpen className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.articles_read_total}</div>
                  <p className="text-xs text-muted-foreground">Articles read</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Reading Streak</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.streak}</div>
                  <p className="text-xs text-muted-foreground">Consecutive days</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">This Week</CardTitle>
                  <Clock className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.articles_read_last_week}</div>
                  <p className="text-xs text-muted-foreground">Articles read recently</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Points</CardTitle>
                  <BarChart3 className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.points}</div>
                  <p className="text-xs text-muted-foreground">Total points earned</p>
                </CardContent>
              </Card>
            </div>
          )}

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Reading History
              </CardTitle>
            </CardHeader>
            <CardContent>
              {stats && stats.reading_history && stats.reading_history.length > 0 ? (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {stats.reading_history
                    .sort((a, b) => {
                      const dateA = a.timestamp ? new Date(a.timestamp).getTime() : 0;
                      const dateB = b.timestamp ? new Date(b.timestamp).getTime() : 0;
                      return dateB - dateA;
                    })
                    .map((entry, index) => (
                      <div
                        key={index}
                        className="flex items-start justify-between p-3 rounded-lg border border-border hover:bg-accent/50 transition-colors"
                      >
                        <div className="flex-1 space-y-1">
                          <div className="flex items-center gap-2">
                            <a
                              href={`/article/${entry.article_id}`}
                              className="text-sm font-medium text-foreground hover:text-primary hover:underline flex items-center gap-1"
                            >
                              Article
                              <ExternalLink className="h-3 w-3" />
                            </a>
                          </div>
                          <div className="flex items-center gap-3 text-xs text-muted-foreground">
                            {entry.timestamp && (
                              <span>
                                {formatDistanceToNow(new Date(entry.timestamp), { addSuffix: true })}
                              </span>
                            )}
                            {entry.reading_time_seconds && (
                              <span>• {Math.round(entry.reading_time_seconds / 60)} min read</span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              ) : (
                <p className="text-muted-foreground">
                  No reading history yet. Start reading articles to track your progress!
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
