import React, { useState, useEffect, useCallback } from 'react';
import {
  X,
  MapPin,
  Navigation,
  Phone,
  Clock,
  ExternalLink,
  Compass,
  AlertCircle,
  Sparkles,
  RefreshCw,
  Search,
  CheckCircle2,
  Building2
} from 'lucide-react';
import apiService, { extractErrorMessage } from '../services/api';
import type { RecyclingCenterItem, RecyclingSearchResponse } from '../types';

interface RecyclingCenterModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialWasteType?: string;
}

const WASTE_CATEGORIES = [
  { id: 'biodegradable', label: 'Biodegradable', desc: 'Food scraps, compostables, organic waste', color: 'emerald' },
  { id: 'cardboard', label: 'Cardboard', desc: 'Packaging boxes, cartons, paperboard', color: 'amber' },
  { id: 'e_waste', label: 'E-Waste', desc: 'Electronics, circuit boards, batteries', color: 'purple' },
  { id: 'glass', label: 'Glass', desc: 'Bottles, jars, beverage glassware', color: 'teal' },
  { id: 'metal', label: 'Metal', desc: 'Aluminum cans, scrap metal, tins', color: 'slate' },
  { id: 'paper', label: 'Paper', desc: 'Office paper, newspapers, magazines', color: 'blue' },
  { id: 'plastic', label: 'Plastic', desc: 'PET/HDPE bottles, plastic containers', color: 'yellow' },
  { id: 'trash', label: 'Trash', desc: 'Municipal solid waste, transfer stations', color: 'stone' },
];

const PRESET_LOCATIONS = [
  { name: 'Navi Mumbai (Vashi)', lat: 19.0772, lng: 72.9981 },
  { name: 'Mumbai (Andheri E)', lat: 19.1197, lng: 72.8826 },
  { name: 'Thane (Wagle)', lat: 19.1915, lng: 72.9510 },
  { name: 'Mumbai (Central)', lat: 19.0410, lng: 72.8540 },
  { name: 'Bandra (Reclamation)', lat: 19.0434, lng: 72.8315 },
  { name: 'Turbhe (MIDC)', lat: 19.0834, lng: 73.0162 },
  { name: 'Pune (Shivajinagar)', lat: 18.5314, lng: 73.8446 },
  { name: 'Delhi (Connaught)', lat: 28.6315, lng: 77.2167 },
  { name: 'Bengaluru (CBD)', lat: 12.9716, lng: 77.5946 },
];

const RADIUS_OPTIONS = [1, 2, 5, 10, 20, 50];

export const RecyclingCenterModal: React.FC<RecyclingCenterModalProps> = ({
  isOpen,
  onClose,
  initialWasteType = 'plastic',
}) => {
  const [selectedWasteType, setSelectedWasteType] = useState<string>(initialWasteType.toLowerCase());
  const [selectedRadius, setSelectedRadius] = useState<number>(10);
  const [latitude, setLatitude] = useState<number>(19.0772);
  const [longitude, setLongitude] = useState<number>(72.9981);
  const [locationLabel, setLocationLabel] = useState<string>('Navi Mumbai (Vashi)');
  const [isLocating, setIsLocating] = useState<boolean>(false);
  const [locationError, setLocationError] = useState<string | null>(null);

  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [searchResponse, setSearchResponse] = useState<RecyclingSearchResponse | null>(null);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [customCoordMode, setCustomCoordMode] = useState<boolean>(false);

  // Sync initial waste type when opened
  useEffect(() => {
    if (initialWasteType) {
      setSelectedWasteType(initialWasteType.toLowerCase());
    }
  }, [initialWasteType, isOpen]);

  // Execute Search
  const executeSearch = useCallback(async (
    targetWaste: string = selectedWasteType,
    targetLat: number = latitude,
    targetLng: number = longitude,
    targetRadius: number = selectedRadius
  ) => {
    setIsSearching(true);
    setSearchError(null);

    try {
      const response = await apiService.searchRecyclingCenters({
        waste_type: targetWaste,
        latitude: targetLat,
        longitude: targetLng,
        radius_km: targetRadius,
        limit: 10,
      });
      setSearchResponse(response);
    } catch (err) {
      setSearchError(extractErrorMessage(err));
    } finally {
      setIsSearching(false);
    }
  }, [selectedWasteType, latitude, longitude, selectedRadius]);

  // Auto-trigger search upon initial opening if not searched yet
  useEffect(() => {
    if (isOpen && !searchResponse && !isSearching) {
      executeSearch();
    }
  }, [isOpen, searchResponse, isSearching, executeSearch]);

  // Browser Geolocation Flow
  const handleUseCurrentLocation = () => {
    if (!navigator.geolocation) {
      setLocationError('Geolocation is not supported by your browser. Please select a regional hub below.');
      return;
    }

    setIsLocating(true);
    setLocationError(null);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = parseFloat(position.coords.latitude.toFixed(4));
        const lng = parseFloat(position.coords.longitude.toFixed(4));
        setLatitude(lat);
        setLongitude(lng);
        setLocationLabel('My Current GPS Location');
        setIsLocating(false);
        // Automatically search with newly detected coordinates
        executeSearch(selectedWasteType, lat, lng, selectedRadius);
      },
      (error) => {
        setIsLocating(false);
        if (error.code === error.PERMISSION_DENIED) {
          setLocationError('Location permission denied. Please select a city or area from the options below.');
        } else if (error.code === error.TIMEOUT) {
          setLocationError('Location request timed out. Please select your regional area.');
        } else {
          setLocationError('Unable to retrieve current location. Please choose a nearby area.');
        }
      },
      { timeout: 10000, enableHighAccuracy: true }
    );
  };

  // Preset location handler
  const handleSelectPreset = (preset: { name: string; lat: number; lng: number }) => {
    setLatitude(preset.lat);
    setLongitude(preset.lng);
    setLocationLabel(preset.name);
    setLocationError(null);
    executeSearch(selectedWasteType, preset.lat, preset.lng, selectedRadius);
  };

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 backdrop-blur-sm p-4 sm:p-6 overflow-y-auto">
      <div className="bg-white rounded-3xl max-w-3xl w-full max-h-[90vh] flex flex-col shadow-2xl border border-slate-200 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-slate-100 bg-slate-50/70">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center shadow-sm">
              <Building2 className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-extrabold text-slate-900 text-lg sm:text-xl tracking-tight">
                Smart Recycling Center Finder
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Discover nearby collection hubs &amp; recycling depots sorted by proximity
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          {/* Controls Grid */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-4 bg-slate-50 p-4 rounded-2xl border border-slate-200/80">
            {/* Waste Category Selector (5 cols) */}
            <div className="md:col-span-6 space-y-1.5">
              <label className="text-xs font-bold text-slate-700 flex items-center justify-between">
                <span>Waste Category</span>
                <span className="text-[10px] text-emerald-600 font-semibold uppercase tracking-wider">8 Classes</span>
              </label>
              <select
                value={selectedWasteType}
                onChange={(e) => {
                  setSelectedWasteType(e.target.value);
                  executeSearch(e.target.value, latitude, longitude, selectedRadius);
                }}
                className="w-full bg-white border border-slate-300 rounded-xl px-3 py-2.5 text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 capitalize shadow-sm"
              >
                {WASTE_CATEGORIES.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.label} ({cat.desc})
                  </option>
                ))}
              </select>
            </div>

            {/* Radius Selector (3 cols) */}
            <div className="md:col-span-3 space-y-1.5">
              <label className="text-xs font-bold text-slate-700">Search Radius</label>
              <select
                value={selectedRadius}
                onChange={(e) => {
                  const r = Number(e.target.value);
                  setSelectedRadius(r);
                  executeSearch(selectedWasteType, latitude, longitude, r);
                }}
                className="w-full bg-white border border-slate-300 rounded-xl px-3 py-2.5 text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 shadow-sm"
              >
                {RADIUS_OPTIONS.map((r) => (
                  <option key={r} value={r}>
                    {r} km Radius
                  </option>
                ))}
              </select>
            </div>

            {/* Search Action Button (3 cols) */}
            <div className="md:col-span-3 flex items-end">
              <button
                onClick={() => executeSearch(selectedWasteType, latitude, longitude, selectedRadius)}
                disabled={isSearching}
                className="w-full py-2.5 px-3 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-300 text-white font-bold text-xs rounded-xl transition shadow-sm flex items-center justify-center gap-1.5"
              >
                {isSearching ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Searching...</span>
                  </>
                ) : (
                  <>
                    <Search className="w-3.5 h-3.5" />
                    <span>Search</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Location Bar & Quick Presets */}
          <div className="space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2 text-xs font-bold text-slate-700">
                <MapPin className="w-4 h-4 text-emerald-600" />
                <span>Search Location:</span>
                <span className="font-semibold text-slate-900 bg-slate-100 px-2.5 py-1 rounded-md border border-slate-200">
                  {locationLabel} ({latitude.toFixed(2)}°, {longitude.toFixed(2)}°)
                </span>
              </div>

              {/* GPS Button */}
              <button
                onClick={handleUseCurrentLocation}
                disabled={isLocating}
                className="text-xs font-bold text-emerald-700 hover:text-emerald-800 bg-emerald-50 hover:bg-emerald-100 px-3 py-1.5 rounded-xl border border-emerald-200 transition flex items-center gap-1.5"
              >
                {isLocating ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin text-emerald-600" />
                    <span>Detecting GPS...</span>
                  </>
                ) : (
                  <>
                    <Navigation className="w-3.5 h-3.5 text-emerald-600" />
                    <span>Use My Current Location</span>
                  </>
                )}
              </button>
            </div>

            {/* Error or Warning regarding Location */}
            {locationError && (
              <div className="text-xs text-amber-800 bg-amber-50 border border-amber-200 rounded-xl p-3 flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                <span>{locationError}</span>
              </div>
            )}

            {/* Preset Area Pills */}
            <div className="space-y-1.5">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                Popular Regional Hubs:
              </span>
              <div className="flex flex-wrap gap-1.5">
                {PRESET_LOCATIONS.map((preset) => (
                  <button
                    key={preset.name}
                    onClick={() => handleSelectPreset(preset)}
                    className={`text-[11px] px-2.5 py-1 rounded-lg border font-medium transition ${
                      locationLabel === preset.name
                        ? 'bg-emerald-600 text-white border-emerald-600 shadow-sm'
                        : 'bg-white text-slate-600 border-slate-200 hover:border-emerald-300 hover:bg-emerald-50/50'
                    }`}
                  >
                    {preset.name}
                  </button>
                ))}
                <button
                  onClick={() => setCustomCoordMode(!customCoordMode)}
                  className="text-[11px] px-2.5 py-1 rounded-lg border border-dashed border-slate-300 text-slate-500 hover:text-slate-800 hover:border-slate-400"
                >
                  {customCoordMode ? 'Hide Custom Coords' : '+ Custom Lat/Lng'}
                </button>
              </div>
            </div>

            {/* Custom Coordinates Collapsible */}
            {customCoordMode && (
              <div className="flex items-center gap-2 pt-2 text-xs">
                <input
                  type="number"
                  step="0.0001"
                  value={latitude}
                  onChange={(e) => setLatitude(parseFloat(e.target.value) || 0)}
                  placeholder="Latitude"
                  className="w-28 px-2 py-1 border border-slate-300 rounded-lg text-xs"
                />
                <input
                  type="number"
                  step="0.0001"
                  value={longitude}
                  onChange={(e) => setLongitude(parseFloat(e.target.value) || 0)}
                  placeholder="Longitude"
                  className="w-28 px-2 py-1 border border-slate-300 rounded-lg text-xs"
                />
                <button
                  onClick={() => {
                    setLocationLabel(`Custom (${latitude.toFixed(2)}, ${longitude.toFixed(2)})`);
                    executeSearch(selectedWasteType, latitude, longitude, selectedRadius);
                  }}
                  className="bg-slate-800 text-white px-3 py-1 rounded-lg font-bold text-xs hover:bg-slate-700"
                >
                  Apply
                </button>
              </div>
            )}
          </div>

          {/* Search Error Alert */}
          {searchError && (
            <div className="text-xs text-rose-800 bg-rose-50 border border-rose-200 rounded-xl p-4 flex items-start gap-2.5">
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
              <div>
                <p className="font-bold">Search Error</p>
                <p className="text-rose-700 mt-0.5">{searchError}</p>
              </div>
            </div>
          )}

          {/* Results List */}
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-2">
              <h4 className="font-bold text-slate-900 text-sm flex items-center gap-2">
                <span>Nearby Recycling Facilities</span>
                {searchResponse && (
                  <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
                    {searchResponse.total_results} Found
                  </span>
                )}
              </h4>
              {searchResponse && (
                <span className="text-[11px] font-semibold text-slate-400">
                  Source: {searchResponse.provider === 'google_places' ? 'Google Places' : 'Curated Regional Hubs (Demo)'}
                </span>
              )}
            </div>

            {isSearching ? (
              /* Loading State */
              <div className="py-12 text-center space-y-3">
                <RefreshCw className="w-8 h-8 animate-spin text-emerald-600 mx-auto" />
                <p className="text-xs font-semibold text-slate-500">
                  Scanning for verified {selectedWasteType} recycling facilities within {selectedRadius} km...
                </p>
              </div>
            ) : searchResponse && searchResponse.results.length > 0 ? (
              /* Results Cards */
              <div className="space-y-3">
                {searchResponse.results.map((center: RecyclingCenterItem, idx: number) => (
                  <div
                    key={center.id}
                    className={`rounded-2xl p-4 sm:p-5 border transition-all ${
                      idx === 0
                        ? 'bg-gradient-to-br from-emerald-50/60 to-white border-emerald-300/80 shadow-sm ring-1 ring-emerald-500/20'
                        : 'bg-white border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2">
                      <div className="space-y-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <h5 className="font-bold text-slate-900 text-sm sm:text-base">
                            {center.name}
                          </h5>
                          {idx === 0 && (
                            <span className="text-[10px] font-extrabold uppercase tracking-wider bg-emerald-600 text-white px-2 py-0.5 rounded-md flex items-center gap-1 shadow-xs">
                              <Sparkles className="w-2.5 h-2.5" /> Nearest Facility
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-slate-600 flex items-start gap-1.5 leading-relaxed">
                          <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5" />
                          <span>{center.address}</span>
                        </p>
                      </div>

                      {/* Distance Badge */}
                      <div className="sm:text-right shrink-0">
                        <div className="inline-block sm:block font-extrabold text-sm text-emerald-700 bg-emerald-100/70 px-2.5 py-1 rounded-lg">
                          Approx. {center.distance_km} km away
                        </div>
                      </div>
                    </div>

                    {/* Metadata & Actions Bar */}
                    <div className="mt-3 pt-3 border-t border-slate-100/80 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-500">
                      <div className="flex flex-wrap items-center gap-3">
                        {center.phone && (
                          <a
                            href={`tel:${center.phone}`}
                            className="flex items-center gap-1 text-slate-600 hover:text-emerald-700 transition"
                          >
                            <Phone className="w-3.5 h-3.5 text-slate-400" />
                            <span>{center.phone}</span>
                          </a>
                        )}
                        {center.opening_hours && (
                          <div className="flex items-center gap-1 text-slate-500">
                            <Clock className="w-3.5 h-3.5 text-slate-400" />
                            <span>{center.opening_hours}</span>
                          </div>
                        )}
                      </div>

                      {/* Navigation & Maps CTAs */}
                      <div className="flex items-center gap-2 w-full sm:w-auto">
                        <a
                          href={center.maps_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex-1 sm:flex-none px-3 py-1.5 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-700 font-bold text-xs transition flex items-center justify-center gap-1.5 shadow-xs"
                        >
                          <Compass className="w-3.5 h-3.5 text-slate-500" />
                          <span>View on Map</span>
                          <ExternalLink className="w-3 h-3 text-slate-400" />
                        </a>
                        <a
                          href={center.directions_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex-1 sm:flex-none px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs transition flex items-center justify-center gap-1.5 shadow-sm shadow-emerald-700/20"
                        >
                          <Navigation className="w-3.5 h-3.5" />
                          <span>Get Directions</span>
                        </a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              /* Empty Results State */
              <div className="py-10 text-center space-y-3 bg-slate-50 rounded-2xl border border-slate-200">
                <AlertCircle className="w-8 h-8 text-amber-500 mx-auto" />
                <div className="max-w-sm mx-auto">
                  <h5 className="font-bold text-slate-800 text-sm">No Facilities Found</h5>
                  <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                    No specialized {selectedWasteType} recycling centers were found within {selectedRadius} km of {locationLabel}.
                  </p>
                  <button
                    onClick={() => {
                      setSelectedRadius(50);
                      executeSearch(selectedWasteType, latitude, longitude, 50);
                    }}
                    className="mt-3 px-4 py-2 bg-emerald-600 text-white rounded-xl text-xs font-bold hover:bg-emerald-500 transition shadow-xs"
                  >
                    Expand Search Radius to 50 km
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Transparency Disclaimer Footer */}
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-3 text-[11px] text-slate-500 leading-relaxed flex items-start gap-2">
            <CheckCircle2 className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
            <span>
              <strong>Note on waste acceptance:</strong> Proximity rankings are calculated from verified geospatial coordinates. Facility acceptance guidelines, operational hours, and commercial fees may vary. We recommend confirming with the center before visiting for hazardous or bulk consignments.
            </span>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-4 border-t border-slate-100 bg-slate-50/70 flex items-center justify-between text-xs text-slate-400">
          <span>EcoClassify DL &bull; Smart Recycling Directory</span>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 font-bold rounded-xl transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default RecyclingCenterModal;
