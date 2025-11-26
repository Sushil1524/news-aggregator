import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ArrowBigUp, ArrowBigDown, Reply, Trash2 } from "lucide-react";
import { Comment, commentsAPI } from "@/lib/api";
import { format } from "date-fns";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/hooks/use-toast";

type Props = {
  comment: Comment;
  allComments: Comment[];
  onReload: () => void;
  depth?: number;
};

export const CommentThread = ({ comment, allComments, onReload, depth = 0 }: Props) => {
  const { isAuthenticated } = useAuth();
  const { toast } = useToast();
  const [showReply, setShowReply] = useState(false);
  const [replyText, setReplyText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [votes, setVotes] = useState({ upvotes: comment.upvotes, downvotes: comment.downvotes });
  const [userVote, setUserVote] = useState<"up" | "down" | null>(null);

  const replies = allComments.filter((c) => c.parent_id === comment._id);

  const handleVote = async (type: "up" | "down") => {
    if (!isAuthenticated) {
      toast({ title: "Please login to vote", variant: "destructive" });
      return;
    }

    try {
      if (type === "up") {
        await commentsAPI.upvote(comment._id);
        setVotes(prev => ({ 
          upvotes: prev.upvotes + (userVote === "up" ? -1 : 1),
          downvotes: userVote === "down" ? prev.downvotes - 1 : prev.downvotes
        }));
        setUserVote(userVote === "up" ? null : "up");
      } else {
        await commentsAPI.downvote(comment._id);
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

  const handleReply = async () => {
    if (!replyText.trim()) return;

    setIsSubmitting(true);
    try {
      await commentsAPI.createComment({
        article_id: comment.article_id,
        content: replyText.trim(),
        parent_id: comment._id,
      });
      setReplyText("");
      setShowReply(false);
      await onReload();
      toast({ title: "Reply posted successfully" });
    } catch (error) {
      toast({ title: "Failed to post reply", variant: "destructive" });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    try {
      await commentsAPI.deleteComment(comment._id);
      await onReload();
      toast({ title: "Comment deleted" });
    } catch (error) {
      toast({ title: "Failed to delete comment", variant: "destructive" });
    }
  };

  return (
    <div className={cn("space-y-3", depth > 0 && "ml-8 pl-4 border-l-2 border-border")}>
      <div className="flex gap-3">
        {/* Vote column */}
        <div className="flex flex-col items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            className={cn("h-6 w-6", userVote === "up" && "text-primary")}
            onClick={() => handleVote("up")}
          >
            <ArrowBigUp className="h-4 w-4" />
          </Button>
          <span className="text-xs font-semibold">
            {votes.upvotes - votes.downvotes}
          </span>
          <Button
            variant="ghost"
            size="icon"
            className={cn("h-6 w-6", userVote === "down" && "text-destructive")}
            onClick={() => handleVote("down")}
          >
            <ArrowBigDown className="h-4 w-4" />
          </Button>
        </div>

        {/* Comment content */}
        <div className="flex-1 space-y-2">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span className="font-medium text-foreground">{comment.author_email}</span>
            <span>•</span>
            <span>{format(new Date(comment.created_at), "MMM d, h:mm a")}</span>
          </div>
          <p className="text-sm leading-relaxed">{comment.content}</p>
          <div className="flex items-center gap-2">
            {depth < 3 && (
              <Button
                variant="ghost"
                size="sm"
                className="h-7 text-xs gap-1"
                onClick={() => setShowReply(!showReply)}
              >
                <Reply className="h-3 w-3" />
                Reply
              </Button>
            )}
            <Button
              variant="ghost"
              size="sm"
              className="h-7 text-xs gap-1 text-destructive hover:text-destructive"
              onClick={handleDelete}
            >
              <Trash2 className="h-3 w-3" />
              Delete
            </Button>
          </div>

          {/* Reply input */}
          {showReply && (
            <div className="space-y-2 pt-2">
              <Textarea
                placeholder="Write a reply..."
                value={replyText}
                onChange={(e) => setReplyText(e.target.value)}
                className="min-h-[80px] text-sm"
              />
              <div className="flex gap-2">
                <Button
                  size="sm"
                  onClick={handleReply}
                  disabled={!replyText.trim() || isSubmitting}
                >
                  {isSubmitting ? "Posting..." : "Post Reply"}
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => {
                    setShowReply(false);
                    setReplyText("");
                  }}
                >
                  Cancel
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Nested replies */}
      {replies.length > 0 && (
        <div className="space-y-3">
          {replies.map((reply) => (
            <CommentThread
              key={reply._id}
              comment={reply}
              allComments={allComments}
              onReload={onReload}
              depth={depth + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
};
