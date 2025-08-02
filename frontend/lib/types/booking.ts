import { Flight } from './flight';

export interface Booking {
    id: number;
    flight_id: number;
    status: string;
    booked_at: string;
    cancelled_at?: string | null;
    flight: Flight;
}
