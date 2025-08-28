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

export function isLoading(key: string): boolean {
  let currentState: LoadingState = {};
  loading.subscribe(state => currentState = state)();
  return currentState[key] || false;
}

// Global loading state for critical operations
export const globalLoading = writable<boolean>(false);

export function setGlobalLoading(isLoading: boolean) {
  globalLoading.set(isLoading);
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
  
  errors.update(currentErrors => {
    // Prevent duplicate errors
    const isDuplicate = currentErrors.some(existingError => 
      existingError.code === appError.code && 
      existingError.message === appError.message &&
      (Date.now() - existingError.timestamp) < 1000 // Within 1 second
    );
    
    if (isDuplicate) {
      return currentErrors;
    }
    
    // Limit to 5 errors maximum
    const newErrors = [...currentErrors, appError];
    return newErrors.slice(-5);
  });
  
  // Auto-remove error after 8 seconds (longer for better UX)
  setTimeout(() => {
    removeError(appError.id);
  }, 8000);
}

export function removeError(errorId: string) {
  errors.update(currentErrors => 
    currentErrors.filter(error => error.id !== errorId)
  );
}

export function clearErrors() {
  errors.set([]);
}

// Success notifications
export interface SuccessNotification {
  id: string;
  message: string;
  timestamp: number;
}

export const successNotifications = writable<SuccessNotification[]>([]);

export function addSuccess(message: string) {
  const notification: SuccessNotification = {
    id: Math.random().toString(36).substr(2, 9),
    message,
    timestamp: Date.now()
  };
  
  successNotifications.update(current => [...current, notification]);
  
  // Auto-remove after 4 seconds
  setTimeout(() => {
    removeSuccess(notification.id);
  }, 4000);
}

export function removeSuccess(notificationId: string) {
  successNotifications.update(current => 
    current.filter(notification => notification.id !== notificationId)
  );
}

export function clearSuccessNotifications() {
  successNotifications.set([]);
}