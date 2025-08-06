export type Flight = {
    id: number;
    origin: string;
    destination: string;
    departure_time: string; // ISO 8601 string
    arrival_time: string;   // ISO 8601 string
    airline: string;
    status: string;
    price: number;
};

export type PaginatedFlightsResponse = {
    items: Flight[];
    total: number;
    page: number;
    size: number;
    pages: number;
};

export type SearchFilters = {
    origin?: string;
    destination?: string;
    departureDate?: string;
};

export type FlightsResponse = Flight[]