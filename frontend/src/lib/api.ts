const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL ?? "").replace(/\/+$/, "");

export type VolunteerOpportunity = {
  id?: string;
  title: string;
  organization: string;
  location: string;
  summary: string;
  url: string;
  full_text?: string | null;
};

type SearchResponse = {
  search_query: string;
  opportunities: VolunteerOpportunity[];
};

type ChatMessage = {
  role: "user" | "assistant" | "system";
  content: string;
};

type ChatResponse = {
  answer: string;
};

async function request<T>(
  path: string,
  init: RequestInit & { token?: string | null } = {}
): Promise<T> {
  const { token, ...rest } = init;
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });

  if (res.status === 204) return undefined as T;

  const text = await res.text();
  let data: { detail?: string | { msg: string }[] } | null = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    // Non-JSON response; fall through to the status-based message.
  }

  if (!res.ok) {
    const detail = data?.detail;
    // FastAPI validation errors come back as a list of {msg} objects.
    const message = Array.isArray(detail) ? detail[0]?.msg : detail;
    throw new Error(message ?? `Request failed with status ${res.status}`);
  }

  return data as T;
}

export function searchOpportunities(query: string): Promise<SearchResponse> {
  return request("/api/search", {
    method: "POST",
    body: JSON.stringify({ user_request: query }),
  });
}

export function chatWithRole(
  fullText: string,
  message: string,
  history: ChatMessage[]
): Promise<ChatResponse> {
  return request("/api/chat", {
    method: "POST",
    body: JSON.stringify({
      full_text: fullText,
      user_query: message,
      chat_history: history,
    }),
  });
}

export function saveRole(
  token: string | null,
  opportunity: VolunteerOpportunity
): Promise<{ success: boolean }> {
  return request("/api/saved", {
    method: "POST",
    token,
    body: JSON.stringify(opportunity),
  });
}

export function getSavedRoles(
  token: string | null
): Promise<VolunteerOpportunity[]> {
  return request("/api/saved", { token });
}

export function deleteSavedRole(
  token: string | null,
  id: string
): Promise<void> {
  return request(`/api/saved/${encodeURIComponent(id)}`, {
    method: "DELETE",
    token,
  });
}
