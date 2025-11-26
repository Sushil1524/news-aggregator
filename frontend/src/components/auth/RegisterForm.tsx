import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { OnboardingStep1 } from "./onboarding/OnboardingStep1";
import { OnboardingStep2 } from "./onboarding/OnboardingStep2";
import { OnboardingStep3 } from "./onboarding/OnboardingStep3";
import { OnboardingStep4 } from "./onboarding/OnboardingStep4";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/hooks/useAuth";
import { authAPI } from "@/lib/api";

export type RegistrationData = {
  email: string;
  username: string;
  password: string;
  full_name: string;
  dob: string;
  vocab_proficiency: "beginner" | "intermediate" | "advanced";
  daily_practice_target: number;
  news_preferences: Record<string, boolean>;
  role: "user";
  gamification: {
    points: number;
    streak: number;
  };
  vocab_cards: any[];
  bookmarks: any[];
};

export const RegisterForm = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState<Partial<RegistrationData>>({
    vocab_proficiency: "beginner",
    daily_practice_target: 10,
    news_preferences: {},
    role: "user",
    gamification: {
      points: 0,
      streak: 0,
    },
    vocab_cards: [],
    bookmarks: [],
  });
  const navigate = useNavigate();
  const { toast } = useToast();
  const { login } = useAuth();

  const updateFormData = (data: Partial<RegistrationData>) => {
    setFormData((prev) => ({ ...prev, ...data }));
  };

  const handleComplete = async () => {
    try {
      const response = await authAPI.register(formData as RegistrationData);
      login(response.access_token, response.refresh_token);
      
      toast({
        title: "Account created successfully!",
        description: "Welcome to NewsFlow. Let's get you started.",
      });
      
      navigate("/");
    } catch (error) {
      console.error("Registration error:", error);
      toast({
        title: "Registration failed",
        description: error instanceof Error ? error.message : "Please check your connection and try again.",
        variant: "destructive",
      });
      throw error; // Re-throw to prevent the onComplete callback from completing
    }
  };

  return (
    <div className="space-y-6">
      {/* Progress indicator */}
      <div className="flex items-center gap-2">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className={`h-1 flex-1 rounded-full transition-all duration-base ${
              i <= step ? "bg-primary" : "bg-muted"
            }`}
          />
        ))}
      </div>

      {/* Step content */}
      {step === 1 && (
        <OnboardingStep1
          data={formData}
          onNext={(data) => {
            updateFormData(data);
            setStep(2);
          }}
        />
      )}
      {step === 2 && (
        <OnboardingStep2
          data={formData}
          onNext={(data) => {
            updateFormData(data);
            setStep(3);
          }}
          onBack={() => setStep(1)}
        />
      )}
      {step === 3 && (
        <OnboardingStep3
          data={formData}
          onNext={(data) => {
            updateFormData(data);
            setStep(4);
          }}
          onBack={() => setStep(2)}
        />
      )}
      {step === 4 && (
        <OnboardingStep4
          data={formData}
          onComplete={(data) => {
            updateFormData(data);
            handleComplete();
          }}
          onBack={() => setStep(3)}
        />
      )}
    </div>
  );
};
