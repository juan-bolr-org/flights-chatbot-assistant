'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { getUserBookings } from '@/lib/api/booking';
import { Booking } from '@/lib/types/booking';
import { BookingCard } from '@/components/bookings/BookingCard';
import { useUser } from '@/context/UserContext';
import { useToken } from '@/context/UserContext';

import { Button, Container, Flex, Section, Text, Box } from '@radix-ui/themes';

const BOOKINGS_PER_PAGE = 5;

export default function BookingsPage() {
    const [bookings, setBookings] = useState<Booking[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const hasFetched = useRef(false);
    const router = useRouter();
    const { user } = useUser();
    const token = useToken();

    const handleBookingUpdate = (updatedBooking: Booking) => {
        setBookings(prevBookings => 
            prevBookings.map(booking => 
                booking.id === updatedBooking.id ? updatedBooking : booking
            )
        );
    };

    useEffect(() => {
        if (hasFetched.current) return;
        hasFetched.current = true;

        const fetchBookings = async () => {
            try {
                if (!user) {
                    router.replace('/login');
                    return;
                }
                if (user?.token) {
                    const result = await getUserBookings(user.token.access_token);
                    setBookings(result);
                } else {
                    setError('User token is missing. Please log in again.');
                }
            } catch {
                setError("Can't load your bookings. Please try again.");
            } finally {
                setIsLoading(false);
            }
        };

        fetchBookings();
    }, [router]);

    const totalPages = Math.ceil(bookings.length / BOOKINGS_PER_PAGE);
    const paginatedBookings = bookings.slice(
        (currentPage - 1) * BOOKINGS_PER_PAGE,
        currentPage * BOOKINGS_PER_PAGE
    );

    const goToNextPage = () => currentPage < totalPages && setCurrentPage((prev) => prev + 1);
    const goToPreviousPage = () => currentPage > 1 && setCurrentPage((prev) => prev - 1);

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

                <Flex direction="column" gap="4" align="stretch">
                    {paginatedBookings.length > 0 ? (
                        paginatedBookings.map((booking) => (
                            <BookingCard 
                                key={booking.id} 
                                booking={booking} 
                                onBookingUpdate={handleBookingUpdate}
                            />
                        ))
                    ) : (
                        <Text>No bookings found.</Text>
                    )}
                </Flex>
            </Section>

            {totalPages > 1 && (
                <Section pt="6">
                    <Flex justify="center" align="center" gap="4">
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
                </Section>
            )}
        </Container>
    );
}
