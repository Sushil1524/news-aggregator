import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { Article as ArticleType, Comment, articlesAPI, commentsAPI, bookmarksAPI } from "@/lib/api";
import { cn } from "@/lib/utils";
import { format } from "date-fns";
import { ExternalLink, MessageSquare, ArrowLeft, ArrowBigUp, ArrowBigDown, Bookmark, Share2 } from "lucide-react";
import { CommentThread } from "@/components/feed/CommentThread";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/hooks/use-toast";
import { ShareDialog } from "@/components/feed/ShareDialog";

export default function Article() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { toast } = useToast();
  const [article, setArticle] = useState<ArticleType | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [votes, setVotes] = useState({ upvotes: 0, downvotes: 0 });
  const [userVote, setUserVote] = useState<"up" | "down" | null>(null);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [isShareOpen, setIsShareOpen] = useState(false);

  useEffect(() => {
    if (id) {
      loadArticle();
      loadComments();
    }
  }, [id]);

  const loadArticle = async () => {
    if (!id) return;
    try {
      const data = await articlesAPI.getArticle(id);
      setArticle(data);
      setVotes({ upvotes: data.upvotes, downvotes: data.downvotes });
    } catch (error) {
      toast({ title: "Failed to load article", variant: "destructive" });
    } finally {
      setIsLoading(false);
    }
  };

  const loadComments = async () => {
    if (!id) return;
    try {
      const data = await commentsAPI.getComments(id);
      setComments(data);
    } catch (error) {
      console.error("Failed to load comments:", error);
    }
  };

  const handleVote = async (type: "up" | "down") => {
    if (!isAuthenticated) {
      toast({ title: "Please login to vote", variant: "destructive" });
      return;
    }

    if (!article) return;

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

    if (!article) return;

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

  const handleSubmitComment = async () => {
    if (!article || !newComment.trim() || !isAuthenticated) {
      if (!isAuthenticated) {
        toast({ title: "Please login to comment", variant: "destructive" });
      }
      return;
    }

    setIsSubmitting(true);
    try {
      await commentsAPI.createComment({
        article_id: article._id,
        content: newComment.trim(),
      });
      setNewComment("");
      await loadComments();
      toast({ title: "Comment posted successfully" });
    } catch (error) {
      toast({ title: "Failed to post comment", variant: "destructive" });
    } finally {
      setIsSubmitting(false);
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
    <div className="min-h-screen flex flex-col bg-background">
      <Header />
      <main className="flex-1 container mx-auto px-4 py-8 max-w-4xl">
        <Button
          variant="ghost"
          size="sm"
          className="mb-6"
          onClick={() => navigate(-1)}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>

        {isLoading ? (
          <div className="space-y-4">
            <Skeleton className="h-12 w-3/4" />
            <Skeleton className="h-6 w-1/2" />
            <Skeleton className="h-64 w-full" />
          </div>
        ) : article ? (
          <article className="space-y-6">
            {/* Article Header */}
            <header className="space-y-4">
              <h1 className="text-4xl font-bold leading-tight">{article.title}</h1>
              <div className="flex flex-wrap items-center gap-2">
                {article.category && (
                  <Badge variant="secondary">{article.category}</Badge>
                )}
                {article.sentiment && (
                  <Badge className={getSentimentColor(article.sentiment)}>
                    {article.sentiment}
                  </Badge>
                )}
                <span className="text-sm text-muted-foreground">
                  {format(new Date(article.created_at), "MMMM d, yyyy")}
                </span>
                <Button variant="outlined" size="sm" asChild>
                  <a href={article.url} target="_blank" rel="noopener noreferrer">
                    <ExternalLink className="h-4 w-4 mr-2" />
                    Read Original
                  </a>
                </Button>
              </div>
            </header>

            {/* AI Summary with Image */}
            {article.summary && (
              <div className="space-y-4">
                <h2 className="text-2xl font-semibold">Summary</h2>
                <div className={`flex gap-6 ${article.image_url ? 'flex-col md:flex-row' : ''}`}>
                  <div className={`prose prose-lg max-w-none dark:prose-invert ${article.image_url ? 'md:w-[65%]' : 'w-full'}`}>
                    {article.summary.split('\n').map((paragraph, index) => (
                      paragraph.trim() && (
                        <p key={index} className="leading-relaxed text-foreground">
                          {paragraph}
                        </p>
                      )
                    ))}
                  </div>
                  {article.image_url && (
                    <div className="md:w-[35%] flex-shrink-0">
                      <div className="rounded-lg overflow-hidden border border-border h-full">
                        <img 
                          src={article.image_url} 
                          alt={article.title}
                          className="w-full h-full object-cover"
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Engagement Actions */}
            <div className="flex items-center justify-between gap-4 py-4 border-y border-border">
              <div className="flex items-center gap-2 bg-accent/30 rounded-full px-4 py-2">
                <Button
                  variant="ghost"
                  size="icon"
                  className={cn("h-9 w-9 rounded-full hover:bg-accent", userVote === "up" && "text-primary")}
                  onClick={() => handleVote("up")}
                >
                  <ArrowBigUp className="h-5 w-5" />
                </Button>
                <span className="text-sm font-semibold min-w-[3rem] text-center">
                  {votes.upvotes - votes.downvotes}
                </span>
                <Button
                  variant="ghost"
                  size="icon"
                  className={cn("h-9 w-9 rounded-full hover:bg-accent", userVote === "down" && "text-destructive")}
                  onClick={() => handleVote("down")}
                >
                  <ArrowBigDown className="h-5 w-5" />
                </Button>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  className="gap-2 h-9"
                  onClick={() => setIsShareOpen(true)}
                >
                  <Share2 className="h-4 w-4" />
                  Share
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className={cn("gap-2 h-9", isBookmarked && "text-primary")}
                  onClick={handleBookmark}
                >
                  <Bookmark className={cn("h-4 w-4", isBookmarked && "fill-current")} />
                  {isBookmarked ? "Saved" : "Save"}
                </Button>
              </div>
            </div>

            {/* Tags */}
            {article.tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {article.tags.map((tag) => (
                  <Badge key={tag} variant="outline">
                    #{tag}
                  </Badge>
                ))}
              </div>
            )}

            <Separator className="my-8" />

            {/* Comments Section */}
            <section className="space-y-6">
              <h2 className="text-2xl font-semibold flex items-center gap-2">
                <MessageSquare className="h-6 w-6" />
                Comments ({comments.length})
              </h2>

              {/* Comment input */}
              <div className="space-y-2">
                <Textarea
                  placeholder={
                    isAuthenticated
                      ? "Share your thoughts..."
                      : "Please login to comment"
                  }
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  disabled={!isAuthenticated}
                  className="min-h-[120px]"
                />
                <div className="flex justify-end">
                  <Button
                    onClick={handleSubmitComment}
                    disabled={!newComment.trim() || isSubmitting || !isAuthenticated}
                  >
                    {isSubmitting ? "Posting..." : "Post Comment"}
                  </Button>
                </div>
              </div>

              {/* Comments list */}
              <div className="space-y-6">
                {comments.length > 0 ? (
                  comments
                    .filter((c) => !c.parent_id)
                    .map((comment) => (
                      <CommentThread
                        key={comment._id}
                        comment={comment}
                        allComments={comments}
                        onReload={loadComments}
                      />
                    ))
                ) : (
                  <p className="text-center text-muted-foreground py-8">
                    No comments yet. Be the first to share your thoughts!
                  </p>
                )}
              </div>
            </section>
          </article>
        ) : (
          <div className="text-center py-12">
            <p className="text-muted-foreground">Article not found</p>
          </div>
        )}
      </main>
      <Footer />
      
      {article && (
        <ShareDialog
          isOpen={isShareOpen}
          onClose={() => setIsShareOpen(false)}
          articleUrl={window.location.href}
          articleTitle={article.title}
        />
      )}
    </div>
  );
}
