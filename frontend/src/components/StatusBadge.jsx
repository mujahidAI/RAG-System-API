/**
 * StatusBadge - Displays backend connection status as a colored badge.
 * Props: status ("online" | "offline" | "checking")
 */

export function StatusBadge({ status }) {
  const getStatusConfig = () => {
    switch (status) {
      case 'online':
        return {
          dotColor: 'bg-green-500',
          text: 'Backend Online',
          textColor: 'text-green-600',
        };
      case 'offline':
        return {
          dotColor: 'bg-red-500',
          text: 'Backend Offline',
          textColor: 'text-red-600',
        };
      case 'checking':
      default:
        return {
          dotColor: 'bg-yellow-500',
          text: 'Checking...',
          textColor: 'text-yellow-600',
        };
    }
  };

  const config = getStatusConfig();

  return (
    <div className={`flex items-center gap-2 ${config.textColor}`}>
      <span className={`relative flex h-3 w-3`}>
        <span className={`absolute inline-flex h-full w-full rounded-full ${config.dotColor} opacity-75`}></span>
        <span className={`relative inline-flex h-3 w-3 rounded-full ${config.dotColor}`}></span>
      </span>
      <span className="text-sm font-medium">{config.text}</span>
    </div>
  );
}
