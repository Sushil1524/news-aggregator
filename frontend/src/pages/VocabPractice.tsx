import { Header } from "@/components/Header";
import { useAuth } from "@/hooks/useAuth";
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { VocabCard, vocabAPI } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { 
  BookOpen, 
  CheckCircle2, 
  ChevronLeft, 
  ChevronRight,
  Trophy,
  Target
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { Skeleton } from "@/components/ui/skeleton";

export default function VocabPractice() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [cards, setCards] = useState<VocabCard[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showMeaning, setShowMeaning] = useState(false);
  const [loading, setLoading] = useState(true);
  const [practicedWords, setPracticedWords] = useState<string[]>([]);
  const [dailyTarget, setDailyTarget] = useState(10);
  const [isCompleting, setIsCompleting] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/auth?tab=login");
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    loadTodayCards();
  }, []);

  const loadTodayCards = async () => {
    try {
      setLoading(true);
      const data = await vocabAPI.getTodayCards();
      setCards(data.today_cards);
      setDailyTarget(data.daily_target);
    } catch (error) {
      toast({ 
        title: "Failed to load vocab cards", 
        variant: "destructive" 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleMarkLearned = () => {
    const currentWord = cards[currentIndex].word;
    if (!practicedWords.includes(currentWord)) {
      setPracticedWords([...practicedWords, currentWord]);
    }
    
    if (currentIndex < cards.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setShowMeaning(false);
    }
  };

  const handleNext = () => {
    if (currentIndex < cards.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setShowMeaning(false);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setShowMeaning(false);
    }
  };

  const handleCompletePractice = async () => {
    if (practicedWords.length === 0) {
      toast({ 
        title: "No words practiced", 
        description: "Mark at least one word as learned",
        variant: "destructive" 
      });
      return;
    }

    try {
      setIsCompleting(true);
      await vocabAPI.markPracticeDone(practicedWords);
      toast({ 
        title: "Practice completed! 🎉", 
        description: `You practiced ${practicedWords.length} words today` 
      });
      navigate("/");
    } catch (error) {
      toast({ 
        title: "Failed to save progress", 
        variant: "destructive" 
      });
    } finally {
      setIsCompleting(false);
    }
  };

  const currentCard = cards[currentIndex];
  const progress = cards.length > 0 ? ((currentIndex + 1) / cards.length) * 100 : 0;
  const practiceProgress = cards.length > 0 ? (practicedWords.length / dailyTarget) * 100 : 0;

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container py-8">
        <div className="max-w-3xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <BookOpen className="h-8 w-8" />
              Vocabulary Practice
            </h1>
            <div className="flex items-center gap-4">
              <Badge variant="secondary" className="flex items-center gap-1">
                <Target className="h-4 w-4" />
                {practicedWords.length}/{dailyTarget}
              </Badge>
              <Badge variant="secondary" className="flex items-center gap-1">
                <Trophy className="h-4 w-4" />
                Card {currentIndex + 1}/{cards.length}
              </Badge>
            </div>
          </div>

          {/* Practice Progress */}
          <div className="mb-8">
            <div className="flex justify-between text-sm text-muted-foreground mb-2">
              <span>Daily Target Progress</span>
              <span>{Math.round(practiceProgress)}%</span>
            </div>
            <Progress value={practiceProgress} className="h-2" />
          </div>

          {loading ? (
            <Card className="p-8">
              <Skeleton className="h-64 w-full" />
            </Card>
          ) : cards.length === 0 ? (
            <Card className="p-12 text-center">
              <CheckCircle2 className="h-16 w-16 mx-auto text-green-500 mb-4" />
              <h2 className="text-2xl font-semibold mb-2">All caught up! 🎉</h2>
              <p className="text-muted-foreground mb-6">
                You've completed all your vocab practice for today
              </p>
              <Button onClick={() => navigate("/")}>Back to Home</Button>
            </Card>
          ) : (
            <>
              {/* Flashcard */}
              <Card className="mb-6 min-h-[400px] flex flex-col">
                <CardContent className="flex-1 flex flex-col items-center justify-center p-12">
                  <div className="text-center w-full">
                    <Badge variant="outline" className="mb-6">
                      Level {currentCard.level}
                    </Badge>
                    
                    <h2 className="text-5xl font-bold mb-8">
                      {currentCard.word}
                    </h2>

                    {showMeaning ? (
                      <div className="space-y-6 animate-in fade-in duration-300">
                        {currentCard.meaning && (
                          <div>
                            <p className="text-sm text-muted-foreground mb-2">Meaning</p>
                            <p className="text-xl">{currentCard.meaning}</p>
                          </div>
                        )}
                        {currentCard.example && (
                          <div className="pt-4 border-t">
                            <p className="text-sm text-muted-foreground mb-2">Example</p>
                            <p className="text-lg italic">{currentCard.example}</p>
                          </div>
                        )}
                        
                        <Button 
                          onClick={handleMarkLearned}
                          className="mt-8"
                          size="lg"
                          disabled={practicedWords.includes(currentCard.word)}
                        >
                          <CheckCircle2 className="h-5 w-5 mr-2" />
                          {practicedWords.includes(currentCard.word) ? "Marked as Learned" : "Mark as Learned"}
                        </Button>
                      </div>
                    ) : (
                      <Button 
                        onClick={() => setShowMeaning(true)}
                        size="lg"
                        variant="outlined"
                      >
                        Show Meaning
                      </Button>
                    )}
                  </div>
                </CardContent>

                {/* Progress bar */}
                <div className="px-6 pb-4">
                  <Progress value={progress} className="h-1" />
                </div>
              </Card>

              {/* Navigation */}
              <div className="flex items-center justify-between">
                <Button
                  variant="outlined"
                  onClick={handlePrevious}
                  disabled={currentIndex === 0}
                >
                  <ChevronLeft className="h-4 w-4 mr-2" />
                  Previous
                </Button>

                <Button
                  onClick={handleCompletePractice}
                  disabled={isCompleting}
                  variant={practicedWords.length >= dailyTarget ? "default" : "secondary"}
                >
                  {isCompleting ? "Saving..." : "Complete Practice"}
                </Button>

                <Button
                  variant="outlined"
                  onClick={handleNext}
                  disabled={currentIndex === cards.length - 1}
                >
                  Next
                  <ChevronRight className="h-4 w-4 ml-2" />
                </Button>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
}
