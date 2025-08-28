// Admin API service for backend communication

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

export interface VehicleCreate {
  registration: string;
  make: string;
  color: string;
}

export interface VehicleUpdate {
  registration?: string;
  make?: string;
  color?: string;
}

export interface Booking {
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

export interface DashboardStats {
  total_vehicles: number;
  total_bookings: number;
  active_bookings: number;
  pending_bookings: number;
  offline_vehicles: number;
  available_vehicles: number;
}

export interface VehicleAvailability {
  id: number;
  vehicle_id: number;
  start_date: string;
  end_date: string;
  is_available: boolean;
  reason?: string;
}

class AdminApiService {
  private baseUrl = 'http://localhost:8000/api/admin';

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
            message: errorData.detail || errorData.message || `HTTP ${response.status}: ${response.statusText}`,
            details: errorData.details,
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

  // Dashboard endpoints
  async getDashboardStats(): Promise<ApiResponse<DashboardStats>> {
    return this.request<DashboardStats>('/dashboard/stats');
  }

  // Vehicle management endpoints
  async getAllVehicles(): Promise<ApiResponse<Vehicle[]>> {
    return this.request<Vehicle[]>('/vehicles/');
  }

  async createVehicle(vehicle: VehicleCreate): Promise<ApiResponse<Vehicle>> {
    return this.request<Vehicle>('/vehicles/', {
      method: 'POST',
      body: JSON.stringify(vehicle),
    });
  }

  async updateVehicle(vehicleId: number, vehicle: VehicleUpdate): Promise<ApiResponse<Vehicle>> {
    return this.request<Vehicle>(`/vehicles/${vehicleId}`, {
      method: 'PUT',
      body: JSON.stringify(vehicle),
    });
  }

  async deleteVehicle(vehicleId: number): Promise<ApiResponse<{ message: string }>> {
    return this.request<{ message: string }>(`/vehicles/${vehicleId}`, {
      method: 'DELETE',
    });
  }

  async takeVehicleOffline(
    vehicleId: number,
    startDate: string,
    endDate: string,
    reason: string
  ): Promise<ApiResponse<{ message: string }>> {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
      reason: reason,
    });
    return this.request<{ message: string }>(`/vehicles/${vehicleId}/offline?${params}`, {
      method: 'POST',
    });
  }

  async bringVehicleOnline(vehicleId: number): Promise<ApiResponse<{ message: string }>> {
    return this.request<{ message: string }>(`/vehicles/${vehicleId}/online`, {
      method: 'POST',
    });
  }

  async getVehicleAvailability(vehicleId: number): Promise<ApiResponse<{
    vehicle: Vehicle;
    availability_records: VehicleAvailability[];
  }>> {
    return this.request(`/vehicles/${vehicleId}/availability`);
  }

  // Booking management endpoints
  async getAllBookings(status?: string, vehicleId?: number): Promise<ApiResponse<Booking[]>> {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (vehicleId) params.append('vehicle_id', vehicleId.toString());
    
    const queryString = params.toString();
    const endpoint = queryString ? `/bookings/?${queryString}` : '/bookings/';
    
    return this.request<Booking[]>(endpoint);
  }

  async updateBookingStatus(
    bookingId: number,
    status: string
  ): Promise<ApiResponse<{ message: string; booking: Booking }>> {
    const params = new URLSearchParams({ status });
    return this.request<{ message: string; booking: Booking }>(`/bookings/${bookingId}/status?${params}`, {
      method: 'PUT',
    });
  }

  async deleteBooking(bookingId: number): Promise<ApiResponse<{ message: string }>> {
    return this.request<{ message: string }>(`/bookings/${bookingId}`, {
      method: 'DELETE',
    });
  }
}

export const adminApiService = new AdminApiService();