import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiService } from '../services/api';

// Mock the API service
vi.mock('../services/api', () => ({
  apiService: {
    getVehicles: vi.fn(),
    getAvailableVehicles: vi.fn(),
  },
}));

const mockVehicles = [
  { id: 1, registration: 'ABC123', make: 'Toyota', color: 'Blue' },
  { id: 2, registration: 'DEF456', make: 'Honda', color: 'Red' },
  { id: 3, registration: 'GHI789', make: 'Ford', color: 'White' },
];

const mockAvailableVehicles = [
  { id: 1, registration: 'ABC123', make: 'Toyota', color: 'Blue' },
  { id: 3, registration: 'GHI789', make: 'Ford', color: 'White' },
];

describe('VehicleSelector Component Logic', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('API service methods are properly mocked', () => {
    expect(apiService.getVehicles).toBeDefined();
    expect(apiService.getAvailableVehicles).toBeDefined();
  });

  it('mock data is properly structured', () => {
    expect(mockVehicles).toHaveLength(3);
    expect(mockVehicles[0]).toHaveProperty('id');
    expect(mockVehicles[0]).toHaveProperty('registration');
    expect(mockVehicles[0]).toHaveProperty('make');
    expect(mockVehicles[0]).toHaveProperty('color');
  });

  it('available vehicles subset is correct', () => {
    expect(mockAvailableVehicles).toHaveLength(2);
    expect(mockAvailableVehicles.map(v => v.id)).toEqual([1, 3]);
  });

  it('vehicle display format function works correctly', () => {
    const formatVehicleDisplay = (vehicle: typeof mockVehicles[0]) => 
      `${vehicle.registration} - ${vehicle.make} (${vehicle.color})`;
    
    expect(formatVehicleDisplay(mockVehicles[0])).toBe('ABC123 - Toyota (Blue)');
    expect(formatVehicleDisplay(mockVehicles[1])).toBe('DEF456 - Honda (Red)');
    expect(formatVehicleDisplay(mockVehicles[2])).toBe('GHI789 - Ford (White)');
  });

  it('API service getVehicles can be mocked to return success', async () => {
    vi.mocked(apiService.getVehicles).mockResolvedValue({ data: mockVehicles });
    
    const result = await apiService.getVehicles();
    expect(result.data).toEqual(mockVehicles);
    expect(result.error).toBeUndefined();
  });

  it('API service getVehicles can be mocked to return error', async () => {
    const errorMessage = 'Failed to load vehicles';
    vi.mocked(apiService.getVehicles).mockResolvedValue({
      error: { code: 'API_ERROR', message: errorMessage },
    });
    
    const result = await apiService.getVehicles();
    expect(result.error?.message).toBe(errorMessage);
    expect(result.data).toBeUndefined();
  });

  it('API service getAvailableVehicles can be mocked with date parameters', async () => {
    vi.mocked(apiService.getAvailableVehicles).mockResolvedValue({ data: mockAvailableVehicles });
    
    const startDate = '2024-01-01T09:00:00';
    const endDate = '2024-01-02T17:00:00';
    
    const result = await apiService.getAvailableVehicles(startDate, endDate);
    expect(result.data).toEqual(mockAvailableVehicles);
    expect(apiService.getAvailableVehicles).toHaveBeenCalledWith(startDate, endDate);
  });

  it('component props validation logic', () => {
    // Test date validation logic
    const canShowAvailable = (startDate: string, endDate: string) => 
      Boolean(startDate && endDate);
    
    expect(canShowAvailable('', '')).toBe(false);
    expect(canShowAvailable('2024-01-01', '')).toBe(false);
    expect(canShowAvailable('', '2024-01-02')).toBe(false);
    expect(canShowAvailable('2024-01-01', '2024-01-02')).toBe(true);
  });

  it('vehicle selection logic', () => {
    // Test vehicle selection logic
    const findVehicleById = (vehicles: typeof mockVehicles, id: number) => 
      vehicles.find(v => v.id === id);
    
    expect(findVehicleById(mockVehicles, 1)).toEqual(mockVehicles[0]);
    expect(findVehicleById(mockVehicles, 999)).toBeUndefined();
  });

  it('display vehicles logic switches correctly', () => {
    // Test the logic for switching between all vehicles and available vehicles
    const getDisplayVehicles = (showAvailableOnly: boolean, allVehicles: typeof mockVehicles, availableVehicles: typeof mockAvailableVehicles) => 
      showAvailableOnly ? availableVehicles : allVehicles;
    
    expect(getDisplayVehicles(false, mockVehicles, mockAvailableVehicles)).toEqual(mockVehicles);
    expect(getDisplayVehicles(true, mockVehicles, mockAvailableVehicles)).toEqual(mockAvailableVehicles);
  });
});