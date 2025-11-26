import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { financeService, MarketIndex, StockDetail } from './financeService';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, TrendingUp, TrendingDown, Plus, ArrowRight } from 'lucide-react';
import { Skeleton } from "@/components/ui/skeleton";

const MarketDashboard = () => {
  const navigate = useNavigate();
  const [indices, setIndices] = useState<MarketIndex[]>([]);
  const [watchlist, setWatchlist] = useState<StockDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  // Default watchlist tickers
  const watchlistTickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS"];

  useEffect(() => {
    const fetchData = async () => {
      try {
        const indicesData = await financeService.getIndices();
        setIndices(indicesData);

        const watchlistData = await Promise.all(
          watchlistTickers.map(ticker => financeService.getStockDetails(ticker))
        );
        setWatchlist(watchlistData.filter(item => item !== null));
      } catch (error) {
        console.error("Failed to fetch market data", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery) {
      // For now, just navigate to the detail page of the searched ticker
      // In a real app, we'd show a dropdown
      navigate(`/finance/${searchQuery.toUpperCase()}`);
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-8 max-w-7xl">
      {/* Top Section: Indices */}
      <section className="overflow-x-auto pb-4">
        <div className="flex space-x-4 min-w-max">
          {loading ? (
            Array(4).fill(0).map((_, i) => (
              <Skeleton key={i} className="h-24 w-64 rounded-xl" />
            ))
          ) : (
            indices.map((index) => (
              <Card key={index.symbol} className="w-64 shrink-0 bg-card border-border">
                <CardContent className="p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div className="font-semibold text-lg">{index.name}</div>
                    <div className={`flex items-center ${index.isPositive ? 'text-green-500' : 'text-red-500'} bg-opacity-10 rounded px-2 py-0.5 text-sm font-medium`}>
                      {index.isPositive ? <TrendingUp size={14} className="mr-1" /> : <TrendingDown size={14} className="mr-1" />}
                      {Math.abs(index.changePercent).toFixed(2)}%
                    </div>
                  </div>
                  <div className="text-2xl font-bold">{index.price.toLocaleString()}</div>
                  <div className={`text-sm ${index.isPositive ? 'text-green-500' : 'text-red-500'}`}>
                    {index.change > 0 ? '+' : ''}{index.change.toFixed(2)}
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </section>

      {/* Middle Section: Search */}
      <section className="relative max-w-2xl mx-auto">
        <form onSubmit={handleSearch} className="relative">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-muted-foreground" />
          <Input 
            type="text" 
            placeholder="Search for stocks, ETFs and more" 
            className="pl-12 py-6 rounded-full text-lg bg-card border-border shadow-sm focus-visible:ring-primary"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </form>
      </section>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left: Watchlist */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">You may be interested in</h2>
            <Button variant="ghost" size="sm" className="text-muted-foreground">
              <Plus size={16} className="mr-1" /> Add to watchlist
            </Button>
          </div>
          
          <div className="space-y-1">
            {loading ? (
              Array(5).fill(0).map((_, i) => (
                <Skeleton key={i} className="h-16 w-full rounded-lg" />
              ))
            ) : (
              watchlist.map((stock) => (
                <div 
                  key={stock.symbol} 
                  onClick={() => navigate(`/finance/${stock.symbol}`)}
                  className="group flex items-center justify-between p-4 rounded-lg hover:bg-accent/50 cursor-pointer transition-colors border-b border-border last:border-0"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded bg-primary/10 flex items-center justify-center text-primary font-bold text-xs">
                      {stock.symbol.substring(0, 2)}
                    </div>
                    <div>
                      <div className="font-medium">{stock.name}</div>
                      <div className="text-xs text-muted-foreground">{stock.symbol}</div>
                    </div>
                  </div>
                  
                  {/* Mini Sparkline Placeholder */}
                  <div className="hidden sm:block w-24 h-8">
                    {/* We can add a mini chart here later if needed */}
                  </div>

                  <div className="text-right min-w-[100px]">
                    <div className="font-medium">₹{stock.price.toLocaleString()}</div>
                    <div className={`text-sm ${stock.isPositive ? 'text-green-500' : 'text-red-500'} bg-opacity-10 rounded px-2 py-0.5 inline-block mt-1`}>
                      {stock.isPositive ? '+' : ''}{stock.changePercent.toFixed(2)}%
                    </div>
                  </div>
                  
                  <Button variant="ghost" size="icon" className="opacity-0 group-hover:opacity-100 transition-opacity rounded-full">
                    <Plus size={18} />
                  </Button>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right: Market Trends & Portfolio */}
        <div className="space-y-6">
          <Card className="bg-card border-border">
            <CardContent className="p-6 space-y-4">
              <div className="w-10 h-10 rounded bg-blue-500/10 flex items-center justify-center text-blue-500 mb-2">
                <TrendingUp size={24} />
              </div>
              <h3 className="font-medium text-lg">Create a portfolio to view your investments in one place</h3>
              <Button className="w-full rounded-full" variant="outlined">
                <Plus size={16} className="mr-2" /> New portfolio
              </Button>
            </CardContent>
          </Card>

          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle>Market trends</CardTitle>
            </CardHeader>
            <CardContent className="p-6 pt-0">
              <div className="flex flex-wrap gap-2">
                {["Market indexes", "Most active", "Gainers", "Losers", "Climate leaders", "Crypto", "Currencies"].map((tag) => (
                  <Button key={tag} variant="outlined" size="sm" className="rounded-full text-xs h-8">
                    {tag}
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default MarketDashboard;
