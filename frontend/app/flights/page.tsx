'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { getFlights } from '@/lib/api/flights';
import { Flight } from '@/lib/types/flight';
import { FlightCard } from '@/components/flights/FlightCard';

import { Button } from '@radix-ui/themes';
import { Text, Flex, Container, Section, Box } from '@radix-ui/themes';

const FLIGHTS_PER_PAGE = 6;

export default function FlightsPage() {
    const [flights, setFlights] = useState<Flight[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const hasFetched = useRef(false);
    const router = useRouter();

    useEffect(() => {
        if (hasFetched.current) return;
        hasFetched.current = true;

        const fetchFlights = async () => {
            try {
                const response = await getFlights();
                setFlights(response);
            } catch (err) {
                setError("Can't load Flights, please try again later.");
            } finally {
                setIsLoading(false);
            }
        };

        fetchFlights();
    }, [router]);

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
                <Text>Loading...</Text>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-4 text-center">
                <Text>{error}</Text>
                <div className="mt-4">
                    <Button onClick={() => window.location.reload()} variant="solid">
                        Try again
                    </Button>
                </div>
            </div>
        );
    }

    return (
        <Container align={'center'} size="3" py="2">
            <Section>

                <Box pb="6">
                    <Text size="6" weight="bold" py="3">
                        All Flights
                    </Text>
                </Box>

                <Flex wrap={'wrap'} justify="center" align={'start'} gap="4">
                    {paginatedFlights.length > 0 ? (
                        paginatedFlights.map((flight) => (
                            <FlightCard flight={flight} key={flight.id} />
                        ))
                    ) : (
                        <Text>No flights available.</Text>
                    )}
                </Flex>
            </Section>
            <Section py="6">
                {totalPages > 1 && (
                    <Flex justify={'center'} align="center" gap="4">
                        <Button onClick={goToPreviousPage} disabled={currentPage === 1} variant="soft">
                            Previous
                        </Button>
                        <Text>
                            Page {currentPage} of {totalPages}
                        </Text>
                        <Button onClick={goToNextPage} disabled={currentPage === totalPages} variant="soft">
                            Next
                        </Button>
                    </Flex>
                )}
            </Section>
        </Container>
    );
}
