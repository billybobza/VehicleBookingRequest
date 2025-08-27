import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiService } from '../services/api.js';

// Mock fetch globally
global.fetch = vi.fn();

describe('API Service', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('should handle successful API responses', async () => {
    const mockVehicles = [
      { id: 1, registration: 'ABC123', make: 'Toyota', color: 'Red' }
    ];

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockVehicles,
    });

    const result = await apiService.getVehicles();
    
    expect(result.data).toEqual(mockVehicles);
    expect(result.error).toBeUndefined();
  });

  it('should handle API errors', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 404,
      statusText: 'Not Found',
      json: async () => ({
        error: {
          code: 'NOT_FOUND',
          message: 'Resource not found'
        }
      }),
    });

    const result = await apiService.getVehicles();
    
    expect(result.data).toBeUndefined();
    expect(result.error).toEqual({
      code: 'HTTP_404',
      message: 'Resource not found',
      details: undefined
    });
  });

  it('should handle network errors', async () => {
    (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

    const result = await apiService.getVehicles();
    
    expect(result.data).toBeUndefined();
    expect(result.error).toEqual({
      code: 'NETWORK_ERROR',
      message: 'Network error'
    });
  });
});