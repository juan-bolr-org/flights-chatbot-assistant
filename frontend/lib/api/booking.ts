import { Booking } from '@/lib/types/booking';

const API_URL = '/api';

export async function getUserBookings(userId: string, token: string): Promise<Booking[]> {
    const res = await fetch(`${API_URL}/bookings/user/${userId}`, {
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
