import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, Eye, ArrowBigUp, BarChart2 } from "lucide-react";
import { useState, useEffect } from "react";
import { analyticsAPI, Article } from "@/lib/api";
import { Link } from "react-router-dom";
import { Badge } from "@/components/ui/badge";

export const TrendingTopics = () => {
  const [trendingArticles, setTrendingArticles] = useState<Article[]>([]);
  const [topCategories, setTopCategories] = useState<{ category: string; count: number }[]>([]);
  const [dailyCounts, setDailyCounts] = useState<{ _id: string; count: number }[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [trending, categories, daily] = await Promise.all([
        analyticsAPI.getTrending(5),
        analyticsAPI.getTopCategories(10),
        analyticsAPI.getDailyCounts(7)
      ]);
      setTrendingArticles(trending);
      setTopCategories(categories);
      setDailyCounts(daily);
    } catch (error) {
      console.error("Failed to load trending data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Trending Articles */}
      <Card className="bg-card border-border hover:shadow-elevation-2 transition-all duration-300">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <TrendingUp className="h-5 w-5 text-primary" />
            Trending Articles
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {isLoading ? (
            <p className="text-sm text-muted-foreground">Loading...</p>
          ) : trendingArticles.length === 0 ? (
            <p className="text-sm text-muted-foreground">No trending articles yet.</p>
          ) : (
            trendingArticles.map((article, index) => (
              <Link
                key={article._id}
                to={`/article/${article._id}`}
                className="flex items-start gap-3 group"
              >
                <span className="text-lg font-bold text-muted-foreground/50 w-4 leading-none mt-0.5">
                  {index + 1}
                </span>
                <div className="space-y-1">
                  <h4 className="text-sm font-medium leading-tight group-hover:text-primary transition-colors line-clamp-2">
                    {article.title}
                  </h4>
                  <div className="flex items-center gap-3 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Eye className="h-3 w-3" />
                      {article.views}
                    </span>
                    <span className="flex items-center gap-1">
                      <ArrowBigUp className="h-3 w-3" />
                      {article.upvotes}
                    </span>
                  </div>
                </div>
              </Link>
            ))
          )}
        </CardContent>
      </Card>

      {/* Popular Categories */}
      <Card className="bg-card border-border hover:shadow-elevation-2 transition-all duration-300">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <BarChart2 className="h-5 w-5 text-primary" />
            Popular Categories
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {isLoading ? (
              <p className="text-sm text-muted-foreground">Loading...</p>
            ) : topCategories.length === 0 ? (
               <p className="text-sm text-muted-foreground">No categories found.</p>
            ) : (
              topCategories.map((item) => (
                <Link
                  key={item.category}
                  to={`/?category=${item.category}`}
                  className="group"
                >
                  <Badge 
                    variant="secondary" 
                    className="hover:bg-primary/10 hover:text-primary transition-colors cursor-pointer"
                  >
                    {item.category}
                    <span className="ml-1.5 text-[10px] text-muted-foreground group-hover:text-primary/70">
                      {item.count}
                    </span>
                  </Badge>
                </Link>
              ))
            )}
          </div>
        </CardContent>
      </Card>

      {/* Daily Activity */}
      <Card className="bg-card border-border hover:shadow-elevation-2 transition-all duration-300">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <BarChart2 className="h-5 w-5 text-primary" />
            Daily Activity
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-end gap-2 h-24 w-full">
            {isLoading ? (
              <p className="text-sm text-muted-foreground">Loading...</p>
            ) : dailyCounts.length === 0 ? (
              <p className="text-sm text-muted-foreground">No activity data.</p>
            ) : (
              dailyCounts.map((day) => {
                const maxCount = Math.max(...dailyCounts.map(d => d.count));
                const heightPercentage = maxCount > 0 ? (day.count / maxCount) * 100 : 0;
                
                return (
                  <div key={day._id} className="flex-1 flex flex-col items-center gap-1 group">
                    <div 
                      className="w-full bg-primary/20 rounded-t-sm group-hover:bg-primary/40 transition-colors relative"
                      style={{ height: `${heightPercentage}%` }}
                    >
                      <span className="absolute -top-6 left-1/2 -translate-x-1/2 text-xs font-bold opacity-0 group-hover:opacity-100 transition-opacity bg-popover px-1.5 py-0.5 rounded shadow-sm">
                        {day.count}
                      </span>
                    </div>
                    <span className="text-[10px] text-muted-foreground truncate w-full text-center">
                      {new Date(day._id).toLocaleDateString('en-US', { weekday: 'narrow' })}
                    </span>
                  </div>
                );
              })
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
