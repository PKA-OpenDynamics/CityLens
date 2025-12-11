// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

'use client';

import { 
  Scale, 
  ExternalLink, 
  Database, 
  Globe, 
  CheckCircle2, 
  Copy, 
  FileText,
  Users,
  Share2,
  Briefcase,
  Info,
  Shield,
  BookOpen
} from 'lucide-react';
import { useState } from 'react';

export default function DataLicensePage() {
  const [copied, setCopied] = useState(false);

  const copyAttribution = () => {
    const attribution = `Data from CityLens Smart City Platform (https://citylens.vn) is licensed under CC BY 4.0`;
    navigator.clipboard.writeText(attribution);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const licenses = [
    {
      name: 'Dữ liệu công khai (Public Data)',
      license: 'Creative Commons Attribution 4.0 International (CC BY 4.0)',
      icon: Database,
      color: 'bg-green-500',
      description: 'Tất cả dữ liệu địa lý, thống kê và báo cáo công khai',
      permissions: ['Chia sẻ', 'Sử dụng thương mại', 'Sửa đổi', 'Phân phối'],
      conditions: ['Ghi nhận nguồn (Attribution)'],
      link: 'https://creativecommons.org/licenses/by/4.0/',
    },
    {
      name: 'Mã nguồn phần mềm (Source Code)',
      license: 'GNU General Public License v3.0 (GPL-3.0)',
      icon: FileText,
      color: 'bg-blue-500',
      description: 'Toàn bộ mã nguồn của nền tảng CityLens',
      permissions: ['Sử dụng', 'Sửa đổi', 'Phân phối', 'Thương mại hóa'],
      conditions: ['Công khai mã nguồn', 'Giữ nguyên giấy phép', 'Ghi nhận nguồn'],
      link: 'https://www.gnu.org/licenses/gpl-3.0.html',
    },
    {
      name: 'API Documentation',
      license: 'Creative Commons Attribution 4.0 International (CC BY 4.0)',
      icon: BookOpen,
      color: 'bg-purple-500',
      description: 'Tài liệu API và hướng dẫn sử dụng',
      permissions: ['Chia sẻ', 'Sử dụng thương mại', 'Sửa đổi'],
      conditions: ['Ghi nhận nguồn (Attribution)'],
      link: 'https://creativecommons.org/licenses/by/4.0/',
    },
  ];

  const ccByFeatures = [
    {
      icon: Share2,
      title: 'Chia sẻ tự do',
      description: 'Sao chép và phân phối lại dữ liệu dưới bất kỳ phương tiện hay định dạng nào',
    },
    {
      icon: Briefcase,
      title: 'Sử dụng thương mại',
      description: 'Được phép sử dụng dữ liệu cho mục đích thương mại',
    },
    {
      icon: Users,
      title: 'Sửa đổi và tái tạo',
      description: 'Remix, chuyển đổi và xây dựng dựa trên dữ liệu cho bất kỳ mục đích nào',
    },
    {
      icon: Info,
      title: 'Ghi nhận nguồn',
      description: 'Phải ghi nhận nguồn gốc dữ liệu từ CityLens một cách phù hợp',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-green-50/30 to-white dark:from-gray-950 dark:via-green-950/10 dark:to-gray-950">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-green-600/10 via-transparent to-green-500/10" />
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-green-500/20 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-green-600/10 rounded-full blur-3xl" />
        
        <div className="relative max-w-7xl mx-auto px-6 py-16">
          <div className="text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-100 dark:bg-green-900/30 border border-green-200 dark:border-green-800 mb-6">
              <Scale className="h-4 w-4 text-green-600" />
              <span className="text-sm font-medium text-green-700 dark:text-green-400">Open Data License</span>
            </div>

            {/* Title */}
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
              Giấy phép Dữ liệu Mở
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto mb-8">
              CityLens cam kết cung cấp dữ liệu mở cho cộng đồng. Tất cả dữ liệu công khai được xuất bản 
              với giấy phép <strong className="text-green-600">Creative Commons Attribution 4.0 (CC BY 4.0)</strong>
            </p>

            {/* CC BY 4.0 Badge */}
            <div className="inline-flex items-center gap-4 px-6 py-4 rounded-2xl bg-white dark:bg-gray-800 shadow-xl border border-green-100 dark:border-green-900">
              <div className="flex items-center gap-2">
                <img 
                  src="https://licensebuttons.net/l/by/4.0/88x31.png" 
                  alt="CC BY 4.0"
                  className="h-8"
                />
              </div>
              <div className="text-left">
                <p className="font-semibold text-gray-900 dark:text-white">CC BY 4.0</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">International License</p>
              </div>
              <a
                href="https://creativecommons.org/licenses/by/4.0/"
                target="_blank"
                rel="noopener noreferrer"
                className="ml-2 p-2 rounded-lg bg-green-100 dark:bg-green-900/50 hover:bg-green-200 dark:hover:bg-green-900 transition-colors"
              >
                <ExternalLink className="h-5 w-5 text-green-600" />
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* CC BY 4.0 Features */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-8 flex items-center gap-3">
            <Shield className="h-7 w-7 text-green-600" />
            Quyền lợi theo CC BY 4.0
          </h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {ccByFeatures.map((feature, index) => (
              <div
                key={index}
                className="relative p-6 rounded-2xl bg-white dark:bg-gray-800/50 border border-gray-100 dark:border-gray-700 hover:border-green-300 dark:hover:border-green-700 transition-all hover:shadow-lg group"
              >
                <div className="w-12 h-12 rounded-xl bg-green-100 dark:bg-green-900/30 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <feature.icon className="h-6 w-6 text-green-600" />
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">{feature.title}</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">{feature.description}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Attribution Box */}
        <section className="mb-16">
          <div className="relative p-8 rounded-3xl bg-gradient-to-r from-green-600 to-green-500 text-white overflow-hidden">
            <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4xIj48Y2lyY2xlIGN4PSIzMCIgY3k9IjMwIiByPSIyIi8+PC9nPjwvZz48L3N2Zz4=')] opacity-30" />
            
            <div className="relative">
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Copy className="h-5 w-5" />
                Mẫu ghi nhận nguồn (Attribution)
              </h3>
              
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 mb-4">
                <code className="text-sm text-white/90 break-all">
                  Data from CityLens Smart City Platform (https://citylens.vn) is licensed under CC BY 4.0
                </code>
              </div>
              
              <button
                onClick={copyAttribution}
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-white text-green-600 font-semibold hover:bg-green-50 transition-colors"
              >
                {copied ? (
                  <>
                    <CheckCircle2 className="h-5 w-5" />
                    Đã sao chép!
                  </>
                ) : (
                  <>
                    <Copy className="h-5 w-5" />
                    Sao chép Attribution
                  </>
                )}
              </button>
            </div>
          </div>
        </section>

        {/* All Licenses */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-8 flex items-center gap-3">
            <FileText className="h-7 w-7 text-green-600" />
            Tất cả Giấy phép
          </h2>
          
          <div className="grid md:grid-cols-3 gap-6">
            {licenses.map((license, index) => (
              <div
                key={index}
                className="relative p-6 rounded-2xl bg-white dark:bg-gray-800/50 border border-gray-100 dark:border-gray-700 hover:shadow-xl transition-all group"
              >
                {/* Header */}
                <div className="flex items-start gap-4 mb-4">
                  <div className={`w-12 h-12 rounded-xl ${license.color} flex items-center justify-center flex-shrink-0`}>
                    <license.icon className="h-6 w-6 text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-1">{license.name}</h3>
                    <p className="text-xs text-green-600 dark:text-green-400 font-medium">{license.license}</p>
                  </div>
                </div>

                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">{license.description}</p>

                {/* Permissions */}
                <div className="mb-4">
                  <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-2">Được phép</p>
                  <div className="flex flex-wrap gap-1">
                    {license.permissions.map((perm, i) => (
                      <span key={i} className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-green-100 dark:bg-green-900/30 text-xs text-green-700 dark:text-green-400">
                        <CheckCircle2 className="h-3 w-3" />
                        {perm}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Conditions */}
                <div className="mb-4">
                  <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-2">Điều kiện</p>
                  <div className="flex flex-wrap gap-1">
                    {license.conditions.map((cond, i) => (
                      <span key={i} className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-amber-100 dark:bg-amber-900/30 text-xs text-amber-700 dark:text-amber-400">
                        <Info className="h-3 w-3" />
                        {cond}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Link */}
                <a
                  href={license.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 text-sm text-green-600 hover:text-green-700 font-medium group-hover:underline"
                >
                  Xem chi tiết giấy phép
                  <ExternalLink className="h-4 w-4" />
                </a>
              </div>
            ))}
          </div>
        </section>

        {/* API License Info */}
        <section className="mb-16">
          <div className="p-8 rounded-3xl bg-gray-50 dark:bg-gray-800/30 border border-gray-100 dark:border-gray-700">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-3">
              <Globe className="h-7 w-7 text-green-600" />
              Giấy phép API & OpenAPI Specification
            </h2>
            
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-3">REST API</h3>
                <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                  <p>• <strong>Version:</strong> 0.3.0</p>
                  <p>• <strong>Specification:</strong> OpenAPI 3.1 (OAS 3.1)</p>
                  <p>• <strong>Endpoint:</strong> /api/v1/openapi.json</p>
                  <p>• <strong>License:</strong> GNU General Public License v3.0</p>
                </div>
                
                {/* <a
                  href="/api/v1/docs"
                  className="inline-flex items-center gap-2 mt-4 px-4 py-2 rounded-lg bg-green-600 text-white hover:bg-green-700 transition-colors text-sm font-medium"
                >
                  Xem API Documentation
                  <ExternalLink className="h-4 w-4" />
                </a> */}
              </div>
              
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Dữ liệu trả về từ API</h3>
                <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                  <p>Tất cả dữ liệu trả về từ các endpoint công khai đều được cấp phép theo <strong className="text-green-600">CC BY 4.0</strong>.</p>
                  <p>Bạn có thể tự do sử dụng dữ liệu cho:</p>
                  <ul className="list-disc list-inside ml-2 space-y-1">
                    <li>Nghiên cứu học thuật</li>
                    <li>Phát triển ứng dụng</li>
                    <li>Phân tích dữ liệu</li>
                    <li>Mục đích thương mại</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Contact */}
        <section className="text-center">
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Có câu hỏi về giấy phép? Liên hệ với chúng tôi
          </p>
          <a
            href="mailto:license@citylens.vn"
            className="inline-flex items-center gap-2 text-green-600 hover:text-green-700 font-medium"
          >
            license@citylens.vn
            <ExternalLink className="h-4 w-4" />
          </a>
        </section>
      </div>
    </div>
  );
}
