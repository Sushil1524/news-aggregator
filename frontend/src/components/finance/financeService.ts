import axios from 'axios';

const API_URL = 'https://verbose-goggles-r47gvjx44j952pvwj-8000.app.github.dev/finance'; // Adjust if needed

export interface MarketIndex {
    symbol: string;
    name: string;
    price: number;
    change: number;
    changePercent: number;
    isPositive: boolean;
}

export interface StockDetail {
    symbol: string;
    name: string;
    price: number;
    currency: string;
    change: number;
    changePercent: number;
    isPositive: boolean;
    previousClose: number;
    open: number;
    dayHigh: number;
    dayLow: number;
    marketCap: number;
    peRatio: number;
    dividendYield: number;
    chartData: { date: string; price: number }[];
}

export interface StockSearchResult {
    symbol: string;
    name: string;
}

export const financeService = {
    getIndices: async (): Promise<MarketIndex[]> => {
        const response = await axios.get(`${API_URL}/indices`);
        return response.data;
    },

    getStockDetails: async (ticker: string): Promise<StockDetail> => {
        const response = await axios.get(`${API_URL}/stock/${ticker}`);
        return response.data;
    },

    searchStocks: async (query: string): Promise<StockSearchResult[]> => {
        const response = await axios.get(`${API_URL}/search`, { params: { q: query } });
        return response.data;
    }
};
