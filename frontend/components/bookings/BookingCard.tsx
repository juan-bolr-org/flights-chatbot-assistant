'use client';

import { Booking } from '@/lib/types/booking';
import { Card, Flex, Text, Box, Badge } from '@radix-ui/themes';
import { formatDate } from '@/lib/utils/date';

interface BookingCardProps {
    booking: Booking;
}

export function BookingCard({ booking }: BookingCardProps) {
    const { flight } = booking;

    return (
        <Card variant="classic" size="3" style={{ width: '100%' }}>
            <Flex direction="column" gap="3">
                <Flex justify="between" align="center">
                    <Text size="4" weight="bold">
                        {flight.origin} → {flight.destination}
                    </Text>
                    <Badge color={booking.status === 'cancelled' ? 'red' : 'green'}>
                        {booking.status.toUpperCase()}
                    </Badge>
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
