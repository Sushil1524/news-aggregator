import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { financeService, StockDetail as StockDetailType } from './financeService';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowLeft, Plus, Share2 } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';

const StockDetail = () => {
  const { ticker } = useParams<{ ticker: string }>();
  const navigate = useNavigate();
  const [stock, setStock] = useState<StockDetailType | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState("1M");

  useEffect(() => {
    const fetchStock = async () => {
      if (!ticker) return;
      setLoading(true);
      try {
        const data = await financeService.getStockDetails(ticker);
        setStock(data);
      } catch (error) {
        console.error("Failed to fetch stock details", error);
      } finally {
        setLoading(false);
      }
    };

    fetchStock();
  }, [ticker]);

  if (loading) {
    return (
      <div className="container mx-auto p-6 space-y-6 max-w-7xl">
        <Skeleton className="h-12 w-1/3" />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <Skeleton className="h-96 lg:col-span-2" />
          <Skeleton className="h-96" />
        </div>
      </div>
    );
  }

  if (!stock) {
    return (
      <div className="container mx-auto p-6 text-center">
        <h2 className="text-2xl font-bold">Stock not found</h2>
        <Button onClick={() => navigate('/finance')} className="mt-4">Back to Dashboard</Button>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6 max-w-7xl">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-2 text-muted-foreground mb-1">
            <span className="cursor-pointer hover:text-foreground" onClick={() => navigate('/finance')}>MARKETS</span>
            <span>•</span>
            <span>INDIA</span>
            <span>•</span>
            <span>{stock.symbol}</span>
          </div>
          <h1 className="text-3xl font-bold">{stock.name}</h1>
        </div>
        <div className="flex gap-2">
          <Button variant="outlined" size="sm">
            <Plus size={16} className="mr-2" /> Follow
          </Button>
          <Button variant="outlined" size="sm">
            <Share2 size={16} className="mr-2" /> Share
          </Button>
        </div>
      </div>

      {/* Price Section */}
      <div className="flex items-baseline gap-4">
        <span className="text-4xl font-light">₹{stock.price.toLocaleString()}</span>
        <span className={`text-lg font-medium ${stock.isPositive ? 'text-green-500' : 'text-red-500'} bg-opacity-10 rounded px-2 py-1`}>
          {stock.isPositive ? '↑' : '↓'} {Math.abs(stock.changePercent).toFixed(2)}%
          <span className="ml-2 text-sm opacity-80">{stock.isPositive ? '+' : ''}{stock.change.toFixed(2)} Today</span>
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Chart Section */}
        <div className="lg:col-span-2 space-y-6">
          {/* Time Range Tabs */}
          <div className="flex border-b border-border">
            {["1D", "5D", "1M", "6M", "YTD", "1Y", "5Y", "MAX"].map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                  timeRange === range 
                    ? 'border-primary text-primary' 
                    : 'border-transparent text-muted-foreground hover:text-foreground'
                }`}
              >
                {range}
              </button>
            ))}
          </div>

          {/* Chart */}
          <div className="h-[400px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={stock.chartData}>
                <defs>
                  <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={stock.isPositive ? "#22c55e" : "#ef4444"} stopOpacity={0.1}/>
                    <stop offset="95%" stopColor={stock.isPositive ? "#22c55e" : "#ef4444"} stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" />
                <XAxis 
                  dataKey="date" 
                  hide={true} 
                />
                <YAxis 
                  domain={['auto', 'auto']} 
                  orientation="right" 
                  tick={{fill: 'hsl(var(--muted-foreground))', fontSize: 12}}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', color: 'hsl(var(--foreground))' }}
                  itemStyle={{ color: 'hsl(var(--foreground))' }}
                  labelStyle={{ color: 'hsl(var(--muted-foreground))' }}
                />
                <Area 
                  type="monotone" 
                  dataKey="price" 
                  stroke={stock.isPositive ? "#22c55e" : "#ef4444"} 
                  strokeWidth={2}
                  fillOpacity={1} 
                  fill="url(#colorPrice)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Sidebar Stats */}
        <div className="space-y-6">
          <Card className="bg-card border-border">
            <CardContent className="p-0">
              <div className="flex gap-2 p-4 border-b border-border">
                <Button variant="secondary" size="sm" className="rounded-full">Stock</Button>
                <Button variant="ghost" size="sm" className="rounded-full">NSE listed security</Button>
              </div>
              <div className="p-4 space-y-4">
                <div className="flex justify-between py-2 border-b border-border last:border-0">
                  <span className="text-sm text-muted-foreground uppercase">Previous Close</span>
                  <span className="font-medium">₹{stock.previousClose.toLocaleString()}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-border last:border-0">
                  <span className="text-sm text-muted-foreground uppercase">Day Range</span>
                  <span className="font-medium">₹{stock.dayLow.toLocaleString()} - ₹{stock.dayHigh.toLocaleString()}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-border last:border-0">
                  <span className="text-sm text-muted-foreground uppercase">Year Range</span>
                  <span className="font-medium">₹{(stock.dayLow * 0.8).toFixed(2)} - ₹{(stock.dayHigh * 1.2).toFixed(2)}</span> {/* Mocked for now */}
                </div>
                <div className="flex justify-between py-2 border-b border-border last:border-0">
                  <span className="text-sm text-muted-foreground uppercase">Market Cap</span>
                  <span className="font-medium">{(stock.marketCap / 10000000).toFixed(2)} Cr</span>
                </div>
                <div className="flex justify-between py-2 border-b border-border last:border-0">
                  <span className="text-sm text-muted-foreground uppercase">P/E Ratio</span>
                  <span className="font-medium">{stock.peRatio?.toFixed(2) || '-'}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-border last:border-0">
                  <span className="text-sm text-muted-foreground uppercase">Dividend Yield</span>
                  <span className="font-medium">{stock.dividendYield ? (stock.dividendYield * 100).toFixed(2) + '%' : '-'}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-border last:border-0">
                  <span className="text-sm text-muted-foreground uppercase">Primary Exchange</span>
                  <span className="font-medium">NSE</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default StockDetail;
