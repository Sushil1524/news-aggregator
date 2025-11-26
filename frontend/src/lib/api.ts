// API configuration and utilities
export const API_BASE_URL = "http://localhost:8000";

// Auth types
export type UserCreate = {
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

export type UserLogin = {
  email: string;
  username: string;
  password: string;
};

export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

// Article types
export type Article = {
  _id: string;
  title: string;
  url: string;
  content: string;
  summary?: string;
  category?: string;
  tags: string[];
  sentiment?: string;
  image_url?: string;
  author_email: string;
  upvotes: number;
  downvotes: number;
  comments_count: number;
  views: number;
  created_at: string;
  updated_at: string;
};

// Comment types
export type Comment = {
  _id: string;
  article_id: string;
  content: string;
  author_email: string;
  parent_id?: string;
  upvotes: number;
  downvotes: number;
  created_at: string;
  updated_at: string;
};

export type CommentCreate = {
  article_id: string;
  content: string;
  parent_id?: string;
};

// API helper with auth
async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const token = localStorage.getItem("access_token");
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.href = "/auth?tab=login";
    throw new Error("Unauthorized");
  }

  return response;
}

// Auth API
export const authAPI = {
  async register(data: UserCreate): Promise<TokenResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error("Registration failed");
    return response.json();
  },

  async login(data: UserLogin): Promise<TokenResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error("Login failed");
    return response.json();
  },

  async getProfile(): Promise<UserCreate> {
    const response = await fetchWithAuth("/auth/me");
    if (!response.ok) throw new Error("Failed to fetch profile");
    return response.json();
  },

  async updateProfile(data: Partial<UserCreate>): Promise<UserCreate> {
    const response = await fetchWithAuth("/auth/me", {
      method: "PATCH",
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error("Failed to update profile");
    return response.json();
  },
};

// Articles API
export const articlesAPI = {
  async getArticles(params?: {
    cursor?: string;
    limit?: number;
    category?: string;
    tag?: string;
    search?: string;
    sort_by?: "hot" | "new" | "top";
    date_filter?: string;
  }): Promise<{ articles: Article[]; next_cursor?: string }> {
    const searchParams = new URLSearchParams();
    if (params?.cursor) searchParams.set("cursor", params.cursor);
    if (params?.limit) searchParams.set("limit", params.limit.toString());
    if (params?.category) searchParams.set("category", params.category);
    if (params?.tag) searchParams.set("tag", params.tag);
    if (params?.search) searchParams.set("search", params.search);
    if (params?.sort_by) searchParams.set("sort_by", params.sort_by);
    if (params?.date_filter) searchParams.set("date_filter", params.date_filter);

    const response = await fetchWithAuth(`/article/?${searchParams}`);
    if (!response.ok) throw new Error("Failed to fetch articles");
    return response.json();
  },

  async getArticle(id: string): Promise<Article> {
    const response = await fetchWithAuth(`/article/${id}`);
    if (!response.ok) throw new Error("Failed to fetch article");
    return response.json();
  },

  async upvote(id: string): Promise<void> {
    const response = await fetchWithAuth(`/article/${id}/upvote`, {
      method: "POST",
    });
    if (!response.ok) throw new Error("Failed to upvote");
  },

  async downvote(id: string): Promise<void> {
    const response = await fetchWithAuth(`/article/${id}/downvote`, {
      method: "POST",
    });
    if (!response.ok) throw new Error("Failed to downvote");
  },
};

// Comments API
export const commentsAPI = {
  async getComments(articleId: string): Promise<Comment[]> {
    const response = await fetchWithAuth(`/comments/${articleId}`);
    if (!response.ok) throw new Error("Failed to fetch comments");
    return response.json();
  },

  async createComment(data: CommentCreate): Promise<Comment> {
    const response = await fetchWithAuth("/comments/", {
      method: "POST",
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error("Failed to create comment");
    return response.json();
  },

  async deleteComment(id: string): Promise<void> {
    const response = await fetchWithAuth(`/comments/${id}`, {
      method: "DELETE",
    });
    if (!response.ok) throw new Error("Failed to delete comment");
  },

  async upvote(id: string): Promise<void> {
    const response = await fetchWithAuth(`/comments/${id}/upvote`, {
      method: "POST",
    });
    if (!response.ok) throw new Error("Failed to upvote");
  },

  async downvote(id: string): Promise<void> {
    const response = await fetchWithAuth(`/comments/${id}/downvote`, {
      method: "POST",
    });
    if (!response.ok) throw new Error("Failed to downvote");
  },
};

// Bookmarks API
export const bookmarksAPI = {
  async getBookmarks(): Promise<Article[]> {
    const response = await fetchWithAuth("/bookmarks/");
    if (!response.ok) throw new Error("Failed to fetch bookmarks");
    return response.json();
  },

  async addBookmark(articleId: string): Promise<void> {
    const response = await fetchWithAuth(`/bookmarks/${articleId}`, {
      method: "POST",
    });
    if (!response.ok) throw new Error("Failed to add bookmark");
  },

  async removeBookmark(articleId: string): Promise<void> {
    const response = await fetchWithAuth(`/bookmarks/${articleId}`, {
      method: "DELETE",
    });
    if (!response.ok) throw new Error("Failed to remove bookmark");
  },
};

// Vocab types
export type VocabCard = {
  word: string;
  meaning?: string;
  example?: string;
  added_at: string;
  level: number;
  proficiency: string;
  next_review_date: string;
  last_practiced?: string;
  is_learned: boolean;
};

export type VocabProgress = {
  summary: {
    total_words: number;
    total_learned: number;
    due_today: number;
    practiced_today: number;
    daily_target: number;
    completion_rate: number;
  };
  gamification: {
    points: number;
    streak: number;
  };
};

// Vocab API
export const vocabAPI = {
  async getTodayCards(): Promise<{ today_cards: VocabCard[]; daily_target: number }> {
    const response = await fetchWithAuth("/vocab/today");
    if (!response.ok) throw new Error("Failed to fetch today's vocab");
    return response.json();
  },

  async markPracticeDone(words: string[]): Promise<{ message: string }> {
    const response = await fetchWithAuth("/vocab/practice/done", {
      method: "POST",
      body: JSON.stringify({ words }),
    });
    if (!response.ok) throw new Error("Failed to mark practice done");
    return response.json();
  },

  async getProgress(): Promise<VocabProgress> {
    const response = await fetchWithAuth("/vocab/progress");
    if (!response.ok) throw new Error("Failed to fetch vocab progress");
    return response.json();
  },
};

// Admin API
export const adminAPI = {
  async refreshFeed(): Promise<void> {
    const response = await fetchWithAuth("/admin/refresh", {
      method: "POST",
    });
    if (!response.ok) throw new Error("Failed to refresh feed");
  },
};

// Analytics API
export const analyticsAPI = {
  async getTrending(limit: number = 10): Promise<Article[]> {
    const response = await fetchWithAuth(`/analytics/trending?limit=${limit}`);
    if (!response.ok) throw new Error("Failed to fetch trending articles");
    return response.json();
  },

  async getTopCategories(limit: number = 5): Promise<Array<{ category: string; count: number }>> {
    const response = await fetchWithAuth(`/analytics/top-categories?limit=${limit}`);
    if (!response.ok) throw new Error("Failed to fetch top categories");
    return response.json();
  },

  async getDailyCounts(days: number = 7): Promise<Array<{ _id: string; count: number }>> {
    const response = await fetchWithAuth(`/analytics/daily-counts?days=${days}`);
    if (!response.ok) throw new Error("Failed to fetch daily counts");
    return response.json();
  },

  async getUserDashboard(): Promise<{
    username: string;
    points: number;
    streak: number;
    articles_read_total: number;
    articles_read_last_week: number;
    vocab_words_added: number;
    reading_history: Array<{
      timestamp: string;
      article_id: string;
      reading_time_seconds?: number | null;
    }>;
  }> {
    const response = await fetchWithAuth("/analytics/dashboard");
    if (!response.ok) throw new Error("Failed to fetch user dashboard");
    return response.json();
  },
};
