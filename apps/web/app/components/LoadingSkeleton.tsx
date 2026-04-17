type LoadingSkeletonProps = {
  lines?: number;
};

export default function LoadingSkeleton({ lines = 6 }: LoadingSkeletonProps) {
  return (
    <section className="panel" aria-label="页面加载中">
      <div className="skeleton skeleton-title" />
      <div className="skeleton-group">
        {Array.from({ length: lines }).map((_, index) => (
          <div className="skeleton skeleton-line" key={index} />
        ))}
      </div>
    </section>
  );
}
