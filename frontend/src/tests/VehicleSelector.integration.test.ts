import { describe, it, expect } from 'vitest';

describe('VehicleSelector Integration', () => {
  it('can import VehicleSelector component', async () => {
    const VehicleSelector = await import('../components/VehicleSelector.svelte');
    expect(VehicleSelector.default).toBeDefined();
  });

  it('can import API service', async () => {
    const { apiService } = await import('../services/api');
    expect(apiService).toBeDefined();
    expect(apiService.getVehicles).toBeDefined();
    expect(apiService.getAvailableVehicles).toBeDefined();
  });

  it('can import child components', async () => {
    const LoadingSpinner = await import('../components/LoadingSpinner.svelte');
    const ErrorDisplay = await import('../components/ErrorDisplay.svelte');
    
    expect(LoadingSpinner.default).toBeDefined();
    expect(ErrorDisplay.default).toBeDefined();
  });
});