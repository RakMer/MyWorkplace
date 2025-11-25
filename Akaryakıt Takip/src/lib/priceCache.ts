// Fiyat verilerini bellekte tutmak için cache
let priceCache: any = null;
let lastUpdateTime: Date | null = null;
let hasAPIBeenCalled = false;

// Cache süresi: Sonsuza dek (uygulama yeniden başlatılana kadar)
// API sadece ilk başta bir kez çağırılacak

export interface CachedPrices {
  data: any[];
  lastUpdated: string;
  isFresh: boolean;
}

export function isPriceCacheValid(): boolean {
  // Cache geçerli ise (ilk API çağrısı yapıldıysa), sonsuza kadar geçerli
  if (hasAPIBeenCalled && priceCache) {
    return true;
  }
  return false;
}

export function getCachedPrices(): any[] | null {
  if (isPriceCacheValid()) {
    return priceCache;
  }
  return null;
}

export function setCachedPrices(prices: any[]): void {
  priceCache = prices;
  lastUpdateTime = new Date();
  hasAPIBeenCalled = true;
}

export function getCacheStatus(): {
  isCached: boolean;
  lastUpdated: string | null;
  apiCalled: boolean;
} {
  return {
    isCached: isPriceCacheValid(),
    lastUpdated: lastUpdateTime ? lastUpdateTime.toISOString() : null,
    apiCalled: hasAPIBeenCalled,
  };
}
