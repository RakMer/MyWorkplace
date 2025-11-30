import { getCachedPrices, setCachedPrices } from "@/lib/priceCache";
import { fetchLatestFuelPrices } from "@/lib/fuelPriceApi";

// Şirket metadata - API'den dönen şirketleri dinamik olarak ekleyeceğiz
const baseCompanyMetadata: Record<string, { logo: string; headquarters: string; founded: number }> = {
  SHELL: { logo: "🔴", headquarters: "İstanbul", founded: 1980 },
  OPET: { logo: "🟠", headquarters: "İstanbul", founded: 1974 },
  AYGAZ: { logo: "🟡", headquarters: "Ankara", founded: 1972 },
  TOTAL: { logo: "🔵", headquarters: "İstanbul", founded: 1980 },
  PETREN: { logo: "🟢", headquarters: "İzmir", founded: 1993 },
  BATTAL: { logo: "🟣", headquarters: "Ankara", founded: 1998 },
  LUKOIL: { logo: "🟤", headquarters: "Rusya", founded: 1991 },
  BP: { logo: "🟩", headquarters: "İngiltere", founded: 1909 },
  MOBIL: { logo: "🟪", headquarters: "ABD", founded: 1920 },
  ENERJİ: { logo: "⚫", headquarters: "Türkiye", founded: 2000 },
};

async function buildCompanyData() {
  // Önce cache'i kontrol et
  let cachedData = getCachedPrices();
  if (cachedData) {
    return cachedData;
  }

  // API'den yeni fiyatları çek (sadece ilk kez)
  const prices = await fetchLatestFuelPrices();
  const now = new Date().toISOString();

  // API'den dönen şirketler + metadata'yı birleştir
  let id = 1;
  const data = Object.entries(prices).map(([companyName, priceData]: [string, any]) => {
    const metadata = baseCompanyMetadata[companyName] || {
      logo: "⚪",
      headquarters: "Bilinmiyor",
      founded: 2000,
    };

    return {
      id: id++,
      name: companyName,
      ...metadata,
      ...priceData,
      priceUpdateTime: now,
    };
  });

  // Cache'e kaydet
  setCachedPrices(data);

  return data;
}

export async function GET() {
  try {
    const data = await buildCompanyData();
    return Response.json({
      success: true,
      data,
      lastUpdated: new Date().toISOString(),
    });
  } catch (error) {
    console.error("Error fetching fuel prices:", error);
    return Response.json(
      {
        success: false,
        message: "Fiyatlar yüklenirken hata oluştu",
      },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const companies = await buildCompanyData();
    const company = companies.find((c: any) => c.id === body.id) as any;

    if (!company) {
      return Response.json(
        { success: false, message: "Şirket bulunamadı" },
        { status: 404 }
      );
    }

    if (body.gasoline95) company.gasoline95 = body.gasoline95;
    if (body.gasoline98) company.gasoline98 = body.gasoline98;
    if (body.diesel) company.diesel = body.diesel;
    if (body.lpg) company.lpg = body.lpg;

    company.priceUpdateTime = new Date().toISOString();

    return Response.json({
      success: true,
      message: "Fiyatlar güncellendi",
      data: company,
    });
  } catch (error) {
    console.error("Error updating prices:", error);
    return Response.json(
      {
        success: false,
        message: "Fiyatlar güncellenirken hata oluştu",
      },
      { status: 500 }
    );
  }
}
