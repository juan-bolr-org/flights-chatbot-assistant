'use client';

import { useState, useRef, useEffect } from 'react';
import { Cross2Icon, SpeakerLoudIcon, SpeakerOffIcon, PlayIcon, PauseIcon, MinusIcon, PlusIcon } from '@radix-ui/react-icons';
import { Button } from '@radix-ui/themes';

interface FloatingVideoAdProps {
    videoSrc: string;
    onClose?: () => void;
    autoPlay?: boolean;
    showControls?: boolean;
}

export function FloatingVideoAd({ 
    videoSrc, 
    onClose, 
    autoPlay = false, 
    showControls = true 
}: FloatingVideoAdProps) {
    const [isVisible, setIsVisible] = useState(true);
    const [isPlaying, setIsPlaying] = useState(autoPlay);
    const [isMuted, setIsMuted] = useState(true); // Start muted for better UX
    const [isMinimized, setIsMinimized] = useState(false);
    const [hasPlayedOnce, setHasPlayedOnce] = useState(false);
    const videoRef = useRef<HTMLVideoElement>(null);

    useEffect(() => {
        const video = videoRef.current;
        if (!video) return;

        const handleVideoEnd = () => {
            setIsPlaying(false);
            setIsMinimized(true);
            setHasPlayedOnce(true);
        };

        // Add event listener for when video ends
        video.addEventListener('ended', handleVideoEnd);

        if (isPlaying) {
            video.play().catch(console.error);
        } else {
            video.pause();
        }

        return () => {
            video.removeEventListener('ended', handleVideoEnd);
        };
    }, [isPlaying]);

    const handleClose = () => {
        setIsVisible(false);
        onClose?.();
    };

    const togglePlay = () => {
        setIsPlaying(!isPlaying);
    };

    const toggleMute = () => {
        if (videoRef.current) {
            videoRef.current.muted = !isMuted;
            setIsMuted(!isMuted);
        }
    };

    const toggleMinimize = () => {
        setIsMinimized(!isMinimized);
    };

    if (!isVisible) return null;

    // Responsive adjustments
    const isMobile = typeof window !== 'undefined' && window.innerWidth <= 480;
    const isTablet = typeof window !== 'undefined' && window.innerWidth <= 768 && window.innerWidth > 480;

    const floatingAdStyle = {
        position: 'fixed' as const,
        zIndex: 1000,
        transition: 'all 0.3s ease-in-out',
        boxShadow: '0 10px 25px rgba(0, 0, 0, 0.3)',
        borderRadius: '12px',
        overflow: 'hidden',
        animation: 'slideInFromTopRight 0.5s ease-out',
        top: isMobile ? '90px' : '100px',
        right: isMobile ? '8px' : '16px',
        width: isMinimized 
            ? (isMobile ? '140px' : isTablet ? '160px' : '192px')
            : (isMobile ? '240px' : isTablet ? '280px' : '320px'),
        height: isMinimized 
            ? (isMobile ? '94px' : isTablet ? '108px' : '128px')
            : (isMobile ? '160px' : isTablet ? '200px' : '240px'),
    };

    const videoContainerStyle = {
        position: 'relative' as const,
        width: '100%',
        height: '100%',
        background: '#000',
        borderRadius: '12px',
        overflow: 'hidden',
    };

    const videoStyle = {
        width: '100%',
        height: '100%',
        objectFit: 'cover' as const,
    };

    const controlsOverlayStyle = {
        position: 'absolute' as const,
        inset: '0',
        background: 'linear-gradient(to top, rgba(0, 0, 0, 0.5), transparent)',
        opacity: 0,
        transition: 'opacity 0.2s ease',
    };

    const topControlsStyle = {
        position: 'absolute' as const,
        top: '8px',
        right: '8px',
        display: 'flex',
        gap: '4px',
        zIndex: 10, // Higher z-index to be above drag handle
    };

    const centerControlsStyle = {
        position: 'absolute' as const,
        inset: '0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 5,
    };

    const bottomControlsStyle = {
        position: 'absolute' as const,
        bottom: '8px',
        left: '8px',
        display: 'flex',
        gap: '4px',
        zIndex: 5,
    };

    const controlButtonStyle = {
        background: 'rgba(0, 0, 0, 0.7)',
        color: 'white',
        border: 'none',
        borderRadius: '4px',
        padding: '4px 8px',
        cursor: 'pointer',
        transition: 'background 0.2s ease',
        position: 'relative' as const,
        zIndex: 15, // Highest z-index for buttons
    };

    const dragHandleStyle = {
        position: 'absolute' as const,
        top: '0',
        left: '0',
        width: '60%', // Reduced width to not cover top controls
        height: '24px',
        cursor: 'move',
        background: 'linear-gradient(to bottom, rgba(0, 0, 0, 0.2), transparent)',
        zIndex: 1, // Lower z-index than controls
    };

    return (
        <div style={floatingAdStyle}>
            {/* Video Container */}
            <div style={videoContainerStyle}>
                <video
                    ref={videoRef}
                    src={videoSrc}
                    style={videoStyle}
                    muted={isMuted}
                    playsInline
                    preload="metadata"
                />
                
                {/* Controls Overlay */}
                {showControls && (
                    <div 
                        style={controlsOverlayStyle}
                        onMouseEnter={(e) => e.currentTarget.style.opacity = '1'}
                        onMouseLeave={(e) => e.currentTarget.style.opacity = '0'}
                    >
                        {/* Top Controls */}
                        <div style={topControlsStyle}>
                            <Button
                                size="1"
                                variant="soft"
                                style={controlButtonStyle}
                                onClick={toggleMinimize}
                                onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(0, 0, 0, 0.9)'}
                                onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(0, 0, 0, 0.7)'}
                            >
                                {isMinimized ? <PlusIcon /> : <MinusIcon />}
                            </Button>
                            <Button
                                size="1"
                                variant="soft"
                                style={controlButtonStyle}
                                onClick={handleClose}
                                onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(0, 0, 0, 0.9)'}
                                onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(0, 0, 0, 0.7)'}
                            >
                                <Cross2Icon />
                            </Button>
                        </div>

                        {/* Center Play/Pause Button */}
                        <div style={centerControlsStyle}>
                            <Button
                                size="3"
                                variant="soft"
                                style={controlButtonStyle}
                                onClick={togglePlay}
                                onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(0, 0, 0, 0.9)'}
                                onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(0, 0, 0, 0.7)'}
                            >
                                {isPlaying ? <PauseIcon /> : <PlayIcon />}
                            </Button>
                        </div>

                        {/* Bottom Controls */}
                        <div style={bottomControlsStyle}>
                            <Button
                                size="1"
                                variant="soft"
                                style={controlButtonStyle}
                                onClick={toggleMute}
                                onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(0, 0, 0, 0.9)'}
                                onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(0, 0, 0, 0.7)'}
                            >
                                {isMuted ? <SpeakerOffIcon /> : <SpeakerLoudIcon />}
                            </Button>
                        </div>
                    </div>
                )}
            </div>

            {/* Drag Handle */}
            <div style={dragHandleStyle} />
        </div>
    );
}
