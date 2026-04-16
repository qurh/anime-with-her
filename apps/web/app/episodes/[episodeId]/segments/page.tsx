type PageProps = {
  params: Promise<{ episodeId: string }>;
};

export default async function SegmentRefinementPage({ params }: PageProps) {
  const { episodeId } = await params;
  return (
    <main className="container">
      <p>Episode: {episodeId}</p>
      <h1>关键片段精修</h1>
    </main>
  );
}
