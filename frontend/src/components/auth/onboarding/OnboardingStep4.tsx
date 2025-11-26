import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { ArrowLeft, Check } from "lucide-react";
import { RegistrationData } from "../RegisterForm";

const newsCategories = [
  { id: "Technology", label: "Technology" },
  { id: "Politics", label: "Politics" },
  { id: "Business", label: "Business" },
  { id: "Health", label: "Health" },
  { id: "Sports", label: "Sports" },
];

type Props = {
  data: Partial<RegistrationData>;
  onComplete: (data: Partial<RegistrationData>) => void;
  onBack: () => void;
};

export const OnboardingStep4 = ({ data, onComplete, onBack }: Props) => {
  const [preferences, setPreferences] = useState<Record<string, boolean>>(
    data.news_preferences || {}
  );
  const [isSubmitting, setIsSubmitting] = useState(false);

  const togglePreference = (id: string) => {
    setPreferences((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onComplete({ news_preferences: preferences });
    } catch (error) {
      // Error is already handled in parent, just reset submitting state
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="text-center mb-6">
        <h3 className="text-lg font-semibold mb-2">News Interests</h3>
        <p className="text-sm text-muted-foreground">
          Select topics you're interested in
        </p>
      </div>

      <div className="space-y-2">
        {newsCategories.map((category) => (
          <div
            key={category.id}
            className="flex items-center space-x-3 p-3 rounded-lg border hover:bg-accent/50 transition-colors"
          >
            <Checkbox
              id={category.id}
              checked={preferences[category.id] || false}
              onCheckedChange={() => togglePreference(category.id)}
            />
            <Label
              htmlFor={category.id}
              className="flex-1 cursor-pointer font-normal"
            >
              {category.label}
            </Label>
            {preferences[category.id] && (
              <Check className="h-4 w-4 text-primary" />
            )}
          </div>
        ))}
      </div>

      <div className="flex gap-2">
        <Button
          type="button"
          variant="outlined"
          onClick={onBack}
          className="flex-1"
          disabled={isSubmitting}
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>
        <Button
          type="submit"
          variant="filled"
          className="flex-1"
          disabled={isSubmitting}
        >
          {isSubmitting ? "Creating Account..." : "Complete"}
        </Button>
      </div>
    </form>
  );
};
