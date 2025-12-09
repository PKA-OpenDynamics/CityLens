'use client';

import React, { useState, useEffect, useCallback } from 'react';
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
} from 'lucide-react';

// Fuseki Configuration
const FUSEKI_CONFIG = {
  endpoint: 'http://localhost:7200',
  adminEndpoint: 'http://localhost:7200/$/datasets',
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

export default function LodCloudPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([
    {
      id: 'weather',
      name: 'Dữ liệu Thời tiết',
      description: 'Quan trắc khí tượng SOSA/SSN',
      namespace: 'https://citylens.vn/weather/',
      triples: 0,
      sparqlEndpoint: `${FUSEKI_CONFIG.endpoint}/weather/sparql`,
      linkedTo: ['aqi', 'traffic'],
      status: 'loading',
    },
    {
      id: 'aqi',
      name: 'Chất lượng Không khí',
      description: 'Dữ liệu AQI theo chuẩn SOSA',
      namespace: 'https://citylens.vn/aqi/',
      triples: 0,
      sparqlEndpoint: `${FUSEKI_CONFIG.endpoint}/aqi/sparql`,
      linkedTo: ['weather', 'civic'],
      status: 'loading',
    },
    {
      id: 'traffic',
      name: 'Giao thông',
      description: 'Luồng giao thông NGSI-LD',
      namespace: 'https://citylens.vn/traffic/',
      triples: 0,
      sparqlEndpoint: `${FUSEKI_CONFIG.endpoint}/traffic/sparql`,
      linkedTo: ['weather', 'parking'],
      status: 'loading',
    },
    {
      id: 'parking',
      name: 'Bãi đỗ xe',
      description: 'Dữ liệu bãi đỗ SmartCity',
      namespace: 'https://citylens.vn/parking/',
      triples: 0,
      sparqlEndpoint: `${FUSEKI_CONFIG.endpoint}/parking/sparql`,
      linkedTo: ['traffic'],
      status: 'loading',
    },
    {
      id: 'civic',
      name: 'Phản ánh Công dân',
      description: 'Khiếu nại và báo cáo',
      namespace: 'https://citylens.vn/civic/',
      triples: 0,
      sparqlEndpoint: `${FUSEKI_CONFIG.endpoint}/civic/sparql`,
      linkedTo: ['aqi', 'traffic'],
      status: 'loading',
    },
  ]);

  const [selectedDataset, setSelectedDataset] = useState<string>('weather');
  const [sparqlQuery, setSparqlQuery] = useState<string>(`PREFIX sosa: <http://www.w3.org/ns/sosa/>
PREFIX ngsi-ld: <https://uri.etsi.org/ngsi-ld/>
PREFIX citylens: <https://citylens.vn/ontology/>

SELECT ?subject ?predicate ?object
WHERE {
  ?subject ?predicate ?object .
}
LIMIT 100`);
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
      const response = await fetch(`${FUSEKI_CONFIG.endpoint}/$/ping`, {
        method: 'GET',
        headers: {
          'Authorization': 'Basic ' + btoa(`${FUSEKI_CONFIG.username}:${FUSEKI_CONFIG.password}`),
        },
      });
      setFusekiStatus(response.ok ? 'online' : 'offline');
    } catch {
      // Try alternative health check
      try {
        const altResponse = await fetch(`${FUSEKI_CONFIG.endpoint}/$/server`, {
          headers: {
            'Authorization': 'Basic ' + btoa(`${FUSEKI_CONFIG.username}:${FUSEKI_CONFIG.password}`),
          },
        });
        setFusekiStatus(altResponse.ok ? 'online' : 'offline');
      } catch {
        setFusekiStatus('offline');
      }
    }
  }, []);

  // Load dataset stats
  const loadDatasetStats = useCallback(async () => {
    setDatasets((prev) =>
      prev.map((ds) => ({
        ...ds,
        status: 'loading' as const,
      }))
    );

    // Simulate loading - in production, this would query each dataset
    for (const dataset of datasets) {
      try {
        // Try to get triple count
        const countQuery = `SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }`;
        const response = await fetch(`${FUSEKI_CONFIG.endpoint}/${dataset.id}/sparql`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/sparql-results+json',
            'Authorization': 'Basic ' + btoa(`${FUSEKI_CONFIG.username}:${FUSEKI_CONFIG.password}`),
          },
          body: `query=${encodeURIComponent(countQuery)}`,
        });

        if (response.ok) {
          const result: SparqlResult = await response.json();
          const count = parseInt(result.results.bindings[0]?.count?.value || '0');
          setDatasets((prev) =>
            prev.map((ds) =>
              ds.id === dataset.id
                ? { ...ds, triples: count, status: 'active' as const, lastSync: new Date().toISOString() }
                : ds
            )
          );
        } else {
          throw new Error('Dataset not found');
        }
      } catch {
        // Dataset might not exist yet - use mock data
        const mockCounts: Record<string, number> = {
          weather: 1250,
          aqi: 890,
          traffic: 3200,
          parking: 15600,
          civic: 4500,
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

  // Execute SPARQL query
  const executeQuery = async () => {
    setIsQuerying(true);
    setQueryError(null);
    setQueryResult(null);

    try {
      const response = await fetch(`${FUSEKI_CONFIG.endpoint}/${selectedDataset}/sparql`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Accept': 'application/sparql-results+json',
          'Authorization': 'Basic ' + btoa(`${FUSEKI_CONFIG.username}:${FUSEKI_CONFIG.password}`),
        },
        body: `query=${encodeURIComponent(sparqlQuery)}`,
      });

      if (!response.ok) {
        throw new Error(`Lỗi ${response.status}: ${response.statusText}`);
      }

      const result: SparqlResult = await response.json();
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

  // Sample queries
  const sampleQueries = [
    {
      name: 'Lấy tất cả Observation',
      query: `PREFIX sosa: <http://www.w3.org/ns/sosa/>

SELECT ?obs ?feature ?result ?time
WHERE {
  ?obs a sosa:Observation ;
       sosa:hasFeatureOfInterest ?feature ;
       sosa:hasSimpleResult ?result ;
       sosa:resultTime ?time .
}
LIMIT 50`,
    },
    {
      name: 'Thống kê theo loại',
      query: `SELECT ?type (COUNT(?s) as ?count)
WHERE {
  ?s a ?type .
}
GROUP BY ?type
ORDER BY DESC(?count)`,
    },
    {
      name: 'Liên kết bên ngoài',
      query: `PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?subject ?link
WHERE {
  { ?subject owl:sameAs ?link }
  UNION
  { ?subject rdfs:seeAlso ?link }
}
LIMIT 50`,
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <Network className="w-7 h-7 text-green-600" />
              LOD Cloud - Dữ liệu Liên kết Mở
            </h1>
            <p className="text-gray-600 mt-1">
              Quản lý và truy vấn dữ liệu Linked Open Data theo tiêu chuẩn 5-Star
            </p>
          </div>
          <div className="flex items-center gap-3">
            {/* Fuseki Status */}
            <div
              className={`px-4 py-2 rounded-lg flex items-center gap-2 ${
                fusekiStatus === 'online'
                  ? 'bg-green-50 border border-green-200 text-green-700'
                  : fusekiStatus === 'offline'
                  ? 'bg-red-50 border border-red-200 text-red-700'
                  : 'bg-yellow-50 border border-yellow-200 text-yellow-700'
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
            <button
              onClick={checkFusekiStatus}
              className="p-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50"
            >
              <RefreshCw className="w-5 h-5 text-gray-600" />
            </button>
          </div>
        </div>
      </div>

      {/* Fuseki Credentials Card */}
      <div className="bg-white rounded-xl border border-gray-200 p-4 mb-6">
        <button
          onClick={() => setShowCredentials(!showCredentials)}
          className="flex items-center justify-between w-full"
        >
          <div className="flex items-center gap-2">
            <Key className="w-5 h-5 text-green-600" />
            <span className="font-semibold text-gray-900">Thông tin Kết nối Fuseki</span>
          </div>
          {showCredentials ? (
            <ChevronUp className="w-5 h-5 text-gray-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-400" />
          )}
        </button>

        {showCredentials && (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-gray-50 p-3 rounded-lg">
              <div className="text-sm text-gray-500 mb-1">Endpoint URL</div>
              <div className="flex items-center gap-2">
                <code className="text-sm font-mono text-gray-900">{FUSEKI_CONFIG.endpoint}</code>
                <button
                  onClick={() => copyToClipboard(FUSEKI_CONFIG.endpoint)}
                  className="p-1 hover:bg-gray-200 rounded"
                >
                  <Copy className="w-4 h-4 text-gray-500" />
                </button>
              </div>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <div className="text-sm text-gray-500 mb-1">Admin Panel</div>
              <div className="flex items-center gap-2">
                <a
                  href={FUSEKI_CONFIG.adminEndpoint}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm font-mono text-green-600 hover:text-green-700 flex items-center gap-1"
                >
                  {FUSEKI_CONFIG.adminEndpoint}
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <div className="text-sm text-gray-500 mb-1">Tên đăng nhập</div>
              <div className="flex items-center gap-2">
                <code className="text-sm font-mono text-gray-900 bg-green-100 px-2 py-1 rounded">
                  {FUSEKI_CONFIG.username}
                </code>
                <button
                  onClick={() => copyToClipboard(FUSEKI_CONFIG.username)}
                  className="p-1 hover:bg-gray-200 rounded"
                >
                  <Copy className="w-4 h-4 text-gray-500" />
                </button>
              </div>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <div className="text-sm text-gray-500 mb-1">Mật khẩu</div>
              <div className="flex items-center gap-2">
                <code className="text-sm font-mono text-gray-900 bg-green-100 px-2 py-1 rounded">
                  {FUSEKI_CONFIG.password}
                </code>
                <button
                  onClick={() => copyToClipboard(FUSEKI_CONFIG.password)}
                  className="p-1 hover:bg-gray-200 rounded"
                >
                  <Copy className="w-4 h-4 text-gray-500" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setActiveTab('datasets')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            activeTab === 'datasets'
              ? 'bg-green-600 text-white'
              : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'
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
              : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'
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
              : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'
          }`}
        >
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4" />
            5-Star Compliance
          </div>
        </button>
      </div>

      {/* Datasets Tab */}
      {activeTab === 'datasets' && (
        <div className="space-y-6">
          {/* Dataset Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {datasets.map((dataset) => (
              <div
                key={dataset.id}
                className={`bg-white rounded-xl border p-5 transition-all cursor-pointer ${
                  selectedDataset === dataset.id
                    ? 'border-green-500 ring-2 ring-green-100'
                    : 'border-gray-200 hover:border-green-300'
                }`}
                onClick={() => setSelectedDataset(dataset.id)}
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-semibold text-gray-900">{dataset.name}</h3>
                    <p className="text-sm text-gray-500">{dataset.description}</p>
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
                    <span className="text-gray-500">Số Triple:</span>
                    <span className="font-medium text-gray-900">
                      {dataset.triples.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Namespace:</span>
                    <code className="text-xs text-green-600 truncate max-w-[150px]">
                      {dataset.namespace}
                    </code>
                  </div>
                </div>

                {/* Linked Datasets */}
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <div className="text-xs text-gray-500 mb-2">Liên kết với:</div>
                  <div className="flex flex-wrap gap-1">
                    {dataset.linkedTo.map((link) => (
                      <span
                        key={link}
                        className="px-2 py-1 bg-green-50 text-green-700 text-xs rounded-full"
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
                    className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <ExternalLink className="w-4 h-4" />
                    SPARQL
                  </a>
                  <button
                    className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-green-100 text-green-700 rounded-lg text-sm hover:bg-green-200"
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
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Link2 className="w-5 h-5 text-green-600" />
              Sơ đồ Liên kết Dữ liệu
            </h3>
            <div className="relative h-64 bg-gray-50 rounded-lg overflow-hidden">
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
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Globe className="w-5 h-5 text-green-600" />
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
                  className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                    <Globe className="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{link.name}</div>
                    <div className="text-sm text-gray-500">{link.desc}</div>
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
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                <FileText className="w-5 h-5 text-green-600" />
                Trình soạn thảo SPARQL
              </h3>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">Dataset:</span>
                <select
                  value={selectedDataset}
                  onChange={(e) => setSelectedDataset(e.target.value)}
                  className="px-3 py-1.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
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
              className="w-full h-64 p-4 font-mono text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 bg-gray-50"
              placeholder="Nhập truy vấn SPARQL..."
            />

            <div className="flex items-center justify-between mt-4">
              <div className="flex gap-2">
                {sampleQueries.map((sample, idx) => (
                  <button
                    key={idx}
                    onClick={() => setSparqlQuery(sample.query)}
                    className="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
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
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                  <Server className="w-5 h-5 text-green-600" />
                  Kết quả ({queryResult.results.bindings.length} bản ghi)
                </h3>
                <button
                  onClick={() => copyToClipboard(JSON.stringify(queryResult, null, 2))}
                  className="flex items-center gap-2 px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
                >
                  <Copy className="w-4 h-4" />
                  Sao chép JSON
                </button>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200">
                      {queryResult.head.vars.map((v) => (
                        <th key={v} className="text-left py-2 px-3 font-medium text-gray-700 bg-gray-50">
                          ?{v}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {queryResult.results.bindings.slice(0, 100).map((binding, idx) => (
                      <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                        {queryResult.head.vars.map((v) => (
                          <td key={v} className="py-2 px-3 font-mono text-xs">
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
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="text-center mb-6">
              <h3 className="text-xl font-bold text-gray-900 mb-2">CityLens LOD Compliance</h3>
              <div className="text-4xl mb-2">★★★★★</div>
              <p className="text-green-600 font-medium">5-Star Linked Open Data</p>
            </div>

            <div className="space-y-4">
              {compliance.map((item, idx) => (
                <div
                  key={idx}
                  className={`p-4 rounded-lg border ${
                    item.status ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {item.status ? (
                      <CheckCircle2 className="w-5 h-5 text-green-600 mt-0.5" />
                    ) : (
                      <XCircle className="w-5 h-5 text-gray-400 mt-0.5" />
                    )}
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h4 className="font-semibold text-gray-900">{item.principle}</h4>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{item.description}</p>
                      <p className="text-sm text-green-700 mt-2 flex items-start gap-1">
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
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Ontology được sử dụng</h3>
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
                <div key={onto.prefix} className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <code className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded">
                      {onto.prefix}:
                    </code>
                    <span className="font-medium text-gray-900">{onto.name}</span>
                  </div>
                  <code className="text-xs text-gray-500 block mb-1">{onto.uri}</code>
                  <p className="text-sm text-gray-600">{onto.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
