const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL ?? "").replace(/\/+$/, "");

type VolunteerOpportunity = {
  id?: string;
  title: string;
  organization: string;
  location: string;
  summary: string;
  url: string;
  full_text?: string | null;
};

type SearchResponse = {
  message: string;
  opportunities: VolunteerOpportunity[];
};

type ChatMessage = {
  role: "user" | "assistant" | "system";
  content: string;
};

type ChatResponse = {
  answer: string;
};

type SaveResponse = {
  success: boolean;
};

type SavedRolesResponse = VolunteerOpportunity[];

function getApiUrl(path: string): string {
  const base = API_BASE_URL || "";
  const normalizedBase = base ? base.replace(/\/+$/, "") : "";
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${normalizedBase}${normalizedPath}`;
}

async function handleResponse<T>(res: Response): Promise<T> {
  let data: unknown;
  const text = await res.text();

  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    // Non-JSON response
    throw new Error(
      res.ok
        ? "Unexpected response format from server."
        : `Request failed with status ${res.status}`
    );
  }

  if (!res.ok) {
    const message =
      (data as any)?.detail ??
      (data as any)?.message ??
      `Request failed with status ${res.status}`;
    throw new Error(message);
  }

  return data as T;
}

export async function searchOpportunities(
  query: string
): Promise<SearchResponse> {
  const res = await fetch(getApiUrl("/api/search"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      user_request: query,
    }),
  });

  return handleResponse<SearchResponse>(res);
}

export async function chatWithRole(
  opportunityId: string,
  fullText: string,
  message: string,
  history: ChatMessage[]
): Promise<ChatResponse> {
  const res = await fetch(getApiUrl("/api/chat"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      opportunity_id: opportunityId,
      full_text: fullText,
      user_query: message,
      chat_history: history,
    }),
  });

  return handleResponse<ChatResponse>(res);
}

export async function saveRole(
  userId: string,
  opportunity: VolunteerOpportunity
): Promise<SaveResponse> {
  const res = await fetch(getApiUrl("/api/save"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      user_id: userId,
      opportunity,
    }),
  });

  return handleResponse<SaveResponse>(res);
}

export async function getSavedRoles(
  userId: string
): Promise<SavedRolesResponse> {
  const url = getApiUrl(`/api/saved?user_id=${encodeURIComponent(userId)}`);

  const res = await fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  return handleResponse<SavedRolesResponse>(res);
}

