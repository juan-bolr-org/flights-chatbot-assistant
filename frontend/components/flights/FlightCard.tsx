'use client';

import { Flight } from '@/lib/types/flight';
import { formatDate } from '@/lib/utils/date';
import { formatCurrency } from '@/lib/utils/currency';
import { Calendar, Plane, Share } from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';
import {
    Card,
    Flex,
    Text,
    Heading,
    Button,
    Badge,
    Box,
} from '@radix-ui/themes';

interface FlightCardProps {
    flight: Flight;
}

export function FlightCard({ flight }: FlightCardProps) {
    return (
        <Card
            size="3"
            style={{
                minHeight: 500,
                maxHeight: 500,
                minWidth: 350,
                maxWidth: 350,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
            }}
        >
            {/* Imagen */}
            <Box style={{ position: 'relative', height: '12rem' }}>
                <Image
                    src={'/images/polvora.jpeg'}
                    alt="flight"
                    fill
                    style={{ objectFit: 'cover', borderTopLeftRadius: 8, borderTopRightRadius: 8 }}
                />
            </Box>

            {/* Etiquetas y Título */}
            <Box px="4" pt="4">
                <Flex justify="between" mb="2">
                    <Flex gap="2">
                        <Badge radius='large' variant="solid" highContrast>
                            Recommended
                        </Badge>
                        <Badge radius='large' variant="soft" highContrast>
                            Highlighted
                        </Badge>
                    </Flex>
                    {flight.status === 'scheduled' ? (
                        <Badge radius='large' variant="solid" color="green" highContrast>
                            On Time
                        </Badge>
                    ) : (
                        <Badge radius='large' variant="solid" color="red" highContrast>
                            Delayed
                        </Badge>
                    )}
                </Flex>
                <Box style={{ minHeight: 50, maxHeight: 50 }}>
                    <Heading as="h3" size="4">
                        From: {flight.origin}
                    </Heading>
                    <Heading as="h3" size="4">
                        To: {flight.destination}
                    </Heading>
                </Box>
            </Box>

            {/* Detalles de Vuelo */}
            <Box px="4">
                <Flex direction="column" gap="3" mt="2">
                    <Flex direction="row" gap="2" align="center">
                        <Calendar className="h-4 w-4 text-gray-500" />
                        <Text weight={"bold"} size="2" color="gray">
                            Departure: <br /> {formatDate(flight.departure_time)}
                        </Text>
                        <Calendar className="h-4 w-4 text-gray-500" />
                        <Text weight={"bold"} size="2" color="gray">
                            Arrival: <br /> {formatDate(flight.arrival_time)}
                        </Text>
                    </Flex>
                    <Flex gap="2" align="center">
                        <Plane className="h-4 w-4 text-gray-500" />
                        <Text size="2" color="gray">{flight.airline}</Text>
                    </Flex>
                </Flex>

                {/* Footer */}
                <Flex justify="between" align="center" mt="4" pt="3" style={{ borderTop: '1px solid #eee' }}>
                    <Text size="2" color="green">
                        {formatCurrency(flight.price, 'USD')}
                    </Text>

                    <Flex gap="3" align="center">
                        <Link href={`/flights/${flight.id}`}>
                            <Button highContrast>
                                Purchase
                            </Button>
                        </Link>
                    </Flex>
                </Flex>
            </Box>
        </Card>
    );
}
