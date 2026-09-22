import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(isoString: string): string {
  try {
    const date = new Date(isoString);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  } catch {
    return 'Recently';
  }
}

export function formatConfidenceLabel(level?: string): { label: string; tone: 'high' | 'medium' | 'low' } {
  if (level === 'high') {
    return { label: 'High', tone: 'high' };
  }
  if (level === 'medium') {
    return { label: 'Medium', tone: 'medium' };
  }
  return { label: 'Low', tone: 'low' };
}
