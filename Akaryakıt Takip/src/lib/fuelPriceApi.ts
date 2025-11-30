// Türkiye'deki akaryakıt fiyatları için API kaynakları
// Bu dosya farklı veri kaynaklarından fiyatları çeker

export interface FuelPriceData {
  gasoline95: number;
  gasoline98: number;
  diesel: number;
  lpg: number;
}

export interface FuelCompanyPrices {
  [key: string]: FuelPriceData;
}

export interface CollectAPIResponse {
  success: boolean;
  result: Array<{
    marka: string;
    benzin: number;
    katkili: string | number;
  }>;
  lastupdate: string;
}

// CollectAPI ile şirket adı eşleştirmesi
const brandMapping: Record<string, string> = {
  "Lukoil": "LUKOIL",
  "Petrol Ofisi": "OPET",
  "Shell": "SHELL",
  "Total": "TOTAL",
  "Aygaz": "AYGAZ",
  "BP": "BP",
  "Mobil": "MOBIL",
  "Enerji": "ENERJİ",
  "Petren": "PETREN",
  "Battal": "BATTAL",
};

async function fetchFromCollectAPI(): Promise<FuelCompanyPrices | null> {
  // Read API key from environment variables for safety
  const key = process.env.COLLECTAPI_KEY || process.env.NEXT_PUBLIC_COLLECTAPI_KEY;
  if (!key) {
    console.error("CollectAPI key not set in environment (COLLECTAPI_KEY or NEXT_PUBLIC_COLLECTAPI_KEY)");
    return null;
  }

  // build URL
  const url = new URL("https://api.collectapi.com/gasPrice/turkeyGasoline");
  url.searchParams.set("district", "kadikoy");
  url.searchParams.set("city", "istanbul");

  // simple retry with backoff
  const maxRetries = 3;
  const baseDelayMs = 500;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(url.toString(), {
        method: "GET",
        headers: {
          authorization: `apikey ${key}`,
          "content-type": "application/json",
        },
      });

      if (!response.ok) {
        // try to read body for more info
        let bodyText = "";
        try {
          bodyText = await response.text();
        } catch (e) {
          bodyText = `<unable to read body: ${e}>`;
        }
        console.error(`CollectAPI returned status ${response.status}: ${bodyText}`);

        // if 5xx, retry
        if (response.status >= 500 && attempt < maxRetries) {
          const delay = baseDelayMs * attempt;
          console.log(`Retrying CollectAPI in ${delay}ms (attempt ${attempt + 1}/${maxRetries})`);
          await new Promise((r) => setTimeout(r, delay));
          continue;
        }

        return null;
      }

      const data: CollectAPIResponse = await response.json();
      if (!data.success || !data.result) {
        console.error("CollectAPI returned unsuccessful response or empty result");
        return null;
      }

      return parseCollectAPIResponse(data);
    } catch (error) {
      console.error(`Error fetching from CollectAPI (attempt ${attempt}):`, error);
      if (attempt < maxRetries) {
        const delay = baseDelayMs * attempt;
        await new Promise((r) => setTimeout(r, delay));
        continue;
      }
      return null;
    }
  }

  return null;
}

function parseCollectAPIResponse(data: CollectAPIResponse): FuelCompanyPrices {
  const prices: FuelCompanyPrices = {};

  data.result.forEach((item) => {
    // Marka adını kendi şirket adlarımıza eşleştir
    const companyName = brandMapping[item.marka] || item.marka.toUpperCase();

    // CollectAPI benzin fiyatını kullan, diğer türleri hesapla
    const basePrice = item.benzin;

    prices[companyName] = {
      gasoline95: parseFloat(basePrice.toFixed(2)),
      gasoline98: parseFloat((basePrice + 2.5).toFixed(2)), // Yaklaşık fark
      diesel: parseFloat((basePrice - 0.5).toFixed(2)),     // Yaklaşık fark
      lpg: parseFloat((basePrice / 1.8).toFixed(2)),        // Yaklaşık fark
    };
  });

  return prices;
}

// Varsayılan fiyatlar (API başarısız olduğunda)
function getDefaultPrices(): FuelCompanyPrices {
  return {
    SHELL: {
      gasoline95: 32.45,
      gasoline98: 35.20,
      diesel: 31.80,
      lpg: 18.50,
    },
    OPET: {
      gasoline95: 32.10,
      gasoline98: 34.85,
      diesel: 31.50,
      lpg: 18.20,
    },
    AYGAZ: {
      gasoline95: 32.30,
      gasoline98: 35.05,
      diesel: 31.65,
      lpg: 17.90,
    },
    TOTAL: {
      gasoline95: 32.55,
      gasoline98: 35.35,
      diesel: 31.95,
      lpg: 18.60,
    },
    PETREN: {
      gasoline95: 32.00,
      gasoline98: 34.70,
      diesel: 31.40,
      lpg: 18.00,
    },
    BATTAL: {
      gasoline95: 31.95,
      gasoline98: 34.65,
      diesel: 31.35,
      lpg: 17.95,
    },
  };
}

export async function fetchLatestFuelPrices(): Promise<FuelCompanyPrices> {
  console.log("Fetching fuel prices from CollectAPI...");

  // Gerçek API'yi dene (sadece bir kez çağırılacak, cache tarafından korunacak)
  const apiResult = await fetchFromCollectAPI();
  if (apiResult) {
    console.log("Prices successfully fetched from CollectAPI");
    return apiResult;
  }

  // Fallback: Varsayılan fiyatlar
  console.log("Using default prices - API unavailable");
  return getDefaultPrices();
}

export function getPriceDifference(
  prices1: FuelCompanyPrices,
  prices2: FuelCompanyPrices
): {
  differences: { [key: string]: Partial<FuelPriceData> };
  changedCount: number;
} {
  const differences: { [key: string]: Partial<FuelPriceData> } = {};
  let changedCount = 0;

  for (const company in prices1) {
    if (company in prices2) {
      const diff: Partial<FuelPriceData> = {};
      let hasChanges = false;

      (["gasoline95", "gasoline98", "diesel", "lpg"] as const).forEach(
        (fuelType) => {
          const change = prices2[company][fuelType] - prices1[company][fuelType];
          if (Math.abs(change) > 0.01) {
            diff[fuelType] = change;
            hasChanges = true;
          }
        }
      );

      if (hasChanges) {
        differences[company] = diff;
        changedCount++;
      }
    }
  }

  return { differences, changedCount };
}
