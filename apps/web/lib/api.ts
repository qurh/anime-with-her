export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

export type JobState =
  | "created"
  | "running"
  | "partial_done"
  | "done"
  | "failed"
  | "awaiting_budget_decision"
  | "rerendering";

export type JobData = {
  job_id: string;
  state: JobState;
  input_video: string | null;
};

export type BudgetDecisionData = {
  job_id: string;
  options: string[];
  estimated_extra_cost_cny: number;
  timeout_minutes: number;
  default_action: string;
};

export type VideoUploadData = {
  stored_path: string;
  original_filename: string;
  size_bytes: number;
  content_type: string;
};

type ApiEnvelope<T> = {
  success: boolean;
  data: T;
};

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  const payload = (await response.json()) as ApiEnvelope<T>;
  if (!payload.success) {
    throw new Error("API returned unsuccessful response.");
  }
  return payload.data;
}

export async function createJob(inputVideo: string): Promise<JobData> {
  return requestJson<JobData>("/jobs", {
    method: "POST",
    body: JSON.stringify({ input_video: inputVideo || null }),
  });
}

export async function getJob(jobId: string): Promise<JobData> {
  return requestJson<JobData>(`/jobs/${jobId}`);
}

export async function getBudgetDecision(jobId: string): Promise<BudgetDecisionData> {
  return requestJson<BudgetDecisionData>(`/jobs/${jobId}/budget-decision`);
}

export async function uploadVideo(file: File): Promise<VideoUploadData> {
  const response = await fetch(`${API_BASE_URL}/uploads/video`, {
    method: "POST",
    headers: {
      "Content-Type": file.type || "application/octet-stream",
      "X-Filename": encodeURIComponent(file.name),
    },
    body: file,
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Video upload failed: ${response.status}`);
  }

  const payload = (await response.json()) as ApiEnvelope<VideoUploadData>;
  if (!payload.success) {
    throw new Error("Video upload did not complete successfully.");
  }
  return payload.data;
}
