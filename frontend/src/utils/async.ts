import { setLoading, addError } from '../stores/ui.js';
import type { ApiResponse } from '../services/api.js';

/**
 * Wrapper for async operations that handles loading states and errors
 */
export async function withLoading<T>(
  key: string,
  operation: () => Promise<ApiResponse<T>>
): Promise<T | null> {
  setLoading(key, true);
  
  try {
    const response = await operation();
    
    if (response.error) {
      addError({
        code: response.error.code,
        message: response.error.message,
        details: response.error.details
      });
      return null;
    }
    
    return response.data || null;
  } catch (error) {
    addError({
      code: 'UNEXPECTED_ERROR',
      message: error instanceof Error ? error.message : 'An unexpected error occurred'
    });
    return null;
  } finally {
    setLoading(key, false);
  }
}

/**
 * Check if a specific operation is loading
 */
export function isLoading(loadingState: Record<string, boolean>, key: string): boolean {
  return loadingState[key] || false;
}