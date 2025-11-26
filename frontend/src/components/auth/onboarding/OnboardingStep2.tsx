import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ArrowLeft } from "lucide-react";
import { RegistrationData } from "../RegisterForm";

type Props = {
  data: Partial<RegistrationData>;
  onNext: (data: Partial<RegistrationData>) => void;
  onBack: () => void;
};

export const OnboardingStep2 = ({ data, onNext, onBack }: Props) => {
  const [fullName, setFullName] = useState(data.full_name || "");
  const [dob, setDob] = useState(data.dob || "");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onNext({ full_name: fullName, dob });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="text-center mb-6">
        <h3 className="text-lg font-semibold mb-2">Tell Us About Yourself</h3>
        <p className="text-sm text-muted-foreground">
          Help us personalize your experience
        </p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="fullName">Full Name</Label>
        <Input
          id="fullName"
          type="text"
          placeholder="John Doe"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          required
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="dob">Date of Birth</Label>
        <Input
          id="dob"
          type="date"
          value={dob}
          onChange={(e) => setDob(e.target.value)}
          required
        />
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
