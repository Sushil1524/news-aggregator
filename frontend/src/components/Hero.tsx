import { Button } from "@/components/ui/button";
import { ArrowRight, Brain, Sparkles, TrendingUp } from "lucide-react";
import { Link } from "react-router-dom";
export const Hero = () => {
  return <section className="relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-surface -z-10" />
      <div className="absolute inset-0 bg-gradient-primary opacity-5 -z-10" />
      
      <div className="container relative">
        
      </div>
    </section>;
};
const FeatureCard = ({
  icon,
  title,
  description
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) => {
  return <div className="flex flex-col items-center gap-3 rounded-xl bg-card p-6 shadow-elevation-2 hover:shadow-elevation-3 transition-all duration-base">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary">
        {icon}
      </div>
      <h3 className="font-semibold text-lg">{title}</h3>
      <p className="text-sm text-muted-foreground text-center">{description}</p>
    </div>;
};