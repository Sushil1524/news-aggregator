import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  ArrowBigUp, 
  ArrowBigDown, 
  MessageSquare, 
  Bookmark, 
  ExternalLink,
  Eye,
  Calendar,
  Share2
} from "lucide-react";
import { Article } from "@/lib/api";
import { cn } from "@/lib/utils";
import { format } from "date-fns";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/hooks/use-toast";
import { articlesAPI, bookmarksAPI } from "@/lib/api";
import { ShareDialog } from "./ShareDialog";

type Props = {
  article: Article;
  onArticleClick?: (article: Article) => void;
  initialIsBookmarked?: boolean;
};

export const ArticleCard = ({ article, onArticleClick, initialIsBookmarked = false }: Props) => {
  const { isAuthenticated } = useAuth();
  const { toast } = useToast();
  const [votes, setVotes] = useState({ upvotes: article.upvotes, downvotes: article.downvotes });
  const [userVote, setUserVote] = useState<"up" | "down" | null>(null);
  const [isBookmarked, setIsBookmarked] = useState(initialIsBookmarked);
  const [isShareOpen, setIsShareOpen] = useState(false);

  const handleVote = async (type: "up" | "down") => {
    if (!isAuthenticated) {
      toast({ title: "Please login to vote", variant: "destructive" });
      return;
    }

    try {
      if (type === "up") {
        await articlesAPI.upvote(article._id);
        setVotes(prev => ({ 
          upvotes: prev.upvotes + (userVote === "up" ? -1 : 1),
          downvotes: userVote === "down" ? prev.downvotes - 1 : prev.downvotes
        }));
        setUserVote(userVote === "up" ? null : "up");
      } else {
        await articlesAPI.downvote(article._id);
        setVotes(prev => ({ 
          downvotes: prev.downvotes + (userVote === "down" ? -1 : 1),
          upvotes: userVote === "up" ? prev.upvotes - 1 : prev.upvotes
        }));
        setUserVote(userVote === "down" ? null : "down");
      }
    } catch (error) {
      toast({ title: "Failed to vote", variant: "destructive" });
    }
  };

  const handleBookmark = async () => {
    if (!isAuthenticated) {
      toast({ title: "Please login to bookmark", variant: "destructive" });
      return;
    }

    try {
      if (isBookmarked) {
        await bookmarksAPI.removeBookmark(article._id);
        setIsBookmarked(false);
        toast({ title: "Removed from bookmarks" });
      } else {
        await bookmarksAPI.addBookmark(article._id);
        setIsBookmarked(true);
        toast({ title: "Added to bookmarks" });
      }
    } catch (error) {
      toast({ title: "Failed to update bookmark", variant: "destructive" });
    }
  };

  const getSentimentColor = (sentiment?: string) => {
    switch (sentiment?.toLowerCase()) {
      case "positive":
        return "bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/20";
      case "negative":
        return "bg-red-500/10 text-red-700 dark:text-red-400 border-red-500/20";
      default:
        return "bg-blue-500/10 text-blue-700 dark:text-blue-400 border-blue-500/20";
    }
  };

  return (
    <>
      <Card className="group hover:shadow-elevation-4 hover:border-primary/20 transition-all duration-300 hover:-translate-y-0.5">
        <div className="flex gap-4 p-4">
          {/* Voting column */}
          <div className="flex flex-col items-center gap-1 pt-1">
            <Button
              variant="ghost"
              size="icon"
              className={cn("h-8 w-8", userVote === "up" && "text-primary")}
              onClick={() => handleVote("up")}
            >
              <ArrowBigUp className="h-5 w-5" />
            </Button>
            <span className="text-sm font-semibold">
              {votes.upvotes - votes.downvotes}
            </span>
            <Button
              variant="ghost"
              size="icon"
              className={cn("h-8 w-8", userVote === "down" && "text-destructive")}
              onClick={() => handleVote("down")}
            >
              <ArrowBigDown className="h-5 w-5" />
            </Button>
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            {/* Metadata */}
            <div className="flex flex-wrap items-center gap-2 mb-2 text-xs text-muted-foreground">
              {article.category && (
                <Badge variant="secondary" className="text-xs">
                  {article.category}
                </Badge>
              )}
              {article.sentiment && (
                <Badge className={getSentimentColor(article.sentiment)}>
                  {article.sentiment}
                </Badge>
              )}
              <span className="flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                {format(new Date(article.created_at), "MMM d, yyyy")}
              </span>
              <span className="flex items-center gap-1">
                <Eye className="h-3 w-3" />
                {article.views}
              </span>
            </div>

            {/* Title */}
            <h3 
              className="text-lg font-semibold mb-2 cursor-pointer hover:text-primary transition-colors line-clamp-2"
              onClick={() => onArticleClick?.(article)}
            >
              {article.title}
            </h3>

            {/* Summary */}
            {article.summary && (
              <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                {article.summary}
              </p>
            )}

            {/* Tags */}
            {article.tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mb-3">
                {article.tags.slice(0, 3).map((tag) => (
                  <Badge key={tag} variant="outline" className="text-xs">
                    #{tag}
                  </Badge>
                ))}
              </div>
            )}

            {/* Actions */}
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <Button
                variant="ghost"
                size="sm"
                className="h-8 gap-2"
                onClick={() => onArticleClick?.(article)}
              >
                <MessageSquare className="h-4 w-4" />
                {article.comments_count}
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className={cn("h-8 gap-2", isBookmarked && "text-primary")}
                onClick={handleBookmark}
              >
                <Bookmark className={cn("h-4 w-4", isBookmarked && "fill-current")} />
                Save
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="h-8 gap-2"
                onClick={() => setIsShareOpen(true)}
              >
                <Share2 className="h-4 w-4" />
                Share
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="h-8 gap-2"
                asChild
              >
                <a href={article.url} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="h-4 w-4" />
                  Source
                </a>
              </Button>
            </div>
          </div>

          {/* Image */}
          {article.image_url && (
            <div className="hidden sm:block shrink-0 ml-4">
              <img 
                src={article.image_url} 
                alt={article.title}
                className="h-24 w-24 object-cover rounded-md border bg-muted"
                onError={(e) => {
                  (e.target as HTMLImageElement).style.display = "none";
                }}
              />
            </div>
          )}
        </div>
      </Card>

      <ShareDialog
        isOpen={isShareOpen}
        onClose={() => setIsShareOpen(false)}
        articleUrl={window.location.origin + "/article/" + article._id}
        articleTitle={article.title}
      />
    </>
  );
};
