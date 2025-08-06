'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Container, Section, Box, Text, Button, Flex } from '@radix-ui/themes';
import { BookingCard } from '@/components/bookings/BookingCard';
import { BookingSearchForm, BookingSearchFilters } from '@/components/bookings/BookingSearchForm';
import { getUserBookings } from '@/lib/api/booking';
import { useUser, useToken } from '@/context/UserContext';
import { Booking, PaginatedBookingsResponse } from '@/lib/types/booking';

const BOOKINGS_PER_PAGE = 10;

export default function BookingsPage() {
    const [bookingData, setBookingData] = useState<PaginatedBookingsResponse | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [searchFilters, setSearchFilters] = useState<BookingSearchFilters>({});
    const [isSearching, setIsSearching] = useState(false);
    const hasActiveFilters = Boolean(searchFilters && (searchFilters.status || searchFilters.bookedDate || searchFilters.departureDate));
    const hasFetched = useRef(false);
    const router = useRouter();
    const { user } = useUser();
    const token = useToken();

    const fetchBookings = async (page: number, filters?: BookingSearchFilters) => {
        try {
            setIsLoading(true);
            if (!user?.token) {
                setError('User token is missing. Please log in again.');
                return;
            }

            let hasActiveFilters = false;
            if (filters && (filters.status || filters.bookedDate || filters.departureDate)) {
                setIsSearching(true);
                hasActiveFilters = true;
            } else {
                setIsSearching(false);
            }

            const response = await getUserBookings(
                user.token.access_token,
                filters?.status,
                filters?.bookedDate,
                filters?.departureDate,
                page,
                BOOKINGS_PER_PAGE
            );
            
            setBookingData(response);
            setError('');
        } catch {
            setError("Can't load your bookings. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleSearch = async (filters: BookingSearchFilters) => {
        setSearchFilters(filters);
        setCurrentPage(1);
        await fetchBookings(1, filters);
    };

    const handleClearSearch = async () => {
        setSearchFilters({});
        setCurrentPage(1);
        await fetchBookings(1);
    };

    const handleBookingUpdate = (updatedBooking: Booking) => {
        if (!bookingData) return;
        
        setBookingData(prevData => ({
            ...prevData!,
            items: prevData!.items.map(booking => 
                booking.id === updatedBooking.id ? updatedBooking : booking
            )
        }));
    };

    useEffect(() => {
        if (hasFetched.current) return;
        hasFetched.current = true;

        const fetchInitialBookings = async () => {
            try {
                if (!user) {
                    router.replace('/login');
                    return;
                }
                await fetchBookings(currentPage);
            } catch {
                setError("Can't load your bookings. Please try again.");
            }
        };

        fetchInitialBookings();
    }, [router]);

    const goToNextPage = async () => {
        if (bookingData && currentPage < bookingData.pages) {
            const nextPage = currentPage + 1;
            setCurrentPage(nextPage);
            await fetchBookings(nextPage, searchFilters);
        }
    };

    const goToPreviousPage = async () => {
        if (currentPage > 1) {
            const prevPage = currentPage - 1;
            setCurrentPage(prevPage);
            await fetchBookings(prevPage, searchFilters);
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
        <Container align="center" size="3" py="4">
            <Section>
                <Box pb="6">
                    <Text size="6" weight="bold">
                        My Bookings
                    </Text>
                </Box>

                <BookingSearchForm 
                    onSearch={handleSearch}
                    onClear={handleClearSearch}
                    isLoading={isLoading}
                    hasActiveFilters={hasActiveFilters}
                />

                <Flex direction="column" gap="4" align="stretch">
                    {bookingData && bookingData.items.length > 0 ? (
                        <>
                            {hasActiveFilters && (
                                <Box p="3" style={{ backgroundColor: 'var(--blue-2)', borderRadius: '6px' }}>
                                    <Text size="2" color="blue">
                                        Showing filtered results ({bookingData.total} booking{bookingData.total !== 1 ? 's' : ''} found)
                                    </Text>
                                </Box>
                            )}
                            {bookingData.items.map((booking) => (
                                <BookingCard 
                                    key={booking.id} 
                                    booking={booking} 
                                    onBookingUpdate={handleBookingUpdate}
                                />
                            ))}
                        </>
                    ) : (
                        <Box p="6" style={{ textAlign: 'center' }}>
                            <Text>
                                {hasActiveFilters 
                                    ? 'No bookings found matching your filters.' 
                                    : 'No bookings found.'
                                }
                            </Text>
                            {hasActiveFilters && (
                                <Box mt="3">
                                    <Button 
                                        variant="soft" 
                                        onClick={handleClearSearch}
                                    >
                                        Clear filters to see all bookings
                                    </Button>
                                </Box>
                            )}
                        </Box>
                    )}
                </Flex>
            </Section>

            {bookingData && bookingData.pages > 1 && (
                <Section pt="6">
                    <Flex justify="center" align="center" gap="4">
                        <Button 
                            onClick={goToPreviousPage} 
                            disabled={currentPage === 1} 
                            variant="soft"
                        >
                            Previous
                        </Button>
                        <Text>
                            Page {currentPage} of {bookingData.pages}
                        </Text>
                        <Button 
                            onClick={goToNextPage} 
                            disabled={currentPage === bookingData.pages} 
                            variant="soft"
                        >
                            Next
                        </Button>
                    </Flex>
                </Section>
            )}
        </Container>
    );
}
