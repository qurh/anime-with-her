import { NextResponse } from "next/server";
import { fetchPipelineRun } from "../../../../../lib/api";

type RouteContext = {
  params: { runId: string } | Promise<{ runId: string }>;
};

async function resolveRunId(context: RouteContext): Promise<string> {
  const params = await context.params;
  return params.runId;
}

export async function GET(_: Request, context: RouteContext) {
  const runId = await resolveRunId(context);
  if (!runId) {
    return NextResponse.json({ success: false, error: "run_id 不能为空。" }, { status: 400 });
  }

  try {
    const data = await fetchPipelineRun(runId);
    return NextResponse.json({ success: true, data }, { status: 200 });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "查询任务详情失败，请稍后重试。",
      },
      { status: 500 },
    );
  }
}
