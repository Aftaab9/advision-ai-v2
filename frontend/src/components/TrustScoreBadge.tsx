import { Shield, AlertTriangle, CheckCircle } from 'lucide-react';

interface TrustScoreBadgeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
}

export default function TrustScoreBadge({ score, size = 'md' }: TrustScoreBadgeProps) {
  const getBadgeLevel = (score: number) => {
    if (score >= 90) return { level: 'high', color: 'green', label: 'Trusted', icon: CheckCircle };
    if (score >= 70) return { level: 'medium', color: 'blue', label: 'Verified', icon: Shield };
    if (score >= 50) return { level: 'low', color: 'yellow', label: 'Caution', icon: AlertTriangle };
    return { level: 'risk', color: 'red', label: 'Risk', icon: AlertTriangle };
  };

  const badge = getBadgeLevel(score);
  const Icon = badge.icon;

  const sizeClasses = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1.5',
    lg: 'text-base px-4 py-2',
  };

  const colorClasses = {
    green: 'bg-green-100 text-green-800 border-green-300',
    blue: 'bg-blue-100 text-blue-800 border-blue-300',
    yellow: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    red: 'bg-red-100 text-red-800 border-red-300',
  };

  return (
    <div
      className={`inline-flex items-center space-x-1 rounded-full border font-medium ${sizeClasses[size]} ${colorClasses[badge.color]}`}
    >
      <Icon className="h-4 w-4" />
      <span>{badge.label}</span>
      <span className="font-bold">{score}</span>
    </div>
  );
}
