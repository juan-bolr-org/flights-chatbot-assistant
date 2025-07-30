import { Flight } from '@/lib/types/flight'
import { formatDate } from '@/lib/utils/date'
import { Calendar, Plane, Share } from 'lucide-react'
import Link from 'next/link'
import Image from 'next/image'

interface FlightCardProps {
    flight: Flight
}

export function FlightCard({ flight }: FlightCardProps) {
    return (
        <div className='rounded shadow bg-white min-h-[500px] max-h-[500px] min-w-[350px] max-w-[350px] flex flex-col justify-between'>
            <div className='flex flex-col'>
                <div className="relative h-48">
                    <Image
                        src={'/images/polvora.jpeg'}
                        alt="flight"
                        fill
                        className="object-cover rounded-t"
                    />
                </div>
                <div className='pl-4 pr-4 pt-4 flex flex-col'>
                    <div className='flex justify-between mb-2'>
                        <div className="flex items-center">
                            <span className="inline-block bg-[var(--color-purple)] text-white text-xs font-semibold px-2 py-1 rounded-full">
                                Recommended
                            </span>
                            <span className="inline-block bg-yellow-400 text-yellow-900 text-xs font-semibold px-2 py-1 rounded-full ml-2">
                                Highlighted
                            </span>
                        </div>
                    </div>
                    <div className='min-h-[104px] max-h-[104px]'>
                        <div className="flex flex-col justify-between">
                            <div className="text-xl text-gray-900 font-semibold">To: {flight.destination}</div>
                            <p className="text-sm text-gray-600 mt-1 line-clamp-2">From: {flight.origin}</p>
                        </div>
                    </div>
                </div>
            </div>
            <div className='pl-4 pr-4'>
                <div className="space-y-3">
                    <div className="flex items-center gap-2 text-sm max-h-[40px]">
                        <Calendar className="h-4 w-4 text-gray-500" />
                        <div className='flex flex-col'>
                            <span className="text-gray-700">{formatDate(flight.departure_time)} - {formatDate(flight.arrival_time)}</span>
                        </div>

                    </div>
                    <div className="flex items-center gap-2 text-sm">
                        <Plane className="h-4 w-4 text-gray-500" />
                        <span className="text-gray-700">{flight.airline}</span>
                    </div>
                    <div className="flex justify-between items-center mt-4 pt-3 gradient-border-top">
                        <div className="text-lg font-semibold text-[var(--color-black)]">
                            {flight.status}
                        </div>
                        <div className='flex gap-2 items-center mb-2'>
                            <Share />
                            <Link href={`/flights/${flight.id}`} className="btn btn-primary">
                                Purchase
                            </Link>
                        </div>
                    </div>
                </div>
            </div>
        </div >
    )
}