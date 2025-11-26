import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useInfiniteQuery, useQuery } from "@tanstack/react-query";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Hero } from "@/components/Hero";
import { Features } from "@/components/Features";
import { ArticleCard } from "@/components/feed/ArticleCard";
import { FeedFilters } from "@/components/feed/FeedFilters";
import { FeedTabs } from "@/components/feed/FeedTabs";
import { DateFilters, DateFilter } from "@/components/feed/DateFilters";
import { WelcomeBanner } from "@/components/WelcomeBanner";
import { JoinCard } from "@/components/feed/JoinCard";
import { TrendingTopics } from "@/components/feed/TrendingTopics";

import { UserStatsCard } from "@/components/feed/UserStatsCard";
import { Button } from "@/components/ui/button";
import { Article, articlesAPI, authAPI } from "@/lib/api";
import { RefreshCw, Search, SlidersHorizontal } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { Input } from "@/components/ui/input";
const Index = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const [showHero, setShowHero] = useState(true);
  const [sortBy, setSortBy] = useState<"hot" | "new" | "top">("hot");
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [dateFilter, setDateFilter] = useState<DateFilter>("all");
  const observerTarget = useRef<HTMLDivElement>(null);
  
  // Debounce search query
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
    }, 500);
    
    return () => clearTimeout(timer);
  }, [searchQuery]);
  
  // Get category from URL params
  const selectedCategory = searchParams.get("category") || undefined;

  const setSelectedCategory = useCallback((category?: string) => {
    if (category) {
      setSearchParams({ category });
    } else {
      setSearchParams({});
    }
  }, [setSearchParams]);

  // Fetch user preferences with React Query
  const { data: userProfile } = useQuery({
    queryKey: ['userProfile'],
    queryFn: () => authAPI.getProfile(),
    enabled: isAuthenticated,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });

  // Auto-select first preferred category if no category is selected
  useEffect(() => {
    if (userProfile?.news_preferences && !selectedCategory) {
      const preferredCategories = Object.keys(userProfile.news_preferences).filter(
        key => userProfile.news_preferences[key]
      );
      if (preferredCategories.length > 0) {
        setSelectedCategory(preferredCategories[0]);
      }
    }
  }, [userProfile, selectedCategory, setSelectedCategory]);

  // Fetch articles with infinite query
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    isError,
    refetch
  } = useInfiniteQuery({
    queryKey: ['articles', selectedCategory, sortBy, debouncedSearch, dateFilter],
    queryFn: ({ pageParam }) => articlesAPI.getArticles({
      limit: 20,
      category: selectedCategory,
      cursor: pageParam,
      search: debouncedSearch || undefined,
      sort_by: sortBy,
      date_filter: dateFilter !== "all" ? dateFilter : undefined
    }),
    getNextPageParam: (lastPage) => lastPage.next_cursor,
    initialPageParam: undefined,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });

  // Flatten articles from all pages
  const articles = data?.pages.flatMap(page => page.articles) || [];

  // Infinite scroll observer
  useEffect(() => {
    const observer = new IntersectionObserver(
      entries => {
        if (entries[0].isIntersecting && !isLoading && !isFetchingNextPage && hasNextPage) {
          fetchNextPage();
        }
      },
      { threshold: 0.1 }
    );

    const currentTarget = observerTarget.current;
    if (currentTarget) {
      observer.observe(currentTarget);
    }

    return () => {
      if (currentTarget) {
        observer.unobserve(currentTarget);
      }
    };
  }, [isLoading, isFetchingNextPage, hasNextPage, fetchNextPage]);
  return <div className="min-h-screen flex flex-col bg-background">
      <Header />
      <main className="flex-1">
        {/* Hero Section - only show when not authenticated */}
        {!isAuthenticated && showHero && <>
            <Hero />
            
          </>}

        {/* Welcome Banner */}
        <WelcomeBanner />

        {/* Feed Section */}
        <section className="py-6">
          <div className="container">
            <div className="grid grid-cols-1 lg:grid-cols-[240px_1fr_300px] gap-6">
              {/* Left Sidebar - Filters */}
              <aside className="hidden lg:block space-y-6">
                <div className="sticky top-24">
                  <FeedFilters selectedCategory={selectedCategory} onCategoryChange={setSelectedCategory} vertical />
                </div>
              </aside>

              {/* Main Feed */}
              <div className="space-y-4">
                {/* Search and Tabs */}
                <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
                  <FeedTabs selected={sortBy} onSelect={setSortBy} />
                  <div className="flex gap-2 w-full sm:w-auto">
                    <div className="relative flex-1 sm:w-64">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input placeholder="Search articles..." value={searchQuery} onChange={e => setSearchQuery(e.target.value)} className="pl-9 bg-surface border-border" />
                    </div>
                    <DateFilters selectedFilter={dateFilter} onFilterChange={setDateFilter} />
                  </div>
                </div>

                {/* Mobile Filters (visible only on small screens) */}
                <div className="lg:hidden">
                  <FeedFilters selectedCategory={selectedCategory} onCategoryChange={setSelectedCategory} />
                </div>

                {/* Articles */}
                {isLoading ? (
                  <div className="text-center py-12">
                    <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
                    <p className="text-muted-foreground">Loading articles...</p>
                  </div>
                ) : isError ? (
                  <div className="text-center py-12 bg-card rounded-lg border border-border">
                    <p className="text-muted-foreground mb-4">
                      Failed to load articles. Please try again.
                    </p>
                    <Button onClick={() => refetch()} variant="filled">Try Again</Button>
                  </div>
                ) : articles.length === 0 ? (
                  <div className="text-center py-12 bg-card rounded-lg border border-border">
                    <p className="text-muted-foreground mb-4">
                      No articles found.
                    </p>
                  </div>
                ) : (
                  <>
                    {articles.map(article => (
                      <ArticleCard 
                        key={article._id} 
                        article={article} 
                        onArticleClick={(article) => navigate(`/article/${article._id}`)} 
                      />
                    ))}
                    
                    {/* Infinite scroll trigger */}
                    <div ref={observerTarget} className="py-4">
                      {isFetchingNextPage && (
                        <div className="text-center">
                          <RefreshCw className="h-6 w-6 animate-spin mx-auto mb-2 text-primary" />
                          <p className="text-sm text-muted-foreground">Loading more...</p>
                        </div>
                      )}
                      {!hasNextPage && articles.length > 0 && (
                        <p className="text-center text-sm text-muted-foreground">
                          You've reached the end
                        </p>
                      )}
                    </div>
                  </>
                )}
              </div>

              {/* Right Sidebar */}
              <aside className="space-y-4">
                {isAuthenticated ? (
                  <>
                    <UserStatsCard />
                    <TrendingTopics />
                  </>
                ) : (
                  <>
                    <JoinCard />
                    <TrendingTopics />
                  </>
                )}
              </aside>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>;
};
export default Index;