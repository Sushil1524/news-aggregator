import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { X } from "lucide-react";
import { useState } from "react";

export const WelcomeBanner = () => {
  const { isAuthenticated } = useAuth();
  const [dismissed, setDismissed] = useState(false);

  if (isAuthenticated || dismissed) return null;

  return (
    <div className="border-b border-border bg-surface-variant">
      <div className="container flex items-center justify-between py-4">
        <div>
          <h2 className="text-lg font-semibold text-foreground">
            Welcome to IntelliNews
          </h2>
          <p className="text-sm text-muted-foreground">
            You're viewing as a guest. Sign up for personalized recommendations, voting, and study tools.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="filled" size="sm" asChild>
            <Link to="/auth?tab=register">Get Started</Link>
          </Button>
          <button
            onClick={() => setDismissed(true)}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  );
};
