'use client';

import { useState, useEffect } from 'react';
import { getFlights } from '@/lib/api/flights';
import { Flight } from '@/lib/types/flight';
import { FlightCard } from '@/components/flights/FlightCard';

const FLIGHTS_PER_PAGE = 8;

export default function FlightsPage() {
    const [flights, setFlights] = useState<Flight[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const [currentPage, setCurrentPage] = useState(1);

    useEffect(() => {
        const fetchFlights = async () => {
            const jwt = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
            if (!jwt) {
                setError("No token found.");
                setIsLoading(false);
                return;
            }

            try {
                const response = await getFlights(jwt);
                setFlights(response);
            } catch (err) {
                setError("Can't load Flights, please try again later.");
            } finally {
                setIsLoading(false);
            }
        };

        fetchFlights();
    }, []);

    const totalPages = Math.ceil(flights.length / FLIGHTS_PER_PAGE);
    const paginatedFlights = flights.slice(
        (currentPage - 1) * FLIGHTS_PER_PAGE,
        currentPage * FLIGHTS_PER_PAGE
    );

    const goToNextPage = () => {
        if (currentPage < totalPages) setCurrentPage((prev) => prev + 1);
    };

    const goToPreviousPage = () => {
        if (currentPage > 1) setCurrentPage((prev) => prev - 1);
    };

    if (isLoading) {
        return (
            <div className="p-4 text-center">
                <p>Loading...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-4 text-center">
                <p className="text-red-600">{error}</p>
                <button
                    onClick={() => window.location.reload()}
                    className="mt-4 btn btn-primary"
                >
                    Try again
                </button>
            </div>
        );
    }

    return (
        <div className="container mx-auto pb-4 px-4">
            <section>
                <h2 className="text-2xl font-bold text-white-900 mb-6 pt-6">All Flights</h2>
                <div className="flex flex-wrap gap-6 justify-start">
                    {paginatedFlights.length > 0 ? (
                        paginatedFlights.map((flight) => (
                            <FlightCard flight={flight} key={flight.id} />
                        ))
                    ) : (
                        <p>There are no flights available.</p>
                    )}
                </div>

                {/* Pagination Controls */}
                {totalPages > 1 && (
                    <div className="flex justify-center items-center gap-4 mt-8">
                        <button
                            onClick={goToPreviousPage}
                            disabled={currentPage === 1}
                            className="btn btn-outline"
                        >
                            Previous
                        </button>
                        <span className="text-gray-700">
                            Page {currentPage} of {totalPages}
                        </span>
                        <button
                            onClick={goToNextPage}
                            disabled={currentPage === totalPages}
                            className="btn btn-outline"
                        >
                            Next
                        </button>
                    </div>
                )}
            </section>
        </div>
    );
}
