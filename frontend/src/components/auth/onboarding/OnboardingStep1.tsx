import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RegistrationData } from "../RegisterForm";

type Props = {
  data: Partial<RegistrationData>;
  onNext: (data: Partial<RegistrationData>) => void;
};

export const OnboardingStep1 = ({ data, onNext }: Props) => {
  const [email, setEmail] = useState(data.email || "");
  const [username, setUsername] = useState(data.username || "");
  const [password, setPassword] = useState(data.password || "");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onNext({ email, username, password });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="text-center mb-6">
        <h3 className="text-lg font-semibold mb-2">Create Your Account</h3>
        <p className="text-sm text-muted-foreground">
          Let's start with the basics
        </p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          placeholder="you@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="username">Username</Label>
        <Input
          id="username"
          type="text"
          placeholder="johndoe"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="password">Password</Label>
        <Input
          id="password"
          type="password"
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={8}
        />
        <p className="text-xs text-muted-foreground">
          Must be at least 8 characters
        </p>
      </div>

      <Button type="submit" variant="filled" className="w-full">
        Continue
      </Button>
    </form>
  );
};
