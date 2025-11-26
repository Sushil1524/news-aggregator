import { Header } from "@/components/Header";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/hooks/useAuth";
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { BookmarkIcon } from "lucide-react";
import { Article, bookmarksAPI } from "@/lib/api";
import { ArticleCard } from "@/components/feed/ArticleCard";
import { ArticleDialog } from "@/components/feed/ArticleDialog";
import { Skeleton } from "@/components/ui/skeleton";

export default function Bookmarks() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [bookmarks, setBookmarks] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/auth?tab=login");
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    const loadBookmarks = async () => {
      if (isAuthenticated) {
        try {
          setLoading(true);
          const data = await bookmarksAPI.getBookmarks();
          setBookmarks(data);
        } catch (error) {
          console.error("Failed to load bookmarks:", error);
        } finally {
          setLoading(false);
        }
      }
    };
    
    loadBookmarks();
  }, [isAuthenticated]);

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container py-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
            <BookmarkIcon className="h-8 w-8" />
            Bookmarks
          </h1>
          <p className="text-muted-foreground mb-8">
            Your saved articles for later reading
          </p>

          {loading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <Card key={i} className="p-4">
                  <Skeleton className="h-24 w-full" />
                </Card>
              ))}
            </div>
          ) : bookmarks.length === 0 ? (
            <Card>
              <CardHeader>
                <CardTitle>Saved Articles</CardTitle>
                <CardDescription>
                  Articles you've bookmarked will appear here
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <BookmarkIcon className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">No bookmarks yet</p>
                  <p className="text-sm text-muted-foreground mt-2">
                    Start bookmarking articles to build your reading list
                  </p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {bookmarks.map((article) => (
                <ArticleCard
                  key={article._id}
                  article={article}
                  onArticleClick={setSelectedArticle}
                  initialIsBookmarked={true}
                />
              ))}
            </div>
          )}
        </div>
      </main>
      
      {selectedArticle && (
        <ArticleDialog
          article={selectedArticle}
          open={!!selectedArticle}
          onOpenChange={(open) => !open && setSelectedArticle(null)}
        />
      )}
    </div>
  );
}
