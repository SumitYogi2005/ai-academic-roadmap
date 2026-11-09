export default function Skeleton({ className = '', variant = 'rectangular' }) {
  const base = 'animate-pulse bg-gray-200 rounded';

  if (variant === 'circular') {
    return <div className={`${base} rounded-full ${className}`} />;
  }
  if (variant === 'text') {
    return <div className={`${base} h-4 rounded ${className}`} />;
  }
  return <div className={`${base} ${className}`} />;
}

export function SkeletonCard({ className = '' }) {
  return (
    <div className={`bg-white rounded-xl p-5 border border-gray-200 space-y-3 ${className}`}>
      <Skeleton className="h-5 w-2/3" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-4/5" />
      <div className="flex gap-2 pt-2">
        <Skeleton className="h-6 w-16 rounded-full" />
        <Skeleton className="h-6 w-20 rounded-full" />
      </div>
    </div>
  );
}

export function SkeletonList({ count = 5, className = '' }) {
  return (
    <div className={`space-y-3 ${className}`}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="flex items-center gap-3 p-3 bg-white rounded-lg border border-gray-200">
          <Skeleton variant="circular" className="w-9 h-9 flex-shrink-0" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
          </div>
        </div>
      ))}
    </div>
  );
}
