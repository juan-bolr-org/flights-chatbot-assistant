'use client';

import { Booking } from '@/lib/types/booking';
import { Card, Flex, Text, Box, Badge, Button, AlertDialog } from '@radix-ui/themes';
import { formatDate } from '@/lib/utils/date';
import { useState } from 'react';
import { useToken } from '@/context/UserContext';
import { cancelBooking } from '@/lib/api/booking';

interface BookingCardProps {
    booking: Booking;
    onBookingUpdate?: (updatedBooking: Booking) => void;
}

export function BookingCard({ booking, onBookingUpdate }: BookingCardProps) {
    const { flight } = booking;
    const token = useToken();
    const [isLoading, setIsLoading] = useState(false);

    const canCancel = booking.status === 'booked' && 
                     new Date(flight.departure_time) > new Date();

    const handleCancelBooking = async () => {
        if (!token) return;
        
        setIsLoading(true);
        try {
            const updatedBooking = await cancelBooking(booking.id, token);
            onBookingUpdate?.(updatedBooking);
        } catch (error) {
            console.error('Failed to cancel booking:', error);
            // You might want to show a toast notification here
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Card variant="classic" size="3" style={{ width: '100%' }}>
            <Flex direction="column" gap="3">
                <Flex justify="between" align="center">
                    <Text size="4" weight="bold">
                        {flight.origin} → {flight.destination}
                    </Text>
                    <Flex align="center" gap="2">
                        <Badge color={booking.status === 'cancelled' ? 'red' : 'green'}>
                            {booking.status.toUpperCase()}
                        </Badge>
                        {canCancel && (
                            <AlertDialog.Root>
                                <AlertDialog.Trigger>
                                    <Button 
                                        variant="soft" 
                                        color="red" 
                                        size="1" 
                                        disabled={isLoading}
                                    >
                                        {isLoading ? 'Cancelling...' : 'Cancel'}
                                    </Button>
                                </AlertDialog.Trigger>
                                <AlertDialog.Content style={{ maxWidth: 450 }}>
                                    <AlertDialog.Title>Cancel Booking</AlertDialog.Title>
                                    <AlertDialog.Description size="2">
                                        Are you sure you want to cancel this booking? This action cannot be undone.
                                    </AlertDialog.Description>

                                    <Flex gap="3" mt="4" justify="end">
                                        <AlertDialog.Cancel>
                                            <Button variant="soft" color="gray">
                                                Cancel
                                            </Button>
                                        </AlertDialog.Cancel>
                                        <AlertDialog.Action>
                                            <Button variant="solid" color="red" onClick={handleCancelBooking}>
                                                Yes, Cancel Booking
                                            </Button>
                                        </AlertDialog.Action>
                                    </Flex>
                                </AlertDialog.Content>
                            </AlertDialog.Root>
                        )}
                    </Flex>
                </Flex>

                <Box>
                    <Text as="div" size="2" color="gray">
                        Airline: {flight.airline}
                    </Text>
                    <Text as="div" size="2" color="gray">
                        Departure: {formatDate(flight.departure_time)}
                    </Text>
                    <Text as="div" size="2" color="gray">
                        Arrival: {formatDate(flight.arrival_time)}
                    </Text>
                    <Text as="div" size="2" color="gray">
                        Booking date: {formatDate(booking.booked_at)}
                    </Text>
                    {booking.cancelled_at && (
                        <Text as="div" size="2" color="red">
                            Cancelled at: {formatDate(booking.cancelled_at)}
                        </Text>
                    )}
                </Box>
            </Flex>
        </Card>
    );
}
