// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

'use client';

import { useState, useRef, useEffect } from 'react';
import { Play, Pause, Volume2, VolumeX, Maximize2, Video } from 'lucide-react';

// Traffic camera locations in Hanoi with video files
export interface TrafficCamera {
  id: string;
  name: string;
  location: [number, number]; // [lat, lng]
  videoUrl: string;
  description?: string;
  status: 'online' | 'offline' | 'demo';
}

// Demo traffic cameras with video files
export const TRAFFIC_CAMERAS: TrafficCamera[] = [
  {
    id: 'cam-1',
    name: 'Phạm Văn Bạch - Viện Huyết Học',
    location: [21.024933, 105.789105], // Ngã tư Phạm Văn Bạch - Đường Láng
    videoUrl: '/video_traffic/HNI_LLGT_Phạm Văn Bạch- Viện Huyết Học.mp4',
    description: 'Camera giao thông ngã tư Phạm Văn Bạch - Viện Huyết Học',
    status: 'demo',
  },
  {
    id: 'cam-2',
    name: 'Khuất Duy Tiến - Nguyễn Xiển (Góc 1)',
    location: [20.991118, 105.802930], // Ngã tư Khuất Duy Tiến - Nguyễn Xiển
    videoUrl: '/video_traffic/HNI_NT_KDT_Khuất Duy Tiến - Nguyễn Xiển 1.mp4',
    description: 'Camera giao thông Khuất Duy Tiến - Nguyễn Xiển góc 1',
    status: 'demo',
  },
  {
    id: 'cam-3',
    name: 'Khuất Duy Tiến - Nguyễn Xiển (Góc 2)',
    location: [20.991761, 105.803992], // Góc 2 của ngã tư
    videoUrl: '/video_traffic/HNI_NT_KDT_Khuất Duy Tiến - Nguyễn Xiển 2.mp4',
    description: 'Camera giao thông Khuất Duy Tiến - Nguyễn Xiển góc 2',
    status: 'demo',
  },
  {
    id: 'cam-4',
    name: 'Nguyễn Xiển - Khuất Duy Tiến',
    location: [20.992635, 105.802553], // Góc 3 của ngã tư
    videoUrl: '/video_traffic/HNI_NT_KDT_Nguyễn Xiển-Khuất Duy Tiến.mp4',
    description: 'Camera giao thông ngã tư Nguyễn Xiển - Khuất Duy Tiến',
    status: 'demo',
  },
];

interface TrafficCameraPopupProps {
  camera: TrafficCamera;
}

// Compact popup content for Leaflet Popup - renders directly in map
export function TrafficCameraPopup({ camera }: TrafficCameraPopupProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(true);

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const toggleFullscreen = () => {
    if (videoRef.current) {
      if (!document.fullscreenElement) {
        videoRef.current.requestFullscreen();
      } else {
        document.exitFullscreen();
      }
    }
  };

  // Auto-play when opened
  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.play().then(() => setIsPlaying(true)).catch(() => {});
    }
  }, []);

  return (
    <div className="w-[320px]">
      {/* Header - Compact */}
      <div className="flex items-center gap-2 mb-2">
        <div className="flex items-center justify-center w-8 h-8 rounded-full bg-red-600/20">
          <Video className="w-4 h-4 text-red-500" />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-sm text-gray-900 dark:text-white truncate">{camera.name}</h3>
          <span className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-medium ${
            camera.status === 'online' ? 'bg-green-600/20 text-green-600' :
            camera.status === 'demo' ? 'bg-yellow-600/20 text-yellow-600' :
            'bg-red-600/20 text-red-600'
          }`}>
            {camera.status === 'online' ? '● Live' : 
             camera.status === 'demo' ? '● Demo' : '● Offline'}
          </span>
        </div>
      </div>

      {/* Video Player - Compact */}
      <div className="relative aspect-video bg-black rounded-lg overflow-hidden shadow-lg">
        <video
          ref={videoRef}
          src={camera.videoUrl}
          className="w-full h-full object-cover"
          loop
          muted={isMuted}
          playsInline
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
        />

        {/* Video Controls - Overlay */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent p-2">
          <div className="flex items-center gap-1">
            {/* Play/Pause */}
            <button
              onClick={togglePlay}
              className="p-1.5 hover:bg-white/20 rounded transition-colors"
              title={isPlaying ? 'Tạm dừng' : 'Phát'}
            >
              {isPlaying ? (
                <Pause className="w-4 h-4 text-white" />
              ) : (
                <Play className="w-4 h-4 text-white" />
              )}
            </button>

            {/* Volume */}
            <button
              onClick={toggleMute}
              className="p-1.5 hover:bg-white/20 rounded transition-colors"
              title={isMuted ? 'Bật tiếng' : 'Tắt tiếng'}
            >
              {isMuted ? (
                <VolumeX className="w-4 h-4 text-white" />
              ) : (
                <Volume2 className="w-4 h-4 text-white" />
              )}
            </button>

            <div className="flex-1" />

            {/* Fullscreen */}
            <button
              onClick={toggleFullscreen}
              className="p-1.5 hover:bg-white/20 rounded transition-colors"
              title="Toàn màn hình"
            >
              <Maximize2 className="w-4 h-4 text-white" />
            </button>
          </div>
        </div>

        {/* Live indicator */}
        {camera.status === 'online' && (
          <div className="absolute top-2 left-2 px-2 py-1 bg-red-600 text-white text-xs font-bold rounded flex items-center gap-1">
            <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>
            LIVE
          </div>
        )}
      </div>
    </div>
  );
}
