import { ReactNode } from 'react';
import { AlertCircle, CheckCircle, XCircle, X } from 'lucide-react';

interface AlertProps {
  children: ReactNode;
  variant?: 'info' | 'success' | 'error' | 'warning';
  onClose?: () => void;
}

export function Alert({ children, variant = 'info', onClose }: AlertProps) {
  const variants = {
    info: {
      bg: 'bg-blue-50 border-blue-200',
      text: 'text-blue-800',
      icon: <AlertCircle className="w-5 h-5 text-blue-600" />,
    },
    success: {
      bg: 'bg-green-50 border-green-200',
      text: 'text-green-800',
      icon: <CheckCircle className="w-5 h-5 text-green-600" />,
    },
    error: {
      bg: 'bg-red-50 border-red-200',
      text: 'text-red-800',
      icon: <XCircle className="w-5 h-5 text-red-600" />,
    },
    warning: {
      bg: 'bg-yellow-50 border-yellow-200',
      text: 'text-yellow-800',
      icon: <AlertCircle className="w-5 h-5 text-yellow-600" />,
    },
  };

  const style = variants[variant];

  return (
    <div className={`p-4 border rounded-lg flex items-start gap-3 ${style.bg} ${style.text}`}>
      {style.icon}
      <div className="flex-1">{children}</div>
      {onClose && (
        <button onClick={onClose} className="hover:opacity-70">
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}
