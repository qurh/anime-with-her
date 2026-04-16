import { NextResponse } from "next/server";

type PipelineRunRequest = {
  episode_id?: string;
  source_video?: string;
  root?: string;
};

const BACKEND_BASE_URL = process.env.BACKEND_BASE_URL || "http://127.0.0.1:8000";

function parseJsonSafely(raw: string): Record<string, unknown> {
  try {
    return JSON.parse(raw) as Record<string, unknown>;
  } catch {
    return {};
  }
}

export async function POST(request: Request) {
  const payload = (await request.json()) as PipelineRunRequest;
  const episodeId = (payload.episode_id || "").trim();
  const sourceVideo = (payload.source_video || "").trim();
  const root = (payload.root || "").trim();

  if (!episodeId || !sourceVideo) {
    return NextResponse.json(
      { success: false, error: "episode_id 和 source_video 为必填项。" },
      { status: 400 },
    );
  }

  const backendResponse = await fetch(
    `${BACKEND_BASE_URL}/api/v1/episodes/${encodeURIComponent(episodeId)}/pipeline/run`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        source_video: sourceVideo,
        root: root || undefined,
      }),
      cache: "no-store",
    },
  );

  const rawText = await backendResponse.text();
  const backendPayload = parseJsonSafely(rawText);
  if (!backendResponse.ok) {
    return NextResponse.json(
      {
        success: false,
        error: (backendPayload.error as string) || "后端执行失败。",
      },
      { status: backendResponse.status },
    );
  }

  return NextResponse.json(backendPayload, { status: backendResponse.status });
}
