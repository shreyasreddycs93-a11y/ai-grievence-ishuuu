import { AlertCircle } from 'lucide-react';

export default function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="flex items-start gap-3 rounded-xl bg-error-50 px-4 py-3 ring-1 ring-inset ring-error-200 animate-fade-in">
      <AlertCircle className="mt-0.5 shrink-0 text-error-600" size={20} />
      <p className="text-sm font-medium text-error-800">{message}</p>
    </div>
  );
}
