// API service layer for backend communication

export interface ApiResponse<T> {
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}

export interface Vehicle {
  id: number;
  registration: string;
  make: string;
  color: string;
  created_at: string;
  updated_at: string;
}

export interface AvailableVehicle extends Vehicle {
  // Additional fields for available vehicles if needed
}

export interface BookingRequest {
  vehicle_id: number;
  start_datetime: string;
  end_datetime: string;
  reason: string;
  estimated_mileage: number;
}

export interface BookingConfirmation {
  id: number;
  vehicle_id: number;
  start_datetime: string;
  end_datetime: string;
  return_datetime: string;
  reason: string;
  estimated_mileage: number;
  status: string;
  created_at: string;
  vehicle: Vehicle;
}

class ApiService {
  private baseUrl = 'http://localhost:8000/api';

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        return {
          error: {
            code: `HTTP_${response.status}`,
            message: errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`,
            details: errorData.error?.details,
          },
        };
      }

      const data = await response.json();
      return { data };
    } catch (error) {
      return {
        error: {
          code: 'NETWORK_ERROR',
          message: error instanceof Error ? error.message : 'Network error occurred',
        },
      };
    }
  }

  // Vehicle endpoints
  async getVehicles(): Promise<ApiResponse<Vehicle[]>> {
    return this.request<Vehicle[]>('/vehicles/');
  }

  async getAvailableVehicles(startDate: string, endDate: string): Promise<ApiResponse<AvailableVehicle[]>> {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
    });
    return this.request<AvailableVehicle[]>(`/vehicles/available?${params}`);
  }

  // Booking endpoints
  async createBooking(booking: BookingRequest): Promise<ApiResponse<BookingConfirmation>> {
    return this.request<BookingConfirmation>('/bookings/', {
      method: 'POST',
      body: JSON.stringify(booking),
    });
  }

  async getBooking(bookingId: number): Promise<ApiResponse<BookingConfirmation>> {
    return this.request<BookingConfirmation>(`/bookings/${bookingId}`);
  }
}

export const apiService = new ApiService();