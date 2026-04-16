type PageProps = {
  params: Promise<{ episodeId: string }>;
};

export default async function CharacterReviewPage({ params }: PageProps) {
  const { episodeId } = await params;
  return (
    <main className="container">
      <p>Episode: {episodeId}</p>
      <h1>角色分析确认</h1>
    </main>
  );
}
