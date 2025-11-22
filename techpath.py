import React, { useState, useEffect } from 'react';
import { MapPin, Battery, Navigation, Search, Zap, User, Lock, CheckCircle, XCircle, AlertCircle, Filter, Plus, Edit, Trash2, Home, LocateFixed } from 'lucide-react';

const EVChargingAssistant = () => {
  const [activeTab, setActiveTab] = useState('user');
  const [userView, setUserView] = useState('home');
  const [ownerView, setOwnerView] = useState('dashboard');
  const [isAdminLoggedIn, setIsAdminLoggedIn] = useState(false);
  const [adminCredentials, setAdminCredentials] = useState({ email: '', password: '' });
  const [adminView, setAdminView] = useState('approvals');
  
  const [batteryPercent, setBatteryPercent] = useState(80);
  const [batteryCapacity, setBatteryCapacity] = useState(3);
  const [destination, setDestination] = useState('');
  const [distance, setDistance] = useState('');
  const [searchArea, setSearchArea] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [routeResult, setRouteResult] = useState(null);
  const [userLocation, setUserLocation] = useState(null);
  const [locationError, setLocationError] = useState('');
  const [pendingStations, setPendingStations] = useState([]);
  
  const [isOwnerLoggedIn, setIsOwnerLoggedIn] = useState(false);
  const [ownerCredentials, setOwnerCredentials] = useState({ email: '', password: '' });
  const [newStation, setNewStation] = useState({
    name: '',
    address: '',
    area: '',
    type: 'fast',
    power: '',
    connectors: '',
    price: '',
    amenities: '',
    operatingHours: ''
  });

  const [stations, setStations] = useState([
    {
      id: 1,
      name: 'Green Power Charging Hub',
      address: 'MG Road, Near City Mall',
      area: 'Central',
      type: 'fast',
      power: '50kW',
      connectors: 'Type 2, CCS',
      price: '₹15/kWh',
      amenities: 'Cafe, Restroom, WiFi',
      operatingHours: '24/7',
      verified: true,
      ownerId: 1,
      lat: 23.0225,
      lng: 72.5714
    },
    {
      id: 2,
      name: 'Quick Charge Station',
      address: 'SG Highway, Beside Tech Park',
      area: 'West',
      type: 'standard',
      power: '22kW',
      connectors: 'Type 2',
      price: '₹12/kWh',
      amenities: 'Parking, Security',
      operatingHours: '6 AM - 10 PM',
      verified: true,
      ownerId: 1,
      lat: 23.0680,
      lng: 72.5300
    },
    {
      id: 3,
      name: 'EcoCharge Point',
      address: 'Vastrapur Lake Road',
      area: 'West',
      type: 'fast',
      power: '60kW',
      connectors: 'Type 2, CCS, CHAdeMO',
      price: '₹18/kWh',
      amenities: 'Shopping, Food Court',
      operatingHours: '24/7',
      verified: true,
      ownerId: 2,
      lat: 23.0300,
      lng: 72.5160
    },
    {
      id: 4,
      name: 'Smart EV Hub',
      address: 'Satellite Road, IT Park',
      area: 'Satellite',
      type: 'ultra-fast',
      power: '150kW',
      connectors: 'Type 2, CCS',
      price: '₹20/kWh',
      amenities: 'Lounge, WiFi, Cafe',
      operatingHours: '24/7',
      verified: true,
      ownerId: 2,
      lat: 23.0120,
      lng: 72.5230
    }
  ]);

  const calculateRange = () => {
    const range = (batteryPercent / 100) * batteryCapacity * 80;
    return range.toFixed(1);
  };

  useEffect(() => {
    if (window.location && window.location.pathname === '/admin') {
      setActiveTab('admin');
    }
  }, []);

  const checkRoute = () => {
    const range = parseFloat(calculateRange());
    const dist = parseFloat(distance);
    
    if (dist <= range) {
      setRouteResult({
        status: 'reachable',
        message: `Your destination is reachable! You have ${range} km range and need ${dist} km.`,
        remaining: (range - dist).toFixed(1)
      });
    } else {
      const nearestStation = findNearestStation();
      setRouteResult({
        status: 'charging-required',
        message: `Charging required. You need ${dist} km but have ${range} km range.`,
        deficit: (dist - range).toFixed(1),
        nearestStation: nearestStation
      });
    }
  };

  const requestUserLocation = () => {
    setLocationError('');
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setUserLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude });
        },
        () => {
          setLocationError('Location access denied');
        },
        { enableHighAccuracy: true, timeout: 10000 }
      );
    } else {
      setLocationError('Geolocation not supported');
    }
  };

  const haversineDistance = (a, b) => {
    const toRad = (v) => (v * Math.PI) / 180;
    const R = 6371;
    const dLat = toRad(b.lat - a.lat);
    const dLng = toRad(b.lng - a.lng);
    const lat1 = toRad(a.lat);
    const lat2 = toRad(b.lat);
    const h =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1) * Math.cos(lat2) *
      Math.sin(dLng / 2) * Math.sin(dLng / 2);
    const c = 2 * Math.atan2(Math.sqrt(h), Math.sqrt(1 - h));
    return R * c;
  };

  const findNearestStation = () => {
    const available = stations.filter((s) => s.verified && s.lat && s.lng);
    if (!userLocation || available.length === 0) {
      return stations[Math.floor(Math.random() * stations.length)];
    }
    let nearest = available[0];
    let best = haversineDistance(userLocation, { lat: nearest.lat, lng: nearest.lng });
    for (let i = 1; i < available.length; i++) {
      const d = haversineDistance(userLocation, { lat: available[i].lat, lng: available[i].lng });
      if (d < best) {
        best = d;
        nearest = available[i];
      }
    }
    return { ...nearest, distanceKm: best.toFixed(1) };
  };

  const openDirections = (station) => {
    const url = station.lat && station.lng
      ? `https://www.google.com/maps/dir/?api=1&destination=${station.lat},${station.lng}`
      : `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(station.address)}`;
    window.open(url, '_blank');
  };

  const getFilteredStations = () => {
    let filtered = stations;
    
    if (searchArea) {
      filtered = filtered.filter(s => 
        s.area.toLowerCase().includes(searchArea.toLowerCase()) ||
        s.address.toLowerCase().includes(searchArea.toLowerCase()) ||
        s.name.toLowerCase().includes(searchArea.toLowerCase())
      );
    }
    
    if (filterType !== 'all') {
      filtered = filtered.filter(s => s.type === filterType);
    }
    filtered = filtered.filter(s => s.verified);
    
    return filtered;
  };

  const handleOwnerLogin = () => {
    if (ownerCredentials.email === 'owner@ev.com' && ownerCredentials.password === 'owner123') {
      setIsOwnerLoggedIn(true);
      setOwnerView('dashboard');
    } else {
      alert('Invalid credentials. Use: owner@ev.com / owner123');
    }
  };

  const handleAdminLogin = () => {
    if (adminCredentials.email === 'admin@ev.com' && adminCredentials.password === 'admin123') {
      setIsAdminLoggedIn(true);
      setAdminView('approvals');
    } else {
      alert('Invalid credentials. Use: admin@ev.com / admin123');
    }
  };

  const handleAddStation = () => {
    const station = {
      ...newStation,
      id: stations.length + pendingStations.length + 1,
      verified: false,
      ownerId: 1
    };
    setPendingStations([...pendingStations, station]);
    setNewStation({
      name: '', address: '', area: '',
      type: 'fast', power: '', connectors: '', price: '', amenities: '', operatingHours: ''
    });
    setOwnerView('dashboard');
    alert('Station submitted for admin approval');
  };

  const handleDeleteStation = (id) => {
    if (window.confirm('Are you sure you want to delete this station?')) {
      setStations(stations.filter(s => s.id !== id));
    }
  };

  const approveStation = (id) => {
    const st = pendingStations.find((s) => s.id === id);
    if (!st) return;
    const approved = { ...st, verified: true };
    setPendingStations(pendingStations.filter((s) => s.id !== id));
    setStations([...stations, approved]);
  };

  const rejectStation = (id) => {
    setPendingStations(pendingStations.filter((s) => s.id !== id));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50">
      <header className="bg-white shadow-lg border-b-4 border-emerald-500">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-br from-emerald-500 to-teal-600 p-3 rounded-xl">
                <Zap className="text-white" size={32} />
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
                  EV Charging Assistant
                </h1>
                <p className="text-gray-600 text-sm">Smart Route Planning & Verified Stations</p>
              </div>
            </div>
          <div className="flex gap-3">
            <button
              onClick={() => setActiveTab('user')}
                className={`px-6 py-3 rounded-xl font-semibold transition-all ${
                  activeTab === 'user'
                    ? 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white shadow-lg'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <Home className="inline mr-2" size={20} />
                User Portal
            </button>
            <button
              onClick={() => setActiveTab('owner')}
                className={`px-6 py-3 rounded-xl font-semibold transition-all ${
                  activeTab === 'owner'
                    ? 'bg-gradient-to-r from-purple-500 to-pink-600 text-white shadow-lg'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
            >
              <User className="inline mr-2" size={20} />
              Owner Portal
            </button>
            <button
              onClick={() => setActiveTab('admin')}
              className={`px-6 py-3 rounded-xl font-semibold transition-all ${
                activeTab === 'admin'
                  ? 'bg-gradient-to-r from-red-500 to-orange-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <Lock className="inline mr-2" size={20} />
              Admin Panel
            </button>
          </div>
          </div>
        </div>
      </header>

      {activeTab === 'user' && (
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="flex gap-4 mb-8">
            <button
              onClick={() => setUserView('home')}
              className={`flex-1 py-4 px-6 rounded-xl font-semibold transition-all ${
                userView === 'home'
                  ? 'bg-white shadow-xl border-2 border-emerald-500 text-emerald-600'
                  : 'bg-white shadow hover:shadow-lg'
              }`}
            >
              <Battery className="inline mr-2" size={20} />
              Range Calculator
            </button>
            <button
              onClick={() => setUserView('stations')}
              className={`flex-1 py-4 px-6 rounded-xl font-semibold transition-all ${
                userView === 'stations'
                  ? 'bg-white shadow-xl border-2 border-emerald-500 text-emerald-600'
                  : 'bg-white shadow hover:shadow-lg'
              }`}
            >
              <MapPin className="inline mr-2" size={20} />
              Find Stations
            </button>
          </div>

          {userView === 'home' && (
            <div className="grid md:grid-cols-2 gap-8">
              <div className="bg-white rounded-2xl shadow-xl p-8 border-t-4 border-emerald-500">
                <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                  <Battery className="mr-3 text-emerald-600" size={28} />
                  Battery Range Calculator
                </h2>
                
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Battery Percentage: {batteryPercent}%
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={batteryPercent}
                      onChange={(e) => setBatteryPercent(e.target.value)}
                      className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-emerald-600"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Battery Capacity (kWh)
                    </label>
                    <input
                      type="number"
                      value={batteryCapacity}
                      onChange={(e) => setBatteryCapacity(e.target.value)}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-emerald-500 focus:outline-none"
                      placeholder="e.g., 3"
                    />
                  </div>

                  <div className="bg-gradient-to-r from-emerald-500 to-teal-600 rounded-xl p-6 text-white">
                    <p className="text-sm font-medium mb-2">Estimated Range</p>
                    <p className="text-4xl font-bold">{calculateRange()} km</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-2xl shadow-xl p-8 border-t-4 border-teal-500">
                <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                  <Navigation className="mr-3 text-teal-600" size={28} />
                  Route Feasibility Check
                </h2>

                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Destination
                    </label>
                    <input
                      type="text"
                      value={destination}
                      onChange={(e) => setDestination(e.target.value)}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-teal-500 focus:outline-none"
                      placeholder="Enter destination"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Distance (km)
                    </label>
                    <input
                      type="number"
                      value={distance}
                      onChange={(e) => setDistance(e.target.value)}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-teal-500 focus:outline-none"
                      placeholder="e.g., 45"
                    />
                  </div>

                  <button
                    onClick={checkRoute}
                    className="w-full bg-gradient-to-r from-teal-500 to-cyan-600 text-white py-4 rounded-xl font-semibold hover:shadow-lg transition-all"
                  >
                    Check Route
                  </button>

                  {routeResult && (
                    <div className={`rounded-xl p-6 ${
                      routeResult.status === 'reachable'
                        ? 'bg-green-50 border-2 border-green-500'
                        : 'bg-orange-50 border-2 border-orange-500'
                    }`}>
                      <div className="flex items-center mb-3">
                        {routeResult.status === 'reachable' ? (
                          <CheckCircle className="text-green-600 mr-2" size={24} />
                        ) : (
                          <AlertCircle className="text-orange-600 mr-2" size={24} />
                        )}
                        <h3 className="font-bold text-lg">
                          {routeResult.status === 'reachable' ? 'Route Reachable!' : 'Charging Required'}
                        </h3>
                      </div>
                      <p className="text-gray-700 mb-2">{routeResult.message}</p>
                      {routeResult.status === 'reachable' && (
                        <p className="text-sm text-green-700 font-semibold">
                          Remaining range: {routeResult.remaining} km
                        </p>
                      )}
                      {routeResult.nearestStation && (
                        <div className="mt-4 p-4 bg-white rounded-lg">
                          <p className="font-semibold text-gray-800 mb-2">Nearest Charging Station:</p>
                          <p className="text-teal-600 font-bold">{routeResult.nearestStation.name}</p>
                          <p className="text-sm text-gray-600">{routeResult.nearestStation.address}</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

      {userView === 'stations' && (
        <div>
          <div className="bg-white rounded-2xl shadow-xl p-6 mb-8">
            <div className="grid md:grid-cols-2 gap-4">
              <div className="relative">
                <Search className="absolute left-4 top-4 text-gray-400" size={20} />
                <input
                  type="text"
                  value={searchArea}
                  onChange={(e) => setSearchArea(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:border-emerald-500 focus:outline-none"
                  placeholder="Search by area, address, or station name..."
                />
              </div>
              <div className="relative">
                <Filter className="absolute left-4 top-4 text-gray-400" size={20} />
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:border-emerald-500 focus:outline-none appearance-none"
                >
                  <option value="all">All Charger Types</option>
                  <option value="standard">Standard (22kW)</option>
                  <option value="fast">Fast (50-60kW)</option>
                  <option value="ultra-fast">Ultra Fast (150kW+)</option>
                </select>
              </div>
            </div>
            <div className="mt-4 flex items-center gap-3">
              <button onClick={requestUserLocation} className="px-4 py-2 rounded-xl bg-emerald-600 text-white font-semibold">
                <LocateFixed className="inline mr-2" size={16} /> Use my location
              </button>
              {locationError && (
                <span className="text-sm text-red-600">{locationError}</span>
              )}
            </div>
            {userLocation && (
              <div className="mt-4 p-4 border rounded-xl bg-emerald-50">
                <p className="font-semibold text-gray-800 mb-1">Nearest station to you</p>
                {(() => {
                  const ns = findNearestStation();
                  return (
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-emerald-700 font-bold">{ns.name}</p>
                        <p className="text-sm text-gray-600">{ns.address} • {ns.distanceKm} km</p>
                      </div>
                      <button onClick={() => openDirections(ns)} className="px-3 py-2 rounded-lg bg-emerald-600 text-white">
                        Navigate
                      </button>
                    </div>
                  );
                })()}
              </div>
            )}
          </div>

              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {getFilteredStations().map((station) => (
                  <div key={station.id} className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all border-t-4 border-emerald-500 overflow-hidden">
                    <div className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <h3 className="text-xl font-bold text-gray-800 mb-1">{station.name}</h3>
                          <div className={`flex items-center text-sm font-semibold ${station.verified ? 'text-green-600' : 'text-orange-600'}`}>
                            {station.verified ? (
                              <CheckCircle size={16} className="mr-1" />
                            ) : (
                              <AlertCircle size={16} className="mr-1" />
                            )}
                            {station.verified ? 'Verified Station' : 'Pending Approval'}
                          </div>
                        </div>
                        <div className={`px-3 py-1 rounded-full text-xs font-bold ${
                          station.type === 'ultra-fast' ? 'bg-purple-100 text-purple-700' :
                          station.type === 'fast' ? 'bg-blue-100 text-blue-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {station.power}
                        </div>
                      </div>

                      <div className="space-y-3 text-sm">
                        <div className="flex items-start">
                          <MapPin className="text-gray-400 mr-2 flex-shrink-0 mt-1" size={16} />
                          <div>
                            <p className="text-gray-700">{station.address}</p>
                            <p className="text-emerald-600 font-semibold">{station.area}</p>
                          </div>
                        </div>

                        <div className="flex items-center text-gray-600">
                          <Zap className="text-yellow-500 mr-2" size={16} />
                          {station.connectors}
                        </div>

                        <div className="flex justify-between items-center pt-3 border-t">
                          <span className="text-gray-600">Price:</span>
                          <span className="text-emerald-600 font-bold">{station.price}</span>
                        </div>

                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">Hours:</span>
                          <span className="text-gray-800 font-semibold">{station.operatingHours}</span>
                        </div>

                        {station.amenities && (
                          <div className="pt-3 border-t">
                            <p className="text-xs text-gray-500 mb-1">Amenities:</p>
                            <p className="text-sm text-gray-700">{station.amenities}</p>
                          </div>
                        )}
                      </div>

                      <button onClick={() => openDirections(station)} className="w-full mt-4 bg-gradient-to-r from-emerald-500 to-teal-600 text-white py-3 rounded-xl font-semibold hover:shadow-lg transition-all">
                        <Navigation className="inline mr-2" size={16} />
                        Get Directions
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {getFilteredStations().length === 0 && (
                <div className="text-center py-12">
                  <MapPin className="mx-auto text-gray-300 mb-4" size={64} />
                  <p className="text-xl text-gray-500">No charging stations found in this area.</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {activeTab === 'owner' && (
        <div className="max-w-7xl mx-auto px-4 py-8">
          {!isOwnerLoggedIn ? (
            <div className="max-w-md mx-auto">
              <div className="bg-white rounded-2xl shadow-2xl p-8 border-t-4 border-purple-500">
                <div className="text-center mb-8">
                  <div className="bg-gradient-to-br from-purple-500 to-pink-600 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Lock className="text-white" size={40} />
                  </div>
                  <h2 className="text-3xl font-bold text-gray-800">Owner Login</h2>
                  <p className="text-gray-600 mt-2">Manage your charging stations</p>
                </div>

                <div className="space-y-4">
                  <input
                    type="email"
                    value={ownerCredentials.email}
                    onChange={(e) => setOwnerCredentials({...ownerCredentials, email: e.target.value})}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none"
                    placeholder="Email"
                  />
                  <input
                    type="password"
                    value={ownerCredentials.password}
                    onChange={(e) => setOwnerCredentials({...ownerCredentials, password: e.target.value})}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none"
                    placeholder="Password"
                  />
                  <button
                    onClick={handleOwnerLogin}
                    className="w-full bg-gradient-to-r from-purple-500 to-pink-600 text-white py-4 rounded-xl font-semibold hover:shadow-lg transition-all"
                  >
                    Login
                  </button>
                  <p className="text-sm text-center text-gray-500 mt-4">
                    Demo: owner@ev.com / owner123
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <>
              <div className="flex gap-4 mb-8">
                <button
                  onClick={() => setOwnerView('dashboard')}
                  className={`flex-1 py-4 px-6 rounded-xl font-semibold transition-all ${
                    ownerView === 'dashboard'
                      ? 'bg-white shadow-xl border-2 border-purple-500 text-purple-600'
                      : 'bg-white shadow hover:shadow-lg'
                  }`}
                >
                  My Stations
                </button>
                <button
                  onClick={() => setOwnerView('add')}
                  className={`flex-1 py-4 px-6 rounded-xl font-semibold transition-all ${
                    ownerView === 'add'
                      ? 'bg-white shadow-xl border-2 border-purple-500 text-purple-600'
                      : 'bg-white shadow hover:shadow-lg'
                  }`}
                >
                  <Plus className="inline mr-2" size={20} />
                  Add New Station
                </button>
              </div>

              {ownerView === 'dashboard' && (
                <div className="grid md:grid-cols-2 gap-6">
                  {stations.filter(s => s.ownerId === 1).map((station) => (
                    <div key={station.id} className="bg-white rounded-2xl shadow-lg p-6 border-t-4 border-purple-500">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="text-xl font-bold text-gray-800">{station.name}</h3>
                          <p className="text-gray-600 text-sm">{station.address}</p>
                        </div>
                        <div className="flex gap-2">
                          <button className="p-2 bg-blue-100 text-blue-600 rounded-lg hover:bg-blue-200">
                            <Edit size={18} />
                          </button>
                          <button
                            onClick={() => handleDeleteStation(station.id)}
                            className="p-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200"
                          >
                            <Trash2 size={18} />
                          </button>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-gray-500">Type</p>
                          <p className="font-semibold text-gray-800">{station.power}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Price</p>
                          <p className="font-semibold text-gray-800">{station.price}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Hours</p>
                          <p className="font-semibold text-gray-800">{station.operatingHours}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Status</p>
                          {station.verified ? (
                            <p className="text-green-600 font-semibold flex items-center">
                              <CheckCircle size={14} className="mr-1" /> Verified
                            </p>
                          ) : (
                            <p className="text-orange-600 font-semibold flex items-center">
                              <AlertCircle size={14} className="mr-1" /> Pending Approval
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                  {pendingStations.filter(s => s.ownerId === 1).length > 0 && (
                    <div className="md:col-span-2">
                      <h3 className="text-lg font-bold text-gray-800 mb-3">Pending Approval</h3>
                      {pendingStations.filter(s => s.ownerId === 1).map((station) => (
                        <div key={station.id} className="bg-white rounded-2xl shadow p-4 mb-3 border-l-4 border-orange-500">
                          <div className="flex justify-between items-center">
                            <div>
                              <p className="font-semibold text-gray-800">{station.name}</p>
                              <p className="text-sm text-gray-600">{station.address}</p>
                            </div>
                            <span className="text-orange-600 font-semibold">Waiting for admin</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {ownerView === 'add' && (
                <div className="bg-white rounded-2xl shadow-xl p-8 max-w-4xl mx-auto">
                  <h2 className="text-2xl font-bold text-gray-800 mb-6">Add New Charging Station</h2>
                  <div className="grid md:grid-cols-2 gap-6">
                    <input
                      type="text"
                      value={newStation.name}
                      onChange={(e) => setNewStation({...newStation, name: e.target.value})}
                      className="px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none"
                      placeholder="Station Name"
                    />
                    <input
                      type="text"
                      value={newStation.address}
                      onChange={(e) => setNewStation({...newStation, address: e.target.value})}
                      className="px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none"
                      placeholder="Address"
                    />
                    <input
                      type="text"
                      value={newStation.area}
                      onChange={(e) => setNewStation({...newStation, area: e.target.value})}
                      className="px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none"
                      placeholder="Area"
                    />
                    <select
                      value={newStation.type}
                      onChange={(e) => setNewStation({...newStation, type: e.target.value})}
                      className="px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none"
                    >
                      <option value="standard">Standard (22kW)</option>
                      <option value="fast">Fast (50-60kW)</option>
                      <option value="ultra-fast">Ultra Fast (150kW+)</option>
                    </select>
                    <input
                      type="text"
                      value={newStation.power}
                      onChange={(e) => setNewStation({...newStation, power: e.target.value})}
                      className="px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none"
                      placeholder="Power (e.g., 50kW)"
                    />
                    <input
                      type="text"
                      value={newStation.connectors}
                      onChange={(e) => setNewStation({...newStation, connectors: e.target.value})}
                      className="px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none"
                      placeholder="Connectors (e.g., Type 2, CCS)"
                    />
                    <input
                      type="text"
                      value={newStation.price}
                      onChange={(e) => setNewStation({...newStation, price: e.target.value})}
                      className="px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none"
                      placeholder="Price (e.g., ₹15/kWh)"
                    />
                    <input
                      type="text"
                      value={newStation.operatingHours}
                      onChange={(e) => setNewStation({...newStation, operatingHours: e.target.value})}
                      className="px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none"
                      placeholder="Operating Hours (e.g., 24/7)"
                    />
                    <input
                      type="text"
                      value={newStation.amenities}
                      onChange={(e) => setNewStation({...newStation, amenities: e.target.value})}
                      className="md:col-span-2 px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none"
                      placeholder="Amenities (e.g., Cafe, WiFi, Restroom)"
                    />
                  </div>
                  <button
                    onClick={handleAddStation}
                    className="w-full mt-6 bg-gradient-to-r from-purple-500 to-pink-600 text-white py-4 rounded-xl font-semibold hover:shadow-lg transition-all"
                  >
                    <Plus className="inline mr-2" size={20} />
                    Add Station
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {activeTab === 'admin' && (
        <div className="max-w-7xl mx-auto px-4 py-8">
          {!isAdminLoggedIn ? (
            <div className="max-w-md mx-auto">
              <div className="bg-white rounded-2xl shadow-2xl p-8 border-t-4 border-red-500">
                <div className="text-center mb-8">
                  <div className="bg-gradient-to-br from-red-500 to-orange-600 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Lock className="text-white" size={40} />
                  </div>
                  <h2 className="text-3xl font-bold text-gray-800">Admin Login</h2>
                  <p className="text-gray-600 mt-2">Approve submitted stations</p>
                </div>
                <div className="space-y-4">
                  <input
                    type="email"
                    value={adminCredentials.email}
                    onChange={(e) => setAdminCredentials({ ...adminCredentials, email: e.target.value })}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-red-500 focus:outline-none"
                    placeholder="Email"
                  />
                  <input
                    type="password"
                    value={adminCredentials.password}
                    onChange={(e) => setAdminCredentials({ ...adminCredentials, password: e.target.value })}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-red-500 focus:outline-none"
                    placeholder="Password"
                  />
                  <button onClick={handleAdminLogin} className="w-full bg-gradient-to-r from-red-500 to-orange-600 text-white py-4 rounded-xl font-semibold hover:shadow-lg transition-all">
                    Login
                  </button>
                  <p className="text-sm text-center text-gray-500 mt-4">Demo: admin@ev.com / admin123</p>
                </div>
              </div>
            </div>
          ) : (
            <>
              <div className="flex gap-4 mb-8">
                <button
                  onClick={() => setAdminView('approvals')}
                  className={`flex-1 py-4 px-6 rounded-xl font-semibold transition-all ${
                    adminView === 'approvals'
                      ? 'bg-white shadow-xl border-2 border-red-500 text-red-600'
                      : 'bg-white shadow hover:shadow-lg'
                  }`}
                >
                  Pending Approvals
                </button>
                <button
                  onClick={() => setAdminView('stations')}
                  className={`flex-1 py-4 px-6 rounded-xl font-semibold transition-all ${
                    adminView === 'stations'
                      ? 'bg-white shadow-xl border-2 border-red-500 text-red-600'
                      : 'bg-white shadow hover:shadow-lg'
                  }`}
                >
                  All Stations
                </button>
              </div>
              {adminView === 'approvals' && (
                <div className="grid md:grid-cols-2 gap-6">
                  {pendingStations.length === 0 && (
                    <p className="text-gray-600">No submissions awaiting approval.</p>
                  )}
                  {pendingStations.map((station) => (
                    <div key={station.id} className="bg-white rounded-2xl shadow-lg p-6 border-t-4 border-red-500">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="text-xl font-bold text-gray-800">{station.name}</h3>
                          <p className="text-gray-600 text-sm">{station.address}</p>
                        </div>
                        <div className="flex gap-2">
                          <button onClick={() => approveStation(station.id)} className="p-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200">
                            <CheckCircle size={18} />
                          </button>
                          <button onClick={() => rejectStation(station.id)} className="p-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200">
                            <XCircle size={18} />
                          </button>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-gray-500">Type</p>
                          <p className="font-semibold text-gray-800">{station.type}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Price</p>
                          <p className="font-semibold text-gray-800">{station.price}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Hours</p>
                          <p className="font-semibold text-gray-800">{station.operatingHours}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Connectors</p>
                          <p className="font-semibold text-gray-800">{station.connectors}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {adminView === 'stations' && (
                <div className="grid md:grid-cols-2 gap-6">
                  {stations.map((station) => (
                    <div key={station.id} className="bg-white rounded-2xl shadow-lg p-6 border-t-4 border-red-500">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="text-xl font-bold text-gray-800">{station.name}</h3>
                          <p className="text-gray-600 text-sm">{station.address}</p>
                        </div>
                        <div className="px-3 py-1 rounded-full text-xs font-bold bg-gray-100 text-gray-700">
                          {station.type}
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-gray-500">Status</p>
                          {station.verified ? (
                            <p className="text-green-600 font-semibold flex items-center">
                              <CheckCircle size={14} className="mr-1" /> Verified
                            </p>
                          ) : (
                            <p className="text-orange-600 font-semibold flex items-center">
                              <AlertCircle size={14} className="mr-1" /> Pending Approval
                            </p>
                          )}
                        </div>
                        <div>
                          <p className="text-gray-500">Power</p>
                          <p className="font-semibold text-gray-800">{station.power}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default EVChargingAssistant;