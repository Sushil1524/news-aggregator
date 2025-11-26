import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Article, Comment, commentsAPI } from "@/lib/api";
import { format } from "date-fns";
import { ExternalLink, MessageSquare } from "lucide-react";
import { CommentThread } from "./CommentThread";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/hooks/use-toast";

type Props = {
  article: Article | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

export const ArticleDialog = ({ article, open, onOpenChange }: Props) => {
  const { isAuthenticated } = useAuth();
  const { toast } = useToast();
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (article && open) {
      loadComments();
    }
  }, [article, open]);

  const loadComments = async () => {
    if (!article) return;
    try {
      const data = await commentsAPI.getComments(article._id);
      setComments(data);
    } catch (error) {
      console.error("Failed to load comments:", error);
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

  if (!article) return null;

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
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh]">
        <DialogHeader>
          <DialogTitle className="text-2xl pr-8">{article.title}</DialogTitle>
          <div className="flex flex-wrap items-center gap-2 pt-2">
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
        </DialogHeader>

        <ScrollArea className="h-[60vh] pr-4">
          <div className="space-y-6">
            {/* AI Summary */}
            {article.summary && (
              <div className="rounded-lg bg-primary/5 border border-primary/10 p-4">
                <h3 className="text-sm font-semibold mb-2 flex items-center gap-2">
                  <span className="inline-flex h-5 w-5 items-center justify-center rounded bg-primary/10 text-xs">
                    AI
                  </span>
                  Summary
                </h3>
                <p className="text-sm leading-relaxed">{article.summary}</p>
              </div>
            )}

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

            {/* Content */}
            <div className="prose prose-sm max-w-none">
              <p className="whitespace-pre-wrap leading-relaxed">
                {article.content}
              </p>
            </div>

            <Separator />

            {/* Comments Section */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                Comments ({comments.length})
              </h3>

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
                  className="min-h-[100px]"
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
              <div className="space-y-4">
                {comments
                  .filter((c) => !c.parent_id)
                  .map((comment) => (
                    <CommentThread
                      key={comment._id}
                      comment={comment}
                      allComments={comments}
                      onReload={loadComments}
                    />
                  ))}
              </div>
            </div>
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
};
