import { Booking, PaginatedBookingsResponse } from '@/lib/types/booking';

const API_URL = '/api';

export async function getUserBookings(
    token: string, 
    status?: string,
    bookedDate?: string,
    departureDate?: string,
    page: number = 1, 
    size: number = 10
): Promise<PaginatedBookingsResponse> {
    const params = new URLSearchParams({
        page: page.toString(),
        size: size.toString(),
    });

    if (status) params.append('status', status);
    if (bookedDate) params.append('booked_date', bookedDate);
    if (departureDate) params.append('departure_date', departureDate);

    const res = await fetch(`${API_URL}/bookings/user?${params.toString()}`, {
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
        },
        credentials: 'include', // Include cookies in the request
    });

    if (!res.ok) {
        throw new Error('Failed to fetch bookings');
    }

    return res.json();
}

export async function cancelBooking(bookingId: number, token: string): Promise<Booking> {
    const res = await fetch(`${API_URL}/bookings/${bookingId}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ status: 'cancelled' }),
        credentials: 'include',
    });

    if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`Failed to cancel booking: ${errorText}`);
    }

    return res.json();
}
