type BudgetPageProps = {
  params: Promise<{
    jobId: string;
  }>;
};

import BudgetDecisionClientPage from "./budget-decision-client";

export default async function BudgetPage({ params }: BudgetPageProps) {
  const resolvedParams = await params;
  return <BudgetDecisionClientPage jobId={resolvedParams.jobId} />;
}
