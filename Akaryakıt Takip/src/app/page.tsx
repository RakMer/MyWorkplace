"use client";

import { useEffect, useState } from "react";
import { TrendingUp, TrendingDown, RefreshCw, Fuel } from "lucide-react";

interface FuelCompany {
  id: number;
  name: string;
  logo: string;
  gasoline95: number;
  gasoline98: number;
  diesel: number;
  lpg: number;
  headquarters: string;
  founded: number;
  priceUpdateTime: string;
}

export default function Home() {
  const [companies, setCompanies] = useState<FuelCompany[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string>("");
  const [selectedCompany, setSelectedCompany] = useState<FuelCompany | null>(null);

  const fetchCompanies = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch("/api/fuel-companies");
      const result = await response.json();
      
      if (result.success) {
        setCompanies(result.data);
        setLastUpdated(result.lastUpdated);
      }
    } catch (err) {
      setError("Veriler yüklenirken hata oluştu: " + (err instanceof Error ? err.message : "Bilinmeyen hata"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCompanies();
    const interval = setInterval(fetchCompanies, 30000); // Her 30 saniyede bir yenile
    return () => clearInterval(interval);
  }, []);

  const getAveragePrice = (type: keyof Omit<FuelCompany, "id" | "name" | "logo" | "headquarters" | "founded" | "priceUpdateTime">) => {
    if (companies.length === 0) return 0;
    const sum = companies.reduce((acc, company) => acc + company[type], 0);
    return (sum / companies.length).toFixed(2);
  };

  const getCheapestCompany = (type: keyof Omit<FuelCompany, "id" | "name" | "logo" | "headquarters" | "founded" | "priceUpdateTime">) => {
    if (companies.length === 0) return null;
    return companies.reduce((min, company) => 
      company[type] < min[type] ? company : min
    );
  };

  const getMostExpensiveCompany = (type: keyof Omit<FuelCompany, "id" | "name" | "logo" | "headquarters" | "founded" | "priceUpdateTime">) => {
    if (companies.length === 0) return null;
    return companies.reduce((max, company) => 
      company[type] > max[type] ? company : max
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-lg">
        <div className="container max-w-7xl mx-auto px-4 py-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Fuel className="w-10 h-10 text-indigo-600" />
              <div>
                <h1 className="text-3xl font-bold text-gray-800">Akaryakıt Takip</h1>
                <p className="text-gray-600">Türkiye'deki güncel akaryakıt fiyatları</p>
              </div>
            </div>
            <button
              onClick={fetchCompanies}
              disabled={loading}
              className="flex items-center space-x-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg transition"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? "animate-spin" : ""}`} />
              <span>{loading ? "Yükleniyor..." : "Yenile"}</span>
            </button>
          </div>
          {lastUpdated && (
            <p className="text-sm text-gray-500 mt-4">
              Son güncelleme: {new Date(lastUpdated).toLocaleString("tr-TR")}
            </p>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="container max-w-7xl mx-auto px-4 py-8">
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mb-8">
            {error}
          </div>
        )}

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg p-6 shadow-lg">
            <h3 className="text-gray-600 text-sm font-semibold mb-2">Ortalama Benzin 95 (₺)</h3>
            <p className="text-3xl font-bold text-indigo-600">{getAveragePrice("gasoline95")}</p>
          </div>
          <div className="bg-white rounded-lg p-6 shadow-lg">
            <h3 className="text-gray-600 text-sm font-semibold mb-2">Ortalama Benzin 98 (₺)</h3>
            <p className="text-3xl font-bold text-indigo-600">{getAveragePrice("gasoline98")}</p>
          </div>
          <div className="bg-white rounded-lg p-6 shadow-lg">
            <h3 className="text-gray-600 text-sm font-semibold mb-2">Ortalama Diesel (₺)</h3>
            <p className="text-3xl font-bold text-indigo-600">{getAveragePrice("diesel")}</p>
          </div>
          <div className="bg-white rounded-lg p-6 shadow-lg">
            <h3 className="text-gray-600 text-sm font-semibold mb-2">Ortalama LPG (₺)</h3>
            <p className="text-3xl font-bold text-indigo-600">{getAveragePrice("lpg")}</p>
          </div>
        </div>

        {/* Companies Grid */}
        {loading && companies.length === 0 ? (
          <div className="text-center py-12">
            <div className="animate-spin inline-block">
              <RefreshCw className="w-8 h-8 text-indigo-600" />
            </div>
            <p className="text-gray-600 mt-4">Veriler yükleniyor...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {companies.map((company) => (
              <div
                key={company.id}
                onClick={() => setSelectedCompany(company)}
                className="bg-white rounded-lg shadow-lg hover:shadow-xl transition cursor-pointer overflow-hidden"
              >
                <div className="bg-gradient-to-r from-indigo-500 to-indigo-600 p-4 text-white">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="text-4xl">{company.logo}</span>
                      <div>
                        <h2 className="text-2xl font-bold">{company.name}</h2>
                        <p className="text-sm opacity-90">{company.headquarters}</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="p-6">
                  <div className="space-y-4">
                    <PriceRow
                      label="Benzin 95"
                      price={company.gasoline95}
                      cheapest={getCheapestCompany("gasoline95")}
                      expensive={getMostExpensiveCompany("gasoline95")}
                      company={company}
                    />
                    <PriceRow
                      label="Benzin 98"
                      price={company.gasoline98}
                      cheapest={getCheapestCompany("gasoline98")}
                      expensive={getMostExpensiveCompany("gasoline98")}
                      company={company}
                    />
                    <PriceRow
                      label="Diesel"
                      price={company.diesel}
                      cheapest={getCheapestCompany("diesel")}
                      expensive={getMostExpensiveCompany("diesel")}
                      company={company}
                    />
                    <PriceRow
                      label="LPG"
                      price={company.lpg}
                      cheapest={getCheapestCompany("lpg")}
                      expensive={getMostExpensiveCompany("lpg")}
                      company={company}
                    />
                  </div>

                  <div className="mt-6 pt-6 border-t border-gray-200">
                    <p className="text-xs text-gray-500">
                      Kuruluş Yılı: {company.founded}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      Güncelleme: {new Date(company.priceUpdateTime).toLocaleTimeString("tr-TR")}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Detail Modal */}
      {selectedCompany && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={() => setSelectedCompany(null)}
        >
          <div
            className="bg-white rounded-lg shadow-2xl max-w-md w-full p-8"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center space-x-3 mb-6">
              <span className="text-5xl">{selectedCompany.logo}</span>
              <div>
                <h2 className="text-2xl font-bold">{selectedCompany.name}</h2>
                <p className="text-gray-600">{selectedCompany.headquarters}</p>
              </div>
            </div>

            <div className="space-y-4 mb-6">
              <div className="flex justify-between items-center py-3 border-b">
                <span className="text-gray-700">Benzin 95</span>
                <span className="text-xl font-bold text-indigo-600">₺{selectedCompany.gasoline95.toFixed(2)}</span>
              </div>
              <div className="flex justify-between items-center py-3 border-b">
                <span className="text-gray-700">Benzin 98</span>
                <span className="text-xl font-bold text-indigo-600">₺{selectedCompany.gasoline98.toFixed(2)}</span>
              </div>
              <div className="flex justify-between items-center py-3 border-b">
                <span className="text-gray-700">Diesel</span>
                <span className="text-xl font-bold text-indigo-600">₺{selectedCompany.diesel.toFixed(2)}</span>
              </div>
              <div className="flex justify-between items-center py-3">
                <span className="text-gray-700">LPG</span>
                <span className="text-xl font-bold text-indigo-600">₺{selectedCompany.lpg.toFixed(2)}</span>
              </div>
            </div>

            <div className="bg-gray-50 rounded p-4 mb-6">
              <p className="text-sm text-gray-600">
                <strong>Kuruluş:</strong> {selectedCompany.founded}
              </p>
              <p className="text-sm text-gray-600 mt-2">
                <strong>Son Güncelleme:</strong> {new Date(selectedCompany.priceUpdateTime).toLocaleString("tr-TR")}
              </p>
            </div>

            <button
              onClick={() => setSelectedCompany(null)}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-2 rounded-lg font-semibold transition"
            >
              Kapat
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

interface PriceRowProps {
  label: string;
  price: number;
  cheapest: FuelCompany | null;
  expensive: FuelCompany | null;
  company: FuelCompany;
}

function PriceRow({ label, price, cheapest, expensive, company }: PriceRowProps) {
  let bgColor = "bg-gray-50";
  let badgeColor = "";
  let badgeText = "";

  if (cheapest && company.id === cheapest.id) {
    bgColor = "bg-green-50";
    badgeColor = "text-green-600";
    badgeText = "EN UCUZ";
  } else if (expensive && company.id === expensive.id) {
    bgColor = "bg-red-50";
    badgeColor = "text-red-600";
    badgeText = "EN PAHAL";
  }

  return (
    <div className={`flex justify-between items-center p-3 rounded ${bgColor}`}>
      <div className="flex items-center space-x-2">
        <span className="text-gray-700 font-medium">{label}</span>
        {badgeText && (
          <span className={`text-xs font-bold ${badgeColor}`}>{badgeText}</span>
        )}
      </div>
      <span className="text-lg font-bold text-indigo-600">₺{price.toFixed(2)}</span>
    </div>
  );
}
