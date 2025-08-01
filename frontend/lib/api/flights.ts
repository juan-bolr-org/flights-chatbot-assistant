import { Flight, FlightsResponse } from '../types/flight';

const API_URL = '/api';

function sanitizeId(id: string | number): string {
    if (!/^\d+$/.test(String(id))) throw new Error('Invalid ID');
    return encodeURIComponent(String(id));
}

export async function getFlights(): Promise<FlightsResponse> {
    const response = await fetch(`${API_URL}/flights/list`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
        cache: 'no-store',
    });

    if (!response.ok) {
        throw new Error('Failed to load flights.');
    }

    return response.json();
}

// Get flight details by ID
export async function getFlightById(id: string): Promise<Flight> {
    const response = await fetch(`${API_URL}/flights/${id}`, {
        cache: 'no-store',
    });

    if (!response.ok) {
        throw new Error('Flight not found.');
    }

    return response.json();
}

// Create a new flight
export async function createFlight(flight: Omit<Flight, 'id'>): Promise<Flight> {
    try {
        const res = await fetch(`${API_URL}/flights`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(flight),
        });

        if (!res.ok) throw new Error('Failed to create flight.');

        const data = await res.json();
        if (!data.data) throw new Error('Unexpected server response.');

        return data.data;
    } catch (error) {
        if (error instanceof Error) {
            throw new Error(`Network error while creating flight: ${error.message}`);
        }
        throw new Error('Unknown error while creating flight.');
    }
}

// Update an existing flight
export async function updateFlight(id: string | number, flight: Partial<Flight>): Promise<Flight> {
    const safeId = sanitizeId(id);

    try {
        const res = await fetch(`${API_URL}/flights/${safeId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(flight),
        });

        if (!res.ok) throw new Error('Failed to update flight.');

        const data = await res.json();
        if (!data.data) throw new Error('Unexpected server response.');

        return data.data;
    } catch (error) {
        if (error instanceof Error) {
            throw new Error(`Network error while updating flight: ${error.message}`);
        }
        throw new Error('Unknown error while updating flight.');
    }
}

// Delete a flight
export async function deleteFlight(id: string | number): Promise<void> {
    const safeId = sanitizeId(id);

    try {
        const res = await fetch(`${API_URL}/flights/${safeId}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
        });

        if (!res.ok) throw new Error('Failed to delete flight.');
    } catch (error) {
        if (error instanceof Error) {
            throw new Error(`Network error while deleting flight: ${error.message}`);
        }
        throw new Error('Unknown error while deleting flight.');
    }
}

export async function createBooking(): Promise<void> {
    // Placeholder for booking creation logic
    throw new Error('Booking creation not implemented yet.');
}