import { writable } from 'svelte/store';

// Loading state management
export interface LoadingState {
  [key: string]: boolean;
}

export const loading = writable<LoadingState>({});

export function setLoading(key: string, isLoading: boolean) {
  loading.update(state => ({
    ...state,
    [key]: isLoading
  }));
}

// Error handling
export interface AppError {
  id: string;
  code: string;
  message: string;
  details?: any;
  timestamp: number;
}

export const errors = writable<AppError[]>([]);

export function addError(error: Omit<AppError, 'id' | 'timestamp'>) {
  const appError: AppError = {
    ...error,
    id: Math.random().toString(36).substr(2, 9),
    timestamp: Date.now()
  };
  
  errors.update(currentErrors => [...currentErrors, appError]);
  
  // Auto-remove error after 5 seconds
  setTimeout(() => {
    removeError(appError.id);
  }, 5000);
}

export function removeError(errorId: string) {
  errors.update(currentErrors => 
    currentErrors.filter(error => error.id !== errorId)
  );
}

export function clearErrors() {
  errors.set([]);
}