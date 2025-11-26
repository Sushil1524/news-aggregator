import { Header } from "@/components/Header";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useAuth } from "@/hooks/useAuth";
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { useToast } from "@/hooks/use-toast";
import { authAPI } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { z } from "zod";

const profileSchema = z.object({
  full_name: z.string().trim().min(1, "Full name is required").max(100),
  email: z.string().trim().email("Invalid email address"),
  dob: z.string(),
  vocab_proficiency: z.enum(["beginner", "intermediate", "advanced"]),
  daily_practice_target: z.number().min(5).max(50),
  news_preferences: z.record(z.boolean()),
});

const passwordSchema = z.object({
  current_password: z.string().min(1, "Current password is required"),
  new_password: z.string().min(8, "Password must be at least 8 characters"),
  confirm_password: z.string(),
}).refine(data => data.new_password === data.confirm_password, {
  message: "Passwords don't match",
  path: ["confirm_password"],
});

export default function Profile() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [userData, setUserData] = useState<any>(null);
  
  const [formData, setFormData] = useState({
    username: "",
    full_name: "",
    email: "",
    dob: "",
    vocab_proficiency: "beginner" as "beginner" | "intermediate" | "advanced",
    daily_practice_target: 10,
    news_preferences: {} as Record<string, boolean>,
  });

  const [passwordData, setPasswordData] = useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/auth?tab=login");
    } else {
      loadUserData();
    }
  }, [isAuthenticated, navigate]);

  const loadUserData = async () => {
    try {
      setLoading(true);
      const data = await authAPI.getProfile();
      setUserData(data);
      setFormData({
        username: data.username,
        full_name: data.full_name,
        email: data.email,
        dob: data.dob,
        vocab_proficiency: data.vocab_proficiency,
        daily_practice_target: data.daily_practice_target,
        news_preferences: data.news_preferences,
      });
    } catch (error) {
      toast({ 
        title: "Failed to load profile", 
        description: "Please try again later",
        variant: "destructive" 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    try {
      // Validate form data
      const validatedData = profileSchema.parse(formData);
      
      setUpdating(true);
      await authAPI.updateProfile(validatedData);
      
      toast({ title: "Profile updated successfully" });
    } catch (error) {
      if (error instanceof z.ZodError) {
        const newErrors: Record<string, string> = {};
        error.errors.forEach((err) => {
          if (err.path[0]) {
            newErrors[err.path[0] as string] = err.message;
          }
        });
        setErrors(newErrors);
      } else {
        toast({ 
          title: "Failed to update profile", 
          variant: "destructive" 
        });
      }
    } finally {
      setUpdating(false);
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    try {
      // Validate password data
      passwordSchema.parse(passwordData);
      
      setUpdating(true);
      // TODO: Implement password change API
      await authAPI.updateProfile({ 
        password: passwordData.new_password 
      });
      
      toast({ title: "Password updated successfully" });
      setPasswordData({
        current_password: "",
        new_password: "",
        confirm_password: "",
      });
    } catch (error) {
      if (error instanceof z.ZodError) {
        const newErrors: Record<string, string> = {};
        error.errors.forEach((err) => {
          if (err.path[0]) {
            newErrors[err.path[0] as string] = err.message;
          }
        });
        setErrors(newErrors);
      } else {
        toast({ 
          title: "Failed to update password", 
          variant: "destructive" 
        });
      }
    } finally {
      setUpdating(false);
    }
  };

  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const handlePasswordInputChange = (field: string, value: string) => {
    setPasswordData(prev => ({
      ...prev,
      [field]: value
    }));
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container py-8">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-3xl font-bold mb-2">Profile Settings</h1>
          <p className="text-muted-foreground mb-8">
            Manage your account information and preferences
          </p>

          {loading ? (
            <Card>
              <CardHeader>
                <Skeleton className="h-6 w-48" />
                <Skeleton className="h-4 w-64 mt-2" />
              </CardHeader>
              <CardContent className="space-y-4">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </CardContent>
            </Card>
          ) : (
            <>
              {/* Personal Information */}
              <Card className="mb-6">
                <CardHeader>
                  <CardTitle>Personal Information</CardTitle>
                  <CardDescription>
                    Update your personal details and contact information
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSubmit} className="space-y-4">
                    {/* Username (Read-only) */}
                    <div className="space-y-2">
                      <Label htmlFor="username">Username</Label>
                      <Input
                        id="username"
                        value={formData.username}
                        disabled
                        className="bg-muted"
                      />
                      <p className="text-xs text-muted-foreground">
                        Username cannot be changed
                      </p>
                    </div>

                    {/* Full Name */}
                    <div className="space-y-2">
                      <Label htmlFor="full_name">Full Name</Label>
                      <Input
                        id="full_name"
                        value={formData.full_name}
                        onChange={(e) => handleChange("full_name", e.target.value)}
                        placeholder="John Doe"
                      />
                      {errors.full_name && (
                        <p className="text-sm text-destructive">{errors.full_name}</p>
                      )}
                    </div>

                    {/* Email */}
                    <div className="space-y-2">
                      <Label htmlFor="email">Email</Label>
                      <Input
                        id="email"
                        type="email"
                        value={formData.email}
                        onChange={(e) => handleChange("email", e.target.value)}
                        placeholder="john@example.com"
                      />
                      {errors.email && (
                        <p className="text-sm text-destructive">{errors.email}</p>
                      )}
                    </div>

                    {/* Date of Birth */}
                    <div className="space-y-2">
                      <Label htmlFor="dob">Date of Birth</Label>
                      <Input
                        id="dob"
                        type="date"
                        value={formData.dob}
                        onChange={(e) => handleChange("dob", e.target.value)}
                      />
                      {errors.dob && (
                        <p className="text-sm text-destructive">{errors.dob}</p>
                      )}
                    </div>

                    <Separator />

                    {/* Vocabulary Settings */}
                    <div className="space-y-4 pt-2">
                      <h3 className="text-lg font-semibold">Vocabulary Practice Settings</h3>
                      
                      <div className="space-y-2">
                        <Label htmlFor="vocab_proficiency">Proficiency Level</Label>
                        <Select
                          value={formData.vocab_proficiency}
                          onValueChange={(value: "beginner" | "intermediate" | "advanced") => 
                            handleChange("vocab_proficiency", value)
                          }
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="beginner">Beginner</SelectItem>
                            <SelectItem value="intermediate">Intermediate</SelectItem>
                            <SelectItem value="advanced">Advanced</SelectItem>
                          </SelectContent>
                        </Select>
                        {errors.vocab_proficiency && (
                          <p className="text-sm text-destructive">{errors.vocab_proficiency}</p>
                        )}
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="daily_practice_target">
                          Daily Practice Target (words per day)
                        </Label>
                        <Input
                          id="daily_practice_target"
                          type="number"
                          min="5"
                          max="50"
                          value={formData.daily_practice_target}
                          onChange={(e) => handleChange("daily_practice_target", parseInt(e.target.value))}
                        />
                        {errors.daily_practice_target && (
                          <p className="text-sm text-destructive">{errors.daily_practice_target}</p>
                        )}
                        <p className="text-xs text-muted-foreground">
                          Set between 5-50 words per day
                        </p>
                      </div>
                    </div>

                    <Button type="submit" className="w-full" disabled={updating}>
                      {updating ? "Saving..." : "Save Changes"}
                    </Button>
                  </form>
                </CardContent>
              </Card>

              {/* Change Password */}
              <Card>
                <CardHeader>
                  <CardTitle>Change Password</CardTitle>
                  <CardDescription>
                    Update your password to keep your account secure
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handlePasswordChange} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="current_password">Current Password</Label>
                      <Input
                        id="current_password"
                        type="password"
                        value={passwordData.current_password}
                        onChange={(e) => handlePasswordInputChange("current_password", e.target.value)}
                        placeholder="Enter current password"
                      />
                      {errors.current_password && (
                        <p className="text-sm text-destructive">{errors.current_password}</p>
                      )}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="new_password">New Password</Label>
                      <Input
                        id="new_password"
                        type="password"
                        value={passwordData.new_password}
                        onChange={(e) => handlePasswordInputChange("new_password", e.target.value)}
                        placeholder="Enter new password"
                      />
                      {errors.new_password && (
                        <p className="text-sm text-destructive">{errors.new_password}</p>
                      )}
                      <p className="text-xs text-muted-foreground">
                        Must be at least 8 characters
                      </p>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="confirm_password">Confirm New Password</Label>
                      <Input
                        id="confirm_password"
                        type="password"
                        value={passwordData.confirm_password}
                        onChange={(e) => handlePasswordInputChange("confirm_password", e.target.value)}
                        placeholder="Confirm new password"
                      />
                      {errors.confirm_password && (
                        <p className="text-sm text-destructive">{errors.confirm_password}</p>
                      )}
                    </div>

                    <Button type="submit" className="w-full" disabled={updating}>
                      {updating ? "Updating..." : "Update Password"}
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </main>
    </div>
  );
}
