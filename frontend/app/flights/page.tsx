'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { getFlights, searchFlights } from '@/lib/api/flights';
import { Flight, PaginatedFlightsResponse } from '@/lib/types/flight';
import { FlightCard } from '@/components/flights/FlightCard';
import { FlightSearchForm, SearchFilters } from '@/components/flights/FlightSearchForm';
import { FloatingVideoAd } from '@/components/layout/FloatingVideoAd';

import { Button } from '@radix-ui/themes';
import { Text, Flex, Container, Section, Box } from '@radix-ui/themes';

const FLIGHTS_PER_PAGE = 6;

export default function FlightsPage() {
    const [flightData, setFlightData] = useState<PaginatedFlightsResponse | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [searchFilters, setSearchFilters] = useState<SearchFilters>({});
    const [isSearching, setIsSearching] = useState(false);
    const [showVideoAd, setShowVideoAd] = useState(false);
    const hasFetched = useRef(false);
    const router = useRouter();

    const fetchFlights = async (page: number, filters?: SearchFilters) => {
        try {
            setIsLoading(true);
            let response: PaginatedFlightsResponse;
            
            if (filters && (filters.origin || filters.destination || filters.departureDate)) {
                setIsSearching(true);
                response = await searchFlights(
                    filters.origin,
                    filters.destination,
                    filters.departureDate,
                    page,
                    FLIGHTS_PER_PAGE
                );
            } else {
                setIsSearching(false);
                response = await getFlights(page, FLIGHTS_PER_PAGE);
            }
            
            setFlightData(response);
            setError('');
        } catch {
            setError("Can't load Flights, please try again later.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleSearch = async (filters: SearchFilters) => {
        setSearchFilters(filters);
        setCurrentPage(1);
        await fetchFlights(1, filters);
    };

    const handleClearSearch = async () => {
        setSearchFilters({});
        setCurrentPage(1);
        await fetchFlights(1);
    };

    useEffect(() => {
        if (hasFetched.current) return;
        hasFetched.current = true;
        fetchFlights(currentPage);
    }, [router]);

    // Show video ad after a delay to improve UX
    useEffect(() => {
        const timer = setTimeout(() => {
            setShowVideoAd(true);
        }, 3000); // Show after 3 seconds

        return () => clearTimeout(timer);
    }, []);

    const goToNextPage = async () => {
        if (flightData && currentPage < flightData.pages) {
            const nextPage = currentPage + 1;
            setCurrentPage(nextPage);
            await fetchFlights(nextPage, searchFilters);
        }
    };

    const goToPreviousPage = async () => {
        if (currentPage > 1) {
            const prevPage = currentPage - 1;
            setCurrentPage(prevPage);
            await fetchFlights(prevPage, searchFilters);
        }
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
                    <Text size="6" weight="bold">
                        {isSearching ? 'Search Results' : 'All Flights'}
                    </Text>
                </Box>

                <FlightSearchForm 
                    onSearch={handleSearch}
                    onClear={handleClearSearch}
                    isLoading={isLoading}
                />

                <Flex wrap={'wrap'} justify="center" align={'start'} gap="4">
                    {flightData?.items && flightData.items.length > 0 ? (
                        flightData.items.map((flight: Flight) => (
                            <FlightCard flight={flight} key={flight.id} />
                        ))
                    ) : (
                        <Text>
                            {isSearching ? 'No flights found matching your search criteria.' : 'No flights available.'}
                        </Text>
                    )}
                </Flex>
            </Section>
            <Section py="6">
                {flightData && flightData.pages > 1 && (
                    <Flex justify={'center'} align="center" gap="4">
                        <Button onClick={goToPreviousPage} disabled={currentPage === 1} variant="soft">
                            Previous
                        </Button>
                        <Text>
                            Page {currentPage} of {flightData.pages}
                        </Text>
                        <Button onClick={goToNextPage} disabled={currentPage === flightData.pages} variant="soft">
                            Next
                        </Button>
                    </Flex>
                )}
            </Section>
            
            {/* Floating Video Ad */}
            {showVideoAd && (
                <FloatingVideoAd
                    videoSrc="/videos/promotional.mp4"
                    onClose={() => setShowVideoAd(false)}
                    autoPlay={true}
                    showControls={true}
                />
            )}
        </Container>
    );
}
