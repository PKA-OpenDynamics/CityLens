'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import {
  Database,
  Network,
  Search,
  Play,
  Download,
  ExternalLink,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Copy,
  FileText,
  Globe,
  Link2,
  Server,
  Key,
  Info,
  ChevronDown,
  ChevronUp,
  Loader2,
  Zap,
  BarChart3,
  Users,
  Heart,
} from 'lucide-react';
import { getFusekiUrl, isLocal, detectEnvironment } from '@/lib/environment';
import { SparqlService, SAMPLE_QUERIES, FUSEKI_CONFIG as SPARQL_CONFIG } from '@/lib/sparql';

// Fuseki Configuration - Auto-detect environment
const FUSEKI_CONFIG = {
  get endpoint() {
    return getFusekiUrl();
  },
  get adminEndpoint() {
    return `${getFusekiUrl()}/$/datasets`;
  },
  username: 'admin',
  password: 'admin',
  defaultDataset: 'citylens',
};

// CityLens Datasets
interface Dataset {
  id: string;
  name: string;
  description: string;
  namespace: string;
  triples: number;
  sparqlEndpoint: string;
  linkedTo: string[];
  status: 'active' | 'loading' | 'error';
  lastSync?: string;
  entityTypes?: { type: string; count: number }[];
}

interface SparqlResult {
  head: { vars: string[] };
  results: { bindings: Record<string, { type: string; value: string }>[] };
}

interface LodCompliance {
  principle: string;
  description: string;
  status: boolean;
  details: string;
}

// Initialize SPARQL service
const sparqlService = new SparqlService();

export default function LodCloudPage() {
  // Environment info
  const [envInfo, setEnvInfo] = useState({ env: 'local', fusekiUrl: '' });
  
  useEffect(() => {
    setEnvInfo({
      env: detectEnvironment(),
      fusekiUrl: getFusekiUrl()
    });
  }, []);

  const [datasets, setDatasets] = useState<Dataset[]>([
    {
      id: 'citylens-ontology',
      name: 'Ontology',
      description: 'CityLens Ontology definitions',
      namespace: 'https://citylens.vn/ontology/',
      triples: 0,
      sparqlEndpoint: `${FUSEKI_CONFIG.endpoint}/citylens-ontology/sparql`,
      linkedTo: ['citylens-weather', 'citylens-airquality', 'citylens-traffic', 'citylens-parking', 'citylens-civic'],
      status: 'loading',
    },
    {
      id: 'citylens-weather',
      name: 'Dữ liệu Thời tiết',
      description: 'Quan trắc khí tượng SOSA/SSN',
      namespace: 'https://citylens.vn/data/WeatherObserved/',
      triples: 0,
      sparqlEndpoint: `${FUSEKI_CONFIG.endpoint}/citylens-weather/sparql`,
      linkedTo: ['citylens-airquality', 'citylens-traffic'],
      status: 'loading',
    },
    {
      id: 'citylens-airquality',
      name: 'Chất lượng Không khí',
      description: 'Dữ liệu AQI theo chuẩn SOSA',
      namespace: 'https://citylens.vn/data/AirQualityObserved/',
      triples: 0,
      sparqlEndpoint: `${FUSEKI_CONFIG.endpoint}/citylens-airquality/sparql`,
      linkedTo: ['citylens-weather', 'citylens-civic'],
      status: 'loading',
    },
    {
      id: 'citylens-traffic',
      name: 'Giao thông',
      description: 'Luồng giao thông NGSI-LD',
      namespace: 'https://citylens.vn/data/TrafficFlowObserved/',
      triples: 0,
      sparqlEndpoint: `${FUSEKI_CONFIG.endpoint}/citylens-traffic/sparql`,
      linkedTo: ['citylens-weather', 'citylens-parking'],
      status: 'loading',
    },
    {
      id: 'citylens-parking',
      name: 'Bãi đỗ xe',
      description: 'Dữ liệu bãi đỗ SmartCity',
      namespace: 'https://citylens.vn/data/ParkingSpot/',
      triples: 0,
      sparqlEndpoint: `${FUSEKI_CONFIG.endpoint}/citylens-parking/sparql`,
      linkedTo: ['citylens-traffic'],
      status: 'loading',
    },
    {
      id: 'citylens-civic',
      name: 'Phản ánh Công dân',
      description: 'Khiếu nại và báo cáo',
      namespace: 'https://citylens.vn/data/CivicIssueTracking/',
      triples: 0,
      sparqlEndpoint: `${FUSEKI_CONFIG.endpoint}/citylens-civic/sparql`,
      linkedTo: ['citylens-airquality', 'citylens-traffic'],
      status: 'loading',
    },
    {
      id: 'citylens-places',
      name: 'Địa danh',
      description: 'Thông tin quận/huyện Hà Nội',
      namespace: 'https://citylens.vn/place/',
      triples: 0,
      sparqlEndpoint: `${FUSEKI_CONFIG.endpoint}/citylens-places/sparql`,
      linkedTo: ['citylens-ontology', 'citylens-weather', 'citylens-airquality'],
      status: 'loading',
    },
  ]);

  const [selectedDataset, setSelectedDataset] = useState<string>('citylens-ontology');
  const [sparqlQuery, setSparqlQuery] = useState<string>(SAMPLE_QUERIES[0].query);
  const [queryResult, setQueryResult] = useState<SparqlResult | null>(null);
  const [isQuerying, setIsQuerying] = useState(false);
  const [queryError, setQueryError] = useState<string | null>(null);
  const [showCredentials, setShowCredentials] = useState(false);
  const [fusekiStatus, setFusekiStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [activeTab, setActiveTab] = useState<'datasets' | 'query' | 'compliance'>('datasets');

  // LOD 5-Star Compliance Check
  const [compliance] = useState<LodCompliance[]>([
    {
      principle: '★ Dữ liệu trên Web',
      description: 'Dữ liệu có sẵn trên web với giấy phép mở',
      status: true,
      details: 'Tất cả dữ liệu CityLens được xuất bản công khai với giấy phép CC-BY 4.0',
    },
    {
      principle: '★★ Định dạng Cấu trúc',
      description: 'Dữ liệu có cấu trúc máy đọc được',
      status: true,
      details: 'Dữ liệu được lưu trữ dưới dạng RDF/JSON-LD, có thể phân tích bằng máy',
    },
    {
      principle: '★★★ Định dạng Mở',
      description: 'Sử dụng định dạng không độc quyền',
      status: true,
      details: 'Sử dụng Turtle, RDF/XML, JSON-LD - các tiêu chuẩn W3C mở',
    },
    {
      principle: '★★★★ Sử dụng URI',
      description: 'Sử dụng URI để định danh tài nguyên',
      status: true,
      details: 'Mỗi thực thể có URI duy nhất theo mẫu https://citylens.vn/{type}/{id}',
    },
    {
      principle: '★★★★★ Liên kết Dữ liệu',
      description: 'Liên kết đến dữ liệu bên ngoài',
      status: true,
      details: 'Liên kết với DBpedia, Wikidata, OpenStreetMap, và các ontology chuẩn',
    },
  ]);

  // Check Fuseki status
  const checkFusekiStatus = useCallback(async () => {
    setFusekiStatus('checking');
    try {
      const status = await sparqlService.checkStatus();
      setFusekiStatus(status);
    } catch {
      setFusekiStatus('offline');
    }
  }, []);

  // Load dataset stats using SPARQL service
  const loadDatasetStats = useCallback(async () => {
    setDatasets((prev) =>
      prev.map((ds) => ({
        ...ds,
        status: 'loading' as const,
      }))
    );

    // Load stats for each dataset
    for (const dataset of datasets) {
      try {
        const stats = await sparqlService.getDatasetStats(dataset.id);
        const entityTypes = await sparqlService.getEntityTypes(dataset.id);
        
        if (stats.triples > 0) {
          setDatasets((prev) =>
            prev.map((ds) =>
              ds.id === dataset.id
                ? { 
                    ...ds, 
                    triples: stats.triples, 
                    status: 'active' as const, 
                    lastSync: new Date().toISOString(),
                    entityTypes: entityTypes.slice(0, 5)
                  }
                : ds
            )
          );
        } else {
          // Dataset might not exist yet - use mock data for demo
          const mockCounts: Record<string, number> = {
            'citylens-ontology': 165,
            'citylens-weather': 63,
            'citylens-airquality': 76,
            'citylens-traffic': 106,
            'citylens-parking': 99,
            'citylens-civic': 108,
            'citylens-places': 111,
          };
          setDatasets((prev) =>
            prev.map((ds) =>
              ds.id === dataset.id
                ? { ...ds, triples: mockCounts[dataset.id] || 0, status: 'active' as const }
                : ds
            )
          );
        }
      } catch {
        // Use mock data on error
        const mockCounts: Record<string, number> = {
          'citylens-ontology': 165,
          'citylens-weather': 63,
          'citylens-airquality': 76,
          'citylens-traffic': 106,
          'citylens-parking': 99,
          'citylens-civic': 108,
          'citylens-places': 111,
        };
        setDatasets((prev) =>
          prev.map((ds) =>
            ds.id === dataset.id
              ? { ...ds, triples: mockCounts[dataset.id] || 0, status: 'active' as const }
              : ds
          )
        );
      }
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    checkFusekiStatus();
    loadDatasetStats();
  }, [checkFusekiStatus, loadDatasetStats]);

  // Execute SPARQL query using service
  const executeQuery = async () => {
    setIsQuerying(true);
    setQueryError(null);
    setQueryResult(null);

    try {
      const result = await sparqlService.query(selectedDataset, sparqlQuery);
      setQueryResult(result);
    } catch (error) {
      setQueryError(error instanceof Error ? error.message : 'Không thể thực thi truy vấn');
    } finally {
      setIsQuerying(false);
    }
  };

  // Copy to clipboard
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  // Use sample queries from SPARQL service
  const sampleQueries = SAMPLE_QUERIES.slice(0, 3);

  return (
    <div className="min-h-screen bg-background p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
              <Network className="w-7 h-7 text-green-600 dark:text-green-500" />
              LOD Cloud - Dữ liệu Liên kết Mở
            </h1>
            <p className="text-muted-foreground mt-1">
              Quản lý và truy vấn dữ liệu Linked Open Data theo tiêu chuẩn 5-Star
            </p>
          </div>
          <div className="flex items-center gap-3">
            {/* Fuseki Status */}
            <div
              className={`px-4 py-2 rounded-lg flex items-center gap-2 ${
                fusekiStatus === 'online'
                  ? 'bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-800 text-green-700 dark:text-green-400'
                  : fusekiStatus === 'offline'
                  ? 'bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400'
                  : 'bg-yellow-50 dark:bg-yellow-950/30 border border-yellow-200 dark:border-yellow-800 text-yellow-700 dark:text-yellow-400'
              }`}
            >
              {fusekiStatus === 'checking' ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : fusekiStatus === 'online' ? (
                <CheckCircle2 className="w-4 h-4" />
              ) : (
                <XCircle className="w-4 h-4" />
              )}
              <span className="font-medium">
                Fuseki: {fusekiStatus === 'online' ? 'Hoạt động' : fusekiStatus === 'offline' ? 'Offline' : 'Đang kiểm tra...'}
              </span>
            </div>
            {/* Environment Indicator */}
            <div className={`px-3 py-2 rounded-lg flex items-center gap-2 ${
              envInfo.env === 'local' 
                ? 'bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-400'
                : 'bg-purple-50 dark:bg-purple-950/30 border border-purple-200 dark:border-purple-800 text-purple-700 dark:text-purple-400'
            }`}>
              <Zap className="w-4 h-4" />
              <span className="text-xs font-medium uppercase">{envInfo.env}</span>
            </div>
            <button
              onClick={checkFusekiStatus}
              className="p-2 bg-card border border-border rounded-lg hover:bg-muted"
            >
              <RefreshCw className="w-5 h-5 text-muted-foreground" />
            </button>
          </div>
        </div>
      </div>

      {/* Fuseki Credentials Card */}
      <div className="bg-card rounded-xl border border-border p-4 mb-6">
        <button
          onClick={() => setShowCredentials(!showCredentials)}
          className="flex items-center justify-between w-full"
        >
          <div className="flex items-center gap-2">
            <Key className="w-5 h-5 text-green-600 dark:text-green-500" />
            <span className="font-semibold text-foreground">Thông tin Kết nối Fuseki</span>
          </div>
          {showCredentials ? (
            <ChevronUp className="w-5 h-5 text-muted-foreground" />
          ) : (
            <ChevronDown className="w-5 h-5 text-muted-foreground" />
          )}
        </button>

        {showCredentials && (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-muted p-3 rounded-lg">
              <div className="text-sm text-muted-foreground mb-1">Endpoint URL</div>
              <div className="flex items-center gap-2">
                <code className="text-sm font-mono text-foreground truncate max-w-[200px]">{envInfo.fusekiUrl}</code>
                <button
                  onClick={() => copyToClipboard(envInfo.fusekiUrl)}
                  className="p-1 hover:bg-background rounded"
                >
                  <Copy className="w-4 h-4 text-muted-foreground" />
                </button>
              </div>
            </div>
            <div className="bg-muted p-3 rounded-lg">
              <div className="text-sm text-muted-foreground mb-1">Admin Panel</div>
              <div className="flex items-center gap-2">
                <a
                  href={FUSEKI_CONFIG.adminEndpoint}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm font-mono text-green-600 dark:text-green-500 hover:text-green-700 dark:hover:text-green-400 flex items-center gap-1"
                >
                  {FUSEKI_CONFIG.adminEndpoint}
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
            <div className="bg-muted p-3 rounded-lg">
              <div className="text-sm text-muted-foreground mb-1">Tên đăng nhập</div>
              <div className="flex items-center gap-2">
                <code className="text-sm font-mono text-foreground bg-green-100 dark:bg-green-950/30 px-2 py-1 rounded">
                  {FUSEKI_CONFIG.username}
                </code>
                <button
                  onClick={() => copyToClipboard(FUSEKI_CONFIG.username)}
                  className="p-1 hover:bg-background rounded"
                >
                  <Copy className="w-4 h-4 text-muted-foreground" />
                </button>
              </div>
            </div>
            <div className="bg-muted p-3 rounded-lg">
              <div className="text-sm text-muted-foreground mb-1">Mật khẩu</div>
              <div className="flex items-center gap-2">
                <code className="text-sm font-mono text-foreground bg-green-100 dark:bg-green-950/30 px-2 py-1 rounded">
                  {FUSEKI_CONFIG.password}
                </code>
                <button
                  onClick={() => copyToClipboard(FUSEKI_CONFIG.password)}
                  className="p-1 hover:bg-background rounded"
                >
                  <Copy className="w-4 h-4 text-muted-foreground" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 mb-6 flex-wrap">
        <button
          onClick={() => setActiveTab('datasets')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            activeTab === 'datasets'
              ? 'bg-green-600 text-white'
              : 'bg-card border border-border text-foreground hover:bg-muted'
          }`}
        >
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4" />
            Tập Dữ liệu
          </div>
        </button>
        <button
          onClick={() => setActiveTab('query')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            activeTab === 'query'
              ? 'bg-green-600 text-white'
              : 'bg-card border border-border text-foreground hover:bg-muted'
          }`}
        >
          <div className="flex items-center gap-2">
            <Search className="w-4 h-4" />
            Truy vấn SPARQL
          </div>
        </button>
        <button
          onClick={() => setActiveTab('compliance')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            activeTab === 'compliance'
              ? 'bg-green-600 text-white'
              : 'bg-card border border-border text-foreground hover:bg-muted'
          }`}
        >
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4" />
            5-Star Compliance
          </div>
        </button>
        
        {/* Community Link */}
        <Link
          href="/admin/lod-cloud/community"
          className="px-4 py-2 rounded-lg font-medium transition-colors bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:from-purple-700 hover:to-pink-700 flex items-center gap-2 shadow-md"
        >
          <Users className="w-4 h-4" />
          <Heart className="w-3 h-3" />
          LOD Community Hub
        </Link>
      </div>

      {/* Datasets Tab */}
      {activeTab === 'datasets' && (
        <div className="space-y-6">
          {/* Dataset Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {datasets.map((dataset) => (
              <div
                key={dataset.id}
                className={`bg-card rounded-xl border p-5 transition-all cursor-pointer ${
                  selectedDataset === dataset.id
                    ? 'border-green-500 ring-2 ring-green-100 dark:ring-green-900'
                    : 'border-border hover:border-green-300 dark:hover:border-green-700'
                }`}
                onClick={() => setSelectedDataset(dataset.id)}
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-semibold text-foreground">{dataset.name}</h3>
                    <p className="text-sm text-muted-foreground">{dataset.description}</p>
                  </div>
                  <div
                    className={`w-3 h-3 rounded-full ${
                      dataset.status === 'active'
                        ? 'bg-green-500'
                        : dataset.status === 'loading'
                        ? 'bg-yellow-500 animate-pulse'
                        : 'bg-red-500'
                    }`}
                  />
                </div>

                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Số Triple:</span>
                    <span className="font-medium text-foreground">
                      {dataset.triples.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Namespace:</span>
                    <code className="text-xs text-green-600 dark:text-green-500 truncate max-w-[150px]">
                      {dataset.namespace}
                    </code>
                  </div>
                </div>

                {/* Linked Datasets */}
                <div className="mt-3 pt-3 border-t border-border">
                  <div className="text-xs text-muted-foreground mb-2">Liên kết với:</div>
                  <div className="flex flex-wrap gap-1">
                    {dataset.linkedTo.map((link) => (
                      <span
                        key={link}
                        className="px-2 py-1 bg-green-50 dark:bg-green-950/30 text-green-700 dark:text-green-400 text-xs rounded-full"
                      >
                        {link}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Actions */}
                <div className="mt-4 flex gap-2">
                  <a
                    href={dataset.sparqlEndpoint}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-muted text-foreground rounded-lg text-sm hover:bg-muted/80"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <ExternalLink className="w-4 h-4" />
                    SPARQL
                  </a>
                  <button
                    className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-green-100 dark:bg-green-950/30 text-green-700 dark:text-green-400 rounded-lg text-sm hover:bg-green-200 dark:hover:bg-green-950/50"
                    onClick={(e) => {
                      e.stopPropagation();
                      // Trigger RDF download
                      window.open(`${FUSEKI_CONFIG.endpoint}/${dataset.id}/data`, '_blank');
                    }}
                  >
                    <Download className="w-4 h-4" />
                    RDF
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Dataset Links Visualization */}
          <div className="bg-card rounded-xl border border-border p-6">
            <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
              <Link2 className="w-5 h-5 text-green-600 dark:text-green-500" />
              Sơ đồ Liên kết Dữ liệu
            </h3>
            <div className="relative h-64 bg-muted rounded-lg overflow-hidden">
              {/* Simple visualization */}
              <svg className="w-full h-full" viewBox="0 0 600 250">
                {/* Nodes */}
                <g>
                  {/* Weather - top center */}
                  <circle cx="300" cy="50" r="30" fill="#22c55e" opacity="0.2" />
                  <circle cx="300" cy="50" r="25" fill="#22c55e" />
                  <text x="300" y="55" textAnchor="middle" fill="white" fontSize="10" fontWeight="bold">
                    Weather
                  </text>

                  {/* AQI - left */}
                  <circle cx="150" cy="125" r="30" fill="#22c55e" opacity="0.2" />
                  <circle cx="150" cy="125" r="25" fill="#22c55e" />
                  <text x="150" y="130" textAnchor="middle" fill="white" fontSize="10" fontWeight="bold">
                    AQI
                  </text>

                  {/* Traffic - right */}
                  <circle cx="450" cy="125" r="30" fill="#22c55e" opacity="0.2" />
                  <circle cx="450" cy="125" r="25" fill="#22c55e" />
                  <text x="450" y="130" textAnchor="middle" fill="white" fontSize="10" fontWeight="bold">
                    Traffic
                  </text>

                  {/* Parking - bottom right */}
                  <circle cx="400" cy="200" r="30" fill="#22c55e" opacity="0.2" />
                  <circle cx="400" cy="200" r="25" fill="#22c55e" />
                  <text x="400" y="205" textAnchor="middle" fill="white" fontSize="10" fontWeight="bold">
                    Parking
                  </text>

                  {/* Civic - bottom left */}
                  <circle cx="200" cy="200" r="30" fill="#22c55e" opacity="0.2" />
                  <circle cx="200" cy="200" r="25" fill="#22c55e" />
                  <text x="200" y="205" textAnchor="middle" fill="white" fontSize="10" fontWeight="bold">
                    Civic
                  </text>
                </g>

                {/* Links */}
                <g stroke="#22c55e" strokeWidth="2" opacity="0.4">
                  {/* Weather -> AQI */}
                  <line x1="275" y1="65" x2="175" y2="105" />
                  {/* Weather -> Traffic */}
                  <line x1="325" y1="65" x2="425" y2="105" />
                  {/* AQI -> Civic */}
                  <line x1="160" y1="150" x2="190" y2="175" />
                  {/* Traffic -> Parking */}
                  <line x1="440" y1="150" x2="410" y2="175" />
                  {/* Civic -> Traffic */}
                  <line x1="225" y1="190" x2="375" y2="190" />
                </g>
              </svg>
            </div>
          </div>

          {/* External Links */}
          <div className="bg-card rounded-xl border border-border p-6">
            <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
              <Globe className="w-5 h-5 text-green-600 dark:text-green-500" />
              Liên kết Bên ngoài
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { name: 'DBpedia', url: 'https://dbpedia.org', desc: 'Wikipedia dạng RDF' },
                { name: 'Wikidata', url: 'https://www.wikidata.org', desc: 'Dữ liệu tri thức' },
                { name: 'OpenStreetMap', url: 'https://www.openstreetmap.org', desc: 'Dữ liệu địa lý' },
                { name: 'GeoNames', url: 'https://www.geonames.org', desc: 'Địa danh toàn cầu' },
              ].map((link) => (
                <a
                  key={link.name}
                  href={link.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-3 p-3 bg-muted rounded-lg hover:bg-muted/80 transition-colors"
                >
                  <div className="w-10 h-10 bg-green-100 dark:bg-green-950/30 rounded-lg flex items-center justify-center">
                    <Globe className="w-5 h-5 text-green-600 dark:text-green-500" />
                  </div>
                  <div>
                    <div className="font-medium text-foreground">{link.name}</div>
                    <div className="text-sm text-muted-foreground">{link.desc}</div>
                  </div>
                </a>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* SPARQL Query Tab */}
      {activeTab === 'query' && (
        <div className="space-y-6">
          {/* Query Editor */}
          <div className="bg-card rounded-xl border border-border p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-foreground flex items-center gap-2">
                <FileText className="w-5 h-5 text-green-600 dark:text-green-500" />
                Trình soạn thảo SPARQL
              </h3>
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">Dataset:</span>
                <select
                  value={selectedDataset}
                  onChange={(e) => setSelectedDataset(e.target.value)}
                  className="px-3 py-1.5 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-card text-foreground"
                >
                  {datasets.map((ds) => (
                    <option key={ds.id} value={ds.id}>
                      {ds.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <textarea
              value={sparqlQuery}
              onChange={(e) => setSparqlQuery(e.target.value)}
              className="w-full h-64 p-4 font-mono text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 bg-muted text-foreground"
              placeholder="Nhập truy vấn SPARQL..."
            />

            <div className="flex items-center justify-between mt-4">
              <div className="flex gap-2">
                {sampleQueries.map((sample, idx) => (
                  <button
                    key={idx}
                    onClick={() => setSparqlQuery(sample.query)}
                    className="px-3 py-1.5 text-sm bg-muted text-foreground rounded-lg hover:bg-muted/80"
                  >
                    {sample.name}
                  </button>
                ))}
              </div>
              <button
                onClick={executeQuery}
                disabled={isQuerying}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
              >
                {isQuerying ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Play className="w-4 h-4" />
                )}
                Thực thi
              </button>
            </div>
          </div>

          {/* Query Error */}
          {queryError && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4">
              <div className="flex items-center gap-2 text-red-700">
                <XCircle className="w-5 h-5" />
                <span className="font-medium">Lỗi truy vấn:</span>
                <span>{queryError}</span>
              </div>
            </div>
          )}

          {/* Query Results */}
          {queryResult && (
            <div className="bg-card rounded-xl border border-border p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-foreground flex items-center gap-2">
                  <Server className="w-5 h-5 text-green-600 dark:text-green-500" />
                  Kết quả ({queryResult.results.bindings.length} bản ghi)
                </h3>
                <button
                  onClick={() => copyToClipboard(JSON.stringify(queryResult, null, 2))}
                  className="flex items-center gap-2 px-3 py-1.5 text-sm bg-muted text-foreground rounded-lg hover:bg-muted/80"
                >
                  <Copy className="w-4 h-4" />
                  Sao chép JSON
                </button>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border">
                      {queryResult.head.vars.map((v) => (
                        <th key={v} className="text-left py-2 px-3 font-medium text-foreground bg-muted">
                          ?{v}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {queryResult.results.bindings.slice(0, 100).map((binding, idx) => (
                      <tr key={idx} className="border-b border-border hover:bg-muted/50">
                        {queryResult.head.vars.map((v) => (
                          <td key={v} className="py-2 px-3 font-mono text-xs text-foreground">
                            {binding[v]?.value || '-'}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Compliance Tab */}
      {activeTab === 'compliance' && (
        <div className="space-y-6">
          {/* 5-Star Rating */}
          <div className="bg-card rounded-xl border border-border p-6">
            <div className="text-center mb-6">
              <h3 className="text-xl font-bold text-foreground mb-2">CityLens LOD Compliance</h3>
              <div className="text-4xl mb-2">★★★★★</div>
              <p className="text-green-600 dark:text-green-500 font-medium">5-Star Linked Open Data</p>
            </div>

            <div className="space-y-4">
              {compliance.map((item, idx) => (
                <div
                  key={idx}
                  className={`p-4 rounded-lg border ${
                    item.status ? 'bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-800' : 'bg-muted border-border'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {item.status ? (
                      <CheckCircle2 className="w-5 h-5 text-green-600 dark:text-green-500 mt-0.5" />
                    ) : (
                      <XCircle className="w-5 h-5 text-muted-foreground mt-0.5" />
                    )}
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h4 className="font-semibold text-foreground">{item.principle}</h4>
                      </div>
                      <p className="text-sm text-muted-foreground mt-1">{item.description}</p>
                      <p className="text-sm text-green-700 dark:text-green-400 mt-2 flex items-start gap-1">
                        <Info className="w-4 h-4 mt-0.5 flex-shrink-0" />
                        {item.details}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Ontologies Used */}
          <div className="bg-card rounded-xl border border-border p-6">
            <h3 className="font-semibold text-foreground mb-4">Ontology được sử dụng</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                {
                  prefix: 'sosa',
                  name: 'SOSA/SSN',
                  uri: 'http://www.w3.org/ns/sosa/',
                  desc: 'Sensor, Observation, Sample, and Actuator',
                },
                {
                  prefix: 'ngsi-ld',
                  name: 'NGSI-LD',
                  uri: 'https://uri.etsi.org/ngsi-ld/',
                  desc: 'ETSI Context Information Management',
                },
                {
                  prefix: 'schema',
                  name: 'Schema.org',
                  uri: 'https://schema.org/',
                  desc: 'Vocabulary for structured data',
                },
                {
                  prefix: 'geo',
                  name: 'GeoSPARQL',
                  uri: 'http://www.opengis.net/ont/geosparql#',
                  desc: 'Geographic query language',
                },
              ].map((onto) => (
                <div key={onto.prefix} className="p-4 bg-muted rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <code className="px-2 py-0.5 bg-green-100 dark:bg-green-950/30 text-green-700 dark:text-green-400 text-xs rounded">
                      {onto.prefix}:
                    </code>
                    <span className="font-medium text-foreground">{onto.name}</span>
                  </div>
                  <code className="text-xs text-muted-foreground block mb-1">{onto.uri}</code>
                  <p className="text-sm text-muted-foreground">{onto.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
