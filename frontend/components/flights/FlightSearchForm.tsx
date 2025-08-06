'use client';

import { useState } from 'react';
import { Button, TextField, Flex, Box, Text } from '@radix-ui/themes';
import { Search, X } from 'lucide-react';

interface FlightSearchFormProps {
    onSearch: (filters: SearchFilters) => void;
    onClear: () => void;
    isLoading?: boolean;
}

export interface SearchFilters {
    origin?: string;
    destination?: string;
    departureDate?: string;
}

export function FlightSearchForm({ onSearch, onClear, isLoading = false }: FlightSearchFormProps) {
    const [origin, setOrigin] = useState('');
    const [destination, setDestination] = useState('');
    const [departureDate, setDepartureDate] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        
        const filters: SearchFilters = {};
        if (origin.trim()) filters.origin = origin.trim();
        if (destination.trim()) filters.destination = destination.trim();
        if (departureDate) filters.departureDate = departureDate;
        
        onSearch(filters);
    };

    const handleClear = () => {
        setOrigin('');
        setDestination('');
        setDepartureDate('');
        onClear();
    };

    const hasFilters = origin || destination || departureDate;

    return (
        <Box mb="6">
            <form onSubmit={handleSubmit}>
                <Flex direction="column" gap="4">
                    <Text size="4" weight="medium">Search Flights</Text>
                    
                    <Flex gap="3" wrap="wrap" align="end">
                        <Box style={{ minWidth: '200px', flex: 1 }}>
                            <Text size="2" weight="medium" mb="2" as="label">
                                From (Origin)
                            </Text>
                            <TextField.Root
                                placeholder="e.g., NYC, JFK, New York"
                                value={origin}
                                onChange={(e) => setOrigin(e.target.value)}
                                disabled={isLoading}
                            />
                        </Box>
                        
                        <Box style={{ minWidth: '200px', flex: 1 }}>
                            <Text size="2" weight="medium" mb="2" as="label">
                                To (Destination)
                            </Text>
                            <TextField.Root
                                placeholder="e.g., LAX, Los Angeles"
                                value={destination}
                                onChange={(e) => setDestination(e.target.value)}
                                disabled={isLoading}
                            />
                        </Box>
                        
                        <Box style={{ minWidth: '200px', flex: 1 }}>
                            <Text size="2" weight="medium" mb="2" as="label">
                                Departure Date
                            </Text>
                            <TextField.Root
                                type="date"
                                value={departureDate}
                                onChange={(e) => setDepartureDate(e.target.value)}
                                disabled={isLoading}
                            />
                        </Box>
                        
                        <Flex gap="2">
                            <Button 
                                type="submit" 
                                disabled={isLoading}
                                variant="solid"
                            >
                                <Search size={16} />
                                Search
                            </Button>
                            
                            {hasFilters && (
                                <Button 
                                    type="button" 
                                    onClick={handleClear}
                                    disabled={isLoading}
                                    variant="soft"
                                    color="gray"
                                >
                                    <X size={16} />
                                    Clear
                                </Button>
                            )}
                        </Flex>
                    </Flex>
                </Flex>
            </form>
        </Box>
    );
}
