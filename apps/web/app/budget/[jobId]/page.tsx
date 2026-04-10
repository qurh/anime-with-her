type BudgetPageProps = {
  params: {
    jobId: string;
  };
};

export default function BudgetPage({ params }: BudgetPageProps) {
  return (
    <main>
      <h1>Budget Decision</h1>
      <p>Job: {params.jobId}</p>
    </main>
  );
}
