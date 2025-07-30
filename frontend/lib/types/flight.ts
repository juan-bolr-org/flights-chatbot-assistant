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

export type FlightsResponse = Flight[]