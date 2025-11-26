import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Slider } from "@/components/ui/slider";
import { ArrowLeft } from "lucide-react";
import { RegistrationData } from "../RegisterForm";

type Props = {
  data: Partial<RegistrationData>;
  onNext: (data: Partial<RegistrationData>) => void;
  onBack: () => void;
};

export const OnboardingStep3 = ({ data, onNext, onBack }: Props) => {
  const [vocabLevel, setVocabLevel] = useState<"beginner" | "intermediate" | "advanced">(
    data.vocab_proficiency || "beginner"
  );
  const [dailyTarget, setDailyTarget] = useState(data.daily_practice_target || 10);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onNext({
      vocab_proficiency: vocabLevel,
      daily_practice_target: dailyTarget,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="text-center mb-6">
        <h3 className="text-lg font-semibold mb-2">Study Preferences</h3>
        <p className="text-sm text-muted-foreground">
          Help us tailor your learning experience
        </p>
      </div>

      <div className="space-y-3">
        <Label>Vocabulary Proficiency Level</Label>
        <RadioGroup value={vocabLevel} onValueChange={(value: any) => setVocabLevel(value)}>
          <div className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-accent/50 transition-colors">
            <RadioGroupItem value="beginner" id="beginner" />
            <Label htmlFor="beginner" className="flex-1 cursor-pointer">
              <div className="font-medium">Beginner</div>
              <div className="text-xs text-muted-foreground">
                Starting to build vocabulary
              </div>
            </Label>
          </div>
          <div className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-accent/50 transition-colors">
            <RadioGroupItem value="intermediate" id="intermediate" />
            <Label htmlFor="intermediate" className="flex-1 cursor-pointer">
              <div className="font-medium">Intermediate</div>
              <div className="text-xs text-muted-foreground">
                Comfortable with common words
              </div>
            </Label>
          </div>
          <div className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-accent/50 transition-colors">
            <RadioGroupItem value="advanced" id="advanced" />
            <Label htmlFor="advanced" className="flex-1 cursor-pointer">
              <div className="font-medium">Advanced</div>
              <div className="text-xs text-muted-foreground">
                Strong vocabulary foundation
              </div>
            </Label>
          </div>
        </RadioGroup>
      </div>

      <div className="space-y-3">
        <Label>Daily Practice Target: {dailyTarget} words</Label>
        <Slider
          value={[dailyTarget]}
          onValueChange={(value) => setDailyTarget(value[0])}
          min={5}
          max={50}
          step={5}
          className="w-full"
        />
        <p className="text-xs text-muted-foreground">
          How many words do you want to practice daily?
        </p>
      </div>

      <div className="flex gap-2">
        <Button type="button" variant="outlined" onClick={onBack} className="flex-1">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>
        <Button type="submit" variant="filled" className="flex-1">
          Continue
        </Button>
      </div>
    </form>
  );
};
