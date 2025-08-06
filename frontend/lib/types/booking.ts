import { Flight } from './flight';

export interface Booking {
    id: number;
    flight_id: number;
    status: string;
    booked_at: string;
    cancelled_at?: string | null;
    flight: Flight;
}

export interface PaginatedBookingsResponse {
    items: Booking[];
    total: number;
    page: number;
    size: number;
    pages: number;
}
