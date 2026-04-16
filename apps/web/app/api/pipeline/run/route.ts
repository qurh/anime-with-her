import { NextResponse } from "next/server";
import { triggerPipelineRun } from "../../../../lib/api";

type PipelineRunRequest = {
  episode_id?: string;
  source_video?: string;
  root?: string;
  start_stage?: string;
};

export async function POST(request: Request) {
  const payload = (await request.json()) as PipelineRunRequest;
  const episodeId = (payload.episode_id || "").trim();
  const sourceVideo = (payload.source_video || "").trim();
  const root = (payload.root || "").trim();
  const startStage = (payload.start_stage || "").trim();

  if (!episodeId || !sourceVideo) {
    return NextResponse.json(
      { success: false, error: "episode_id 和 source_video 为必填项。" },
      { status: 400 },
    );
  }

  try {
    const data = await triggerPipelineRun({
      episode_id: episodeId,
      source_video: sourceVideo,
      root: root || undefined,
      start_stage: startStage || undefined,
    });
    return NextResponse.json({ success: true, data }, { status: 202 });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "后端执行失败。",
      },
      { status: 500 },
    );
  }
}
