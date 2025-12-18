"use client";

import { useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { Region } from "@/types";

// Fix for default marker icon in Next.js
const icon = L.icon({
    iconUrl: "/images/marker-icon.png",
    shadowUrl: "/images/marker-shadow.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41],
});

// Helper to update map view
function MapUpdater({ center }: { center: [number, number] }) {
    const map = useMap();
    useEffect(() => {
        map.setView(center, map.getZoom());
    }, [center, map]);
    return null;
}

interface MapViewProps {
    regions: Region[];
    selectedRegionId?: number;
    onSelectRegion: (id: number) => void;
}

export default function MapView({ regions, selectedRegionId, onSelectRegion }: MapViewProps) {
    // Default center (Morocco)
    const defaultCenter: [number, number] = [31.7917, -7.0926];

    const selectedRegion = regions.find((r) => r.id === selectedRegionId);
    const center = selectedRegion
        ? ([selectedRegion.latitude, selectedRegion.longitude] as [number, number])
        : defaultCenter;

    // We need to fix the icon path issue manually or use a CDN
    // For simplicity, let's try using a standard CDN for icons if local assets aren't set up
    useEffect(() => {
        // @ts-ignore
        delete L.Icon.Default.prototype._getIconUrl;
        L.Icon.Default.mergeOptions({
            iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
            iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
        });
    }, []);

    return (
        <div className="h-[400px] w-full rounded-lg overflow-hidden border border-gray-200 z-0">
            <MapContainer center={defaultCenter} zoom={6} scrollWheelZoom={false} className="h-full w-full">
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <MapUpdater center={center} />
                {regions.map((region) => (
                    <Marker
                        key={region.id}
                        position={[region.latitude, region.longitude]}
                        eventHandlers={{
                            click: () => onSelectRegion(region.id),
                        }}
                    >
                        <Popup>
                            <div className="font-semibold">{region.name}</div>
                            <div className="text-xs text-gray-500">
                                Lat: {region.latitude}, Lng: {region.longitude}
                            </div>
                        </Popup>
                    </Marker>
                ))}
            </MapContainer>
        </div>
    );
}
