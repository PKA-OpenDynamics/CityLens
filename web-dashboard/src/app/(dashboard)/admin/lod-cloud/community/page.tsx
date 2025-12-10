'use client';

import React, { useState } from 'react';
import {
  Database,
  Upload,
  Download,
  Users,
  GitBranch,
  Star,
  Globe,
  CheckCircle2,
  TrendingUp,
  Award,
  FileText,
  Code,
  ExternalLink,
  Search,
  Filter,
  Eye,
  Heart,
  Share2,
  BookOpen,
  Zap,
  Shield,
} from 'lucide-react';
import Link from 'next/link';

// =============================================================================
// TYPES
// =============================================================================

interface Dataset {
  id: string;
  name: string;
  description: string;
  namespace: string;
  triples: number;
  contributor: string;
  contributorAvatar?: string;
  license: string;
  status: 'approved' | 'pending' | 'review';
  downloads: number;
  stars: number;
  lastUpdated: string;
  tags: string[];
  format: string[];
  linkedDatasets: string[];
}

interface Contributor {
  id: string;
  name: string;
  avatar: string;
  organization?: string;
  datasets: number;
  triples: number;
  stars: number;
  joined: string;
  badge: 'gold' | 'silver' | 'bronze' | 'contributor';
}

interface ContributionStats {
  totalDatasets: number;
  totalTriples: number;
  totalContributors: number;
  totalDownloads: number;
  pendingReviews: number;
  thisMonthContributions: number;
}

// =============================================================================
// MOCK DATA
// =============================================================================

const DATASETS: Dataset[] = [
  {
    id: 'citylens-weather',
    name: 'Hanoi Weather Observations',
    description: 'Real-time weather data for Hanoi districts using SOSA/SSN ontology',
    namespace: 'https://citylens.vn/data/weather/',
    triples: 63,
    contributor: 'CityLens Team',
    license: 'CC-BY 4.0',
    status: 'approved',
    downloads: 1250,
    stars: 45,
    lastUpdated: '2025-12-10',
    tags: ['weather', 'hanoi', 'sosa', 'iot'],
    format: ['turtle', 'json-ld', 'rdf-xml'],
    linkedDatasets: ['citylens-places', 'citylens-airquality'],
  },
  {
    id: 'citylens-airquality',
    name: 'Air Quality Index Data',
    description: 'AQI measurements including PM2.5, PM10, CO, NO2 for Vietnamese cities',
    namespace: 'https://citylens.vn/data/aqi/',
    triples: 76,
    contributor: 'CityLens Team',
    license: 'CC-BY 4.0',
    status: 'approved',
    downloads: 980,
    stars: 38,
    lastUpdated: '2025-12-10',
    tags: ['air-quality', 'environment', 'health', 'sosa'],
    format: ['turtle', 'json-ld'],
    linkedDatasets: ['citylens-weather', 'citylens-places'],
  },
  {
    id: 'citylens-traffic',
    name: 'Traffic Flow Observations',
    description: 'Real-time traffic congestion data for major roads in Hanoi',
    namespace: 'https://citylens.vn/data/traffic/',
    triples: 106,
    contributor: 'VN Transport Lab',
    contributorAvatar: '🚗',
    license: 'CC-BY 4.0',
    status: 'approved',
    downloads: 2100,
    stars: 67,
    lastUpdated: '2025-12-09',
    tags: ['traffic', 'transport', 'smart-city', 'ngsi-ld'],
    format: ['turtle', 'json-ld', 'rdf-xml'],
    linkedDatasets: ['citylens-places', 'citylens-parking'],
  },
  {
    id: 'citylens-parking',
    name: 'Parking Spots Database',
    description: 'Parking availability data for shopping centers and street parking',
    namespace: 'https://citylens.vn/data/parking/',
    triples: 99,
    contributor: 'Smart Parking VN',
    contributorAvatar: '🅿️',
    license: 'CC-BY-SA 4.0',
    status: 'approved',
    downloads: 560,
    stars: 23,
    lastUpdated: '2025-12-08',
    tags: ['parking', 'smart-city', 'fiware'],
    format: ['turtle', 'json-ld'],
    linkedDatasets: ['citylens-traffic', 'citylens-places'],
  },
  {
    id: 'citylens-civic',
    name: 'Civic Issue Reports',
    description: 'Urban infrastructure issues reported by citizens',
    namespace: 'https://citylens.vn/data/civic/',
    triples: 108,
    contributor: 'Open Gov VN',
    contributorAvatar: '🏛️',
    license: 'CC0 1.0',
    status: 'approved',
    downloads: 340,
    stars: 19,
    lastUpdated: '2025-12-10',
    tags: ['civic', 'government', 'urban', 'citizen'],
    format: ['turtle', 'json-ld', 'rdf-xml', 'csv'],
    linkedDatasets: ['citylens-places'],
  },
  {
    id: 'citylens-places',
    name: 'Hanoi Administrative Divisions',
    description: 'Districts and wards of Hanoi with Wikidata/DBpedia links',
    namespace: 'https://citylens.vn/place/',
    triples: 111,
    contributor: 'CityLens Team',
    license: 'CC-BY 4.0',
    status: 'approved',
    downloads: 890,
    stars: 52,
    lastUpdated: '2025-12-10',
    tags: ['geography', 'administrative', 'hanoi', 'linked-data'],
    format: ['turtle', 'json-ld'],
    linkedDatasets: ['dbpedia', 'wikidata', 'geonames'],
  },
  {
    id: 'community-hospitals',
    name: 'Vietnam Hospitals',
    description: 'Public hospitals data linked to OpenStreetMap',
    namespace: 'https://citylens.vn/data/hospitals/',
    triples: 0,
    contributor: 'Health Data VN',
    contributorAvatar: '🏥',
    license: 'ODbL',
    status: 'pending',
    downloads: 0,
    stars: 5,
    lastUpdated: '2025-12-09',
    tags: ['health', 'hospitals', 'osm'],
    format: ['turtle'],
    linkedDatasets: ['osm', 'citylens-places'],
  },
];

const CONTRIBUTORS: Contributor[] = [
  {
    id: '1',
    name: 'CityLens Team',
    avatar: '🌆',
    organization: 'PKA OpenDynamics',
    datasets: 4,
    triples: 450,
    stars: 150,
    joined: '2025-01-01',
    badge: 'gold',
  },
  {
    id: '2',
    name: 'VN Transport Lab',
    avatar: '🚗',
    organization: 'Vietnam Transportation Research',
    datasets: 2,
    triples: 210,
    stars: 85,
    joined: '2025-03-15',
    badge: 'silver',
  },
  {
    id: '3',
    name: 'Smart Parking VN',
    avatar: '🅿️',
    datasets: 1,
    triples: 99,
    stars: 23,
    joined: '2025-06-20',
    badge: 'bronze',
  },
  {
    id: '4',
    name: 'Open Gov VN',
    avatar: '🏛️',
    organization: 'Open Government Vietnam',
    datasets: 1,
    triples: 108,
    stars: 19,
    joined: '2025-08-01',
    badge: 'contributor',
  },
  {
    id: '5',
    name: 'Health Data VN',
    avatar: '🏥',
    datasets: 1,
    triples: 0,
    stars: 5,
    joined: '2025-12-01',
    badge: 'contributor',
  },
];

const STATS: ContributionStats = {
  totalDatasets: 7,
  totalTriples: 728,
  totalContributors: 5,
  totalDownloads: 6120,
  pendingReviews: 1,
  thisMonthContributions: 3,
};

// =============================================================================
// COMPONENTS
// =============================================================================

function StatCard({ icon: Icon, label, value, trend, color }: {
  icon: React.ElementType;
  label: string;
  value: string | number;
  trend?: string;
  color: string;
}) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm">
      <div className="flex items-start justify-between">
        <div className={`p-3 rounded-lg ${color}`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
        {trend && (
          <span className="flex items-center text-sm text-green-600 dark:text-green-400">
            <TrendingUp className="h-4 w-4 mr-1" />
            {trend}
          </span>
        )}
      </div>
      <div className="mt-4">
        <p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
        <p className="text-sm text-gray-600 dark:text-gray-400">{label}</p>
      </div>
    </div>
  );
}

function DatasetCard({ dataset, onDownload }: { dataset: Dataset; onDownload: (id: string) => void }) {
  const statusColors = {
    approved: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
    review: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
            <Database className="h-5 w-5 text-blue-600 dark:text-blue-400" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white">{dataset.name}</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">by {dataset.contributor}</p>
          </div>
        </div>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[dataset.status]}`}>
          {dataset.status === 'approved' ? '✓ Verified' : dataset.status === 'pending' ? '⏳ Pending' : '👁 Review'}
        </span>
      </div>

      <p className="text-sm text-gray-600 dark:text-gray-300 mb-4 line-clamp-2">
        {dataset.description}
      </p>

      <div className="flex flex-wrap gap-2 mb-4">
        {dataset.tags.slice(0, 4).map((tag) => (
          <span
            key={tag}
            className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded text-xs"
          >
            #{tag}
          </span>
        ))}
      </div>

      <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400 mb-4">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1">
            <FileText className="h-4 w-4" />
            {dataset.triples.toLocaleString()} triples
          </span>
          <span className="flex items-center gap-1">
            <Download className="h-4 w-4" />
            {dataset.downloads.toLocaleString()}
          </span>
          <span className="flex items-center gap-1">
            <Star className="h-4 w-4 text-yellow-500" />
            {dataset.stars}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-2 pt-4 border-t border-gray-200 dark:border-gray-700">
        <button
          onClick={() => onDownload(dataset.id)}
          className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors"
        >
          <Download className="h-4 w-4" />
          Download
        </button>
        <button className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
          <Eye className="h-4 w-4" />
        </button>
        <button className="p-2 text-gray-500 hover:text-red-500 dark:text-gray-400 dark:hover:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
          <Heart className="h-4 w-4" />
        </button>
        <button className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
          <Share2 className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}

function ContributorCard({ contributor }: { contributor: Contributor }) {
  const badgeColors = {
    gold: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
    silver: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
    bronze: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400',
    contributor: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
  };

  const badgeIcons = {
    gold: '🥇',
    silver: '🥈',
    bronze: '🥉',
    contributor: '⭐',
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-center gap-3">
        <div className="text-3xl">{contributor.avatar}</div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h4 className="font-semibold text-gray-900 dark:text-white truncate">{contributor.name}</h4>
            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${badgeColors[contributor.badge]}`}>
              {badgeIcons[contributor.badge]} {contributor.badge}
            </span>
          </div>
          {contributor.organization && (
            <p className="text-sm text-gray-500 dark:text-gray-400 truncate">{contributor.organization}</p>
          )}
        </div>
      </div>
      <div className="flex items-center gap-4 mt-3 text-sm text-gray-600 dark:text-gray-400">
        <span className="flex items-center gap-1">
          <Database className="h-4 w-4" />
          {contributor.datasets} datasets
        </span>
        <span className="flex items-center gap-1">
          <Star className="h-4 w-4 text-yellow-500" />
          {contributor.stars}
        </span>
      </div>
    </div>
  );
}

// =============================================================================
// MAIN PAGE
// =============================================================================

export default function LODCommunityPage() {
  const [activeTab, setActiveTab] = useState<'datasets' | 'contributors' | 'contribute' | 'api'>('datasets');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFormat, setSelectedFormat] = useState<string>('all');
  const [showContributeModal, setShowContributeModal] = useState(false);

  // Filter datasets
  const filteredDatasets = DATASETS.filter((ds) => {
    const matchesSearch = ds.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ds.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ds.tags.some((t) => t.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesFormat = selectedFormat === 'all' || ds.format.includes(selectedFormat);
    return matchesSearch && matchesFormat;
  });

  const handleDownload = (datasetId: string) => {
    // TODO: Implement actual download
    alert(`Downloading dataset: ${datasetId}\nFormats: Turtle, JSON-LD, RDF/XML`);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 text-white">
        <div className="max-w-7xl mx-auto px-4 py-12">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <Globe className="h-10 w-10" />
                <h1 className="text-3xl font-bold">CityLens LOD Community</h1>
              </div>
              <p className="text-lg text-blue-100 max-w-2xl">
                Nền tảng dữ liệu mở liên kết cho thành phố thông minh. 
                Đóng góp, chia sẻ và sử dụng dữ liệu theo chuẩn Linked Open Data 5-Star.
              </p>
              <div className="flex items-center gap-4 mt-6">
                <button
                  onClick={() => setShowContributeModal(true)}
                  className="flex items-center gap-2 px-6 py-3 bg-white text-blue-600 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
                >
                  <Upload className="h-5 w-5" />
                  Đóng góp Dataset
                </button>
                <Link
                  href="/admin/lod-cloud"
                  className="flex items-center gap-2 px-6 py-3 bg-blue-500/30 text-white rounded-lg font-semibold hover:bg-blue-500/40 transition-colors"
                >
                  <Code className="h-5 w-5" />
                  SPARQL Endpoint
                </Link>
              </div>
            </div>
            <div className="hidden lg:block">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white/10 backdrop-blur rounded-xl p-4 text-center">
                  <div className="text-3xl font-bold">{STATS.totalDatasets}</div>
                  <div className="text-sm text-blue-200">Datasets</div>
                </div>
                <div className="bg-white/10 backdrop-blur rounded-xl p-4 text-center">
                  <div className="text-3xl font-bold">{STATS.totalTriples.toLocaleString()}</div>
                  <div className="text-sm text-blue-200">Triples</div>
                </div>
                <div className="bg-white/10 backdrop-blur rounded-xl p-4 text-center">
                  <div className="text-3xl font-bold">{STATS.totalContributors}</div>
                  <div className="text-sm text-blue-200">Contributors</div>
                </div>
                <div className="bg-white/10 backdrop-blur rounded-xl p-4 text-center">
                  <div className="text-3xl font-bold">{STATS.totalDownloads.toLocaleString()}</div>
                  <div className="text-sm text-blue-200">Downloads</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4">
          <nav className="flex gap-8">
            {[
              { id: 'datasets', label: 'Dataset Catalog', icon: Database },
              { id: 'contributors', label: 'Contributors', icon: Users },
              { id: 'contribute', label: 'How to Contribute', icon: GitBranch },
              { id: 'api', label: 'API & SPARQL', icon: Code },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as typeof activeTab)}
                className={`flex items-center gap-2 py-4 border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-600 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                }`}
              >
                <tab.icon className="h-5 w-5" />
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard icon={Database} label="Total Datasets" value={STATS.totalDatasets} trend="+3 this month" color="bg-blue-600" />
          <StatCard icon={FileText} label="Total Triples" value={STATS.totalTriples.toLocaleString()} trend="+15%" color="bg-purple-600" />
          <StatCard icon={Users} label="Contributors" value={STATS.totalContributors} trend="+2 new" color="bg-green-600" />
          <StatCard icon={Download} label="Total Downloads" value={STATS.totalDownloads.toLocaleString()} trend="+25%" color="bg-orange-600" />
        </div>

        {/* Dataset Catalog Tab */}
        {activeTab === 'datasets' && (
          <div>
            {/* Search & Filter */}
            <div className="flex flex-col md:flex-row gap-4 mb-6">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search datasets by name, description, or tag..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 dark:text-white"
                />
              </div>
              <div className="flex items-center gap-2">
                <Filter className="h-5 w-5 text-gray-400" />
                <select
                  value={selectedFormat}
                  onChange={(e) => setSelectedFormat(e.target.value)}
                  className="px-4 py-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white"
                >
                  <option value="all">All Formats</option>
                  <option value="turtle">Turtle (.ttl)</option>
                  <option value="json-ld">JSON-LD</option>
                  <option value="rdf-xml">RDF/XML</option>
                  <option value="csv">CSV</option>
                </select>
              </div>
            </div>

            {/* Dataset Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredDatasets.map((dataset) => (
                <DatasetCard key={dataset.id} dataset={dataset} onDownload={handleDownload} />
              ))}
            </div>
          </div>
        )}

        {/* Contributors Tab */}
        {activeTab === 'contributors' && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Top Contributors</h2>
              <div className="flex items-center gap-2">
                <Award className="h-5 w-5 text-yellow-500" />
                <span className="text-sm text-gray-600 dark:text-gray-400">Leaderboard</span>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {CONTRIBUTORS.map((contributor) => (
                <ContributorCard key={contributor.id} contributor={contributor} />
              ))}
            </div>

            {/* Contribution Guidelines */}
            <div className="mt-8 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-xl p-6 border border-green-200 dark:border-green-800">
              <h3 className="text-lg font-semibold text-green-800 dark:text-green-300 mb-4 flex items-center gap-2">
                <Award className="h-5 w-5" />
                Badge System
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl mb-1">🥇</div>
                  <div className="font-medium text-gray-900 dark:text-white">Gold</div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">10+ datasets, 1000+ stars</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl mb-1">🥈</div>
                  <div className="font-medium text-gray-900 dark:text-white">Silver</div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">5+ datasets, 500+ stars</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl mb-1">🥉</div>
                  <div className="font-medium text-gray-900 dark:text-white">Bronze</div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">2+ datasets, 100+ stars</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl mb-1">⭐</div>
                  <div className="font-medium text-gray-900 dark:text-white">Contributor</div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">1+ approved dataset</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* How to Contribute Tab */}
        {activeTab === 'contribute' && (
          <div className="space-y-8">
            {/* Contribution Flow */}
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
                <GitBranch className="h-6 w-6 text-blue-600" />
                Quy trình Đóng góp Dataset
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {[
                  { step: 1, title: 'Chuẩn bị', desc: 'Chuẩn hóa dữ liệu theo RDF/Turtle hoặc JSON-LD', icon: FileText, color: 'blue' },
                  { step: 2, title: 'Submit', desc: 'Upload dataset qua form hoặc GitHub PR', icon: Upload, color: 'purple' },
                  { step: 3, title: 'Review', desc: 'Đội ngũ review và validate dữ liệu', icon: Shield, color: 'orange' },
                  { step: 4, title: 'Publish', desc: 'Dataset được publish và index', icon: CheckCircle2, color: 'green' },
                ].map((item) => (
                  <div key={item.step} className="relative">
                    <div className={`bg-${item.color}-100 dark:bg-${item.color}-900/30 rounded-xl p-4`}>
                      <div className={`w-10 h-10 bg-${item.color}-600 text-white rounded-full flex items-center justify-center font-bold mb-3`}>
                        {item.step}
                      </div>
                      <h3 className="font-semibold text-gray-900 dark:text-white mb-1">{item.title}</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{item.desc}</p>
                    </div>
                    {item.step < 4 && (
                      <div className="hidden md:block absolute top-1/2 -right-2 transform -translate-y-1/2 text-gray-400">
                        →
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Data Requirements */}
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
                <BookOpen className="h-6 w-6 text-green-600" />
                Yêu cầu Dữ liệu
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white mb-3">✅ Yêu cầu bắt buộc</h3>
                  <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5" />
                      Định dạng RDF (Turtle, JSON-LD, hoặc RDF/XML)
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5" />
                      Sử dụng ontology chuẩn (SOSA, Schema.org, NGSI-LD...)
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5" />
                      URI dereferenceable cho mỗi entity
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5" />
                      License mở (CC-BY, CC0, ODbL...)
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5" />
                      Metadata đầy đủ (title, description, creator, date)
                    </li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white mb-3">⭐ Khuyến khích</h3>
                  <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                    <li className="flex items-start gap-2">
                      <Star className="h-4 w-4 text-yellow-500 mt-0.5" />
                      Liên kết với external datasets (DBpedia, Wikidata)
                    </li>
                    <li className="flex items-start gap-2">
                      <Star className="h-4 w-4 text-yellow-500 mt-0.5" />
                      Dữ liệu có tọa độ địa lý (GeoSPARQL/WGS84)
                    </li>
                    <li className="flex items-start gap-2">
                      <Star className="h-4 w-4 text-yellow-500 mt-0.5" />
                      Multilingual labels (Vietnamese + English)
                    </li>
                    <li className="flex items-start gap-2">
                      <Star className="h-4 w-4 text-yellow-500 mt-0.5" />
                      VoID description cho dataset
                    </li>
                    <li className="flex items-start gap-2">
                      <Star className="h-4 w-4 text-yellow-500 mt-0.5" />
                      SHACL shapes cho validation
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Template */}
            <div className="bg-gray-900 rounded-xl p-6 overflow-x-auto">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-white font-medium flex items-center gap-2">
                  <Code className="h-5 w-5" />
                  Template Turtle
                </h3>
                <button className="text-blue-400 hover:text-blue-300 text-sm">Copy</button>
              </div>
              <pre className="text-sm text-gray-300 font-mono">
{`@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix sosa: <http://www.w3.org/ns/sosa/> .
@prefix wgs84: <http://www.w3.org/2003/01/geo/wgs84_pos#> .
@prefix citylens: <https://citylens.vn/ontology/> .
@prefix mydata: <https://citylens.vn/data/mycontribution/> .

# Dataset Metadata
mydata:dataset a dcat:Dataset ;
    dct:title "My Contribution Dataset"@en ;
    dct:description "Description of the dataset"@en ;
    dct:creator <https://your-organization.org/> ;
    dct:license <https://creativecommons.org/licenses/by/4.0/> ;
    dct:created "2025-12-10"^^xsd:date .

# Sample Observation
mydata:obs-001 a sosa:Observation ;
    rdfs:label "Observation 001"@en ;
    sosa:resultTime "2025-12-10T10:00:00Z"^^xsd:dateTime ;
    wgs84:lat "21.0278"^^xsd:double ;
    wgs84:long "105.8342"^^xsd:double ;
    citylens:locatedIn <https://citylens.vn/place/Hanoi> .`}
              </pre>
            </div>
          </div>
        )}

        {/* API & SPARQL Tab */}
        {activeTab === 'api' && (
          <div className="space-y-8">
            {/* SPARQL Endpoint */}
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
                <Zap className="h-6 w-6 text-yellow-500" />
                SPARQL Endpoint
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white mb-3">Endpoints</h3>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between p-3 bg-gray-100 dark:bg-gray-700 rounded-lg">
                      <span className="text-sm font-mono text-gray-700 dark:text-gray-300">
                        /citylens/sparql
                      </span>
                      <span className="text-xs bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 px-2 py-1 rounded">
                        Unified
                      </span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-gray-100 dark:bg-gray-700 rounded-lg">
                      <span className="text-sm font-mono text-gray-700 dark:text-gray-300">
                        /citylens-weather/sparql
                      </span>
                      <span className="text-xs bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400 px-2 py-1 rounded">
                        Weather
                      </span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-gray-100 dark:bg-gray-700 rounded-lg">
                      <span className="text-sm font-mono text-gray-700 dark:text-gray-300">
                        /citylens-traffic/sparql
                      </span>
                      <span className="text-xs bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400 px-2 py-1 rounded">
                        Traffic
                      </span>
                    </div>
                  </div>
                </div>
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white mb-3">Base URL</h3>
                  <div className="p-4 bg-gray-100 dark:bg-gray-700 rounded-lg">
                    <code className="text-sm text-gray-700 dark:text-gray-300">
                      http://localhost:7200 (Local)<br />
                      https://fuseki.citylens.vn (Production)
                    </code>
                  </div>
                  <Link
                    href="/admin/lod-cloud"
                    className="mt-4 flex items-center gap-2 text-blue-600 dark:text-blue-400 hover:underline"
                  >
                    <ExternalLink className="h-4 w-4" />
                    Open SPARQL Query Interface
                  </Link>
                </div>
              </div>
            </div>

            {/* REST API */}
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
                <Code className="h-6 w-6 text-blue-600" />
                REST API Endpoints
              </h2>
              
              <div className="space-y-4">
                {[
                  { method: 'GET', path: '/api/v1/lod/datasets', desc: 'List all datasets' },
                  { method: 'GET', path: '/api/v1/lod/datasets/{id}', desc: 'Get dataset details' },
                  { method: 'GET', path: '/api/v1/lod/datasets/{id}/download', desc: 'Download dataset' },
                  { method: 'POST', path: '/api/v1/lod/contributions', desc: 'Submit new dataset' },
                  { method: 'GET', path: '/api/v1/lod/contributors', desc: 'List contributors' },
                  { method: 'GET', path: '/api/v1/lod/stats', desc: 'Get community statistics' },
                ].map((api, idx) => (
                  <div key={idx} className="flex items-center gap-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <span className={`px-2 py-1 rounded text-xs font-mono ${
                      api.method === 'GET' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' :
                      'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
                    }`}>
                      {api.method}
                    </span>
                    <code className="flex-1 text-sm text-gray-700 dark:text-gray-300">{api.path}</code>
                    <span className="text-sm text-gray-500 dark:text-gray-400">{api.desc}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Code Examples */}
            <div className="bg-gray-900 rounded-xl p-6">
              <h3 className="text-white font-medium mb-4 flex items-center gap-2">
                <Code className="h-5 w-5" />
                Example: Query Weather Data
              </h3>
              <pre className="text-sm text-gray-300 font-mono overflow-x-auto">
{`# Python Example
import requests

SPARQL_ENDPOINT = "http://localhost:7200/citylens/sparql"

query = """
PREFIX citylens: <https://citylens.vn/ontology/>
PREFIX sosa: <http://www.w3.org/ns/sosa/>

SELECT ?obs ?temp ?humidity ?time
WHERE {
  ?obs a sosa:Observation .
  ?obs citylens:temperature ?temp .
  OPTIONAL { ?obs citylens:relativeHumidity ?humidity }
  OPTIONAL { ?obs sosa:resultTime ?time }
}
LIMIT 10
"""

response = requests.post(
    SPARQL_ENDPOINT,
    data={'query': query},
    headers={'Accept': 'application/sparql-results+json'}
)

results = response.json()
for binding in results['results']['bindings']:
    print(f"Temp: {binding['temp']['value']}°C")`}
              </pre>
            </div>
          </div>
        )}
      </div>

      {/* Contribute Modal */}
      {showContributeModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                  <Upload className="h-6 w-6 text-blue-600" />
                  Đóng góp Dataset
                </h2>
                <button
                  onClick={() => setShowContributeModal(false)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                >
                  ✕
                </button>
              </div>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Dataset Name *
                </label>
                <input
                  type="text"
                  placeholder="e.g., Hanoi Bus Routes"
                  className="w-full px-4 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Description *
                </label>
                <textarea
                  rows={3}
                  placeholder="Describe your dataset..."
                  className="w-full px-4 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Namespace URI *
                  </label>
                  <input
                    type="text"
                    placeholder="https://citylens.vn/data/..."
                    className="w-full px-4 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    License *
                  </label>
                  <select className="w-full px-4 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white">
                    <option>CC-BY 4.0</option>
                    <option>CC-BY-SA 4.0</option>
                    <option>CC0 1.0</option>
                    <option>ODbL</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Upload RDF File *
                </label>
                <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center">
                  <Upload className="h-10 w-10 text-gray-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Drag & drop your .ttl, .jsonld, or .rdf file here
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                    Or click to browse
                  </p>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Tags
                </label>
                <input
                  type="text"
                  placeholder="transport, hanoi, public-transit (comma separated)"
                  className="w-full px-4 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white"
                />
              </div>
            </div>
            <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
              <button
                onClick={() => setShowContributeModal(false)}
                className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                Cancel
              </button>
              <button className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium flex items-center gap-2">
                <Upload className="h-4 w-4" />
                Submit for Review
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
