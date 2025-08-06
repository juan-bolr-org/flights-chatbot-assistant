'use client';

import { Box, Button, Flex, Text, TextField, Select } from '@radix-ui/themes';
import { Search, X } from 'lucide-react';
import { useState } from 'react';

export interface BookingSearchFilters {
    status?: string;
    bookedDate?: string;
    departureDate?: string;
}

interface BookingSearchFormProps {
    onSearch: (filters: BookingSearchFilters) => void;
    onClear: () => void;
    isLoading?: boolean;
    hasActiveFilters?: boolean;
}

export function BookingSearchForm({ onSearch, onClear, isLoading = false, hasActiveFilters = false }: BookingSearchFormProps) {
    const [status, setStatus] = useState('');
    const [bookedDate, setBookedDate] = useState('');
    const [departureDate, setDepartureDate] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        
        const filters: BookingSearchFilters = {};
        if (status && status !== 'all') filters.status = status;
        if (bookedDate) filters.bookedDate = bookedDate;
        if (departureDate) filters.departureDate = departureDate;
        
        onSearch(filters);
    };

    const handleClear = () => {
        setStatus('');
        setBookedDate('');
        setDepartureDate('');
        onClear();
    };

    const hasLocalFilters = (status && status !== 'all') || bookedDate || departureDate;

    return (
        <Box mb="6">
            <form onSubmit={handleSubmit}>
                <Flex direction="column" gap="4">
                    <Flex justify="between" align="center">
                        <Text size="4" weight="medium">Filter Bookings</Text>
                        {hasActiveFilters && (
                            <Box px="3" py="1" style={{ backgroundColor: 'var(--blue-3)', borderRadius: '4px' }}>
                                <Text size="2" color="blue" weight="medium">
                                    Filters Active
                                </Text>
                            </Box>
                        )}
                    </Flex>
                    
                    <Flex gap="3" wrap="wrap" align="end">
                        <Box style={{ minWidth: '180px', flex: 1 }}>
                            <Text size="2" weight="medium" mb="2" as="label">
                                Status
                            </Text>
                            <Select.Root value={status} onValueChange={setStatus} disabled={isLoading}>
                                <Select.Trigger placeholder="All statuses" />
                                <Select.Content>
                                    <Select.Item value="all">All statuses</Select.Item>
                                    <Select.Item value="booked">Booked (Upcoming)</Select.Item>
                                    <Select.Item value="completed">Completed</Select.Item>
                                    <Select.Item value="cancelled">Cancelled</Select.Item>
                                </Select.Content>
                            </Select.Root>
                        </Box>
                        
                        <Box style={{ minWidth: '180px', flex: 1 }}>
                            <Text size="2" weight="medium" mb="2" as="label">
                                Booking Date
                            </Text>
                            <TextField.Root
                                type="date"
                                value={bookedDate}
                                onChange={(e) => setBookedDate(e.target.value)}
                                disabled={isLoading}
                                placeholder="Select date"
                            />
                        </Box>
                        
                        <Box style={{ minWidth: '180px', flex: 1 }}>
                            <Text size="2" weight="medium" mb="2" as="label">
                                Departure Date
                            </Text>
                            <TextField.Root
                                type="date"
                                value={departureDate}
                                onChange={(e) => setDepartureDate(e.target.value)}
                                disabled={isLoading}
                                placeholder="Select date"
                            />
                        </Box>
                        
                        <Flex gap="2">
                            <Button 
                                type="submit" 
                                disabled={isLoading}
                                variant="solid"
                            >
                                <Search size={16} />
                                Filter
                            </Button>
                            
                            <Button 
                                type="button" 
                                onClick={handleClear}
                                disabled={isLoading}
                                variant="soft"
                                color="gray"
                            >
                                <X size={16} />
                                {hasActiveFilters ? 'Clear Filters' : 'Clear'}
                            </Button>
                        </Flex>
                    </Flex>
                </Flex>
            </form>
        </Box>
    );
}
