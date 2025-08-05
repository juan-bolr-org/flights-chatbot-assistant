import { Booking } from '@/lib/types/booking';

const API_URL = '/api';

export async function getUserBookings(token: string): Promise<Booking[]> {
    const res = await fetch(`${API_URL}/bookings/user`, {
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
        },
    });

    if (!res.ok) {
        throw new Error('Failed to fetch bookings');
    }

    return res.json();
}
