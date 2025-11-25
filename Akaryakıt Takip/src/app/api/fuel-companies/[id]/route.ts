import { NextRequest } from "next/server";

const prices = {
  "1": { gasoline95: 32.45, gasoline98: 35.20, diesel: 31.80, lpg: 18.50 }, // SHELL
  "2": { gasoline95: 32.10, gasoline98: 34.85, diesel: 31.50, lpg: 18.20 }, // OPET
  "3": { gasoline95: 32.30, gasoline98: 35.05, diesel: 31.65, lpg: 17.90 }, // AYGAZ
  "4": { gasoline95: 32.55, gasoline98: 35.35, diesel: 31.95, lpg: 18.60 }, // TOTAL
  "5": { gasoline95: 32.00, gasoline98: 34.70, diesel: 31.40, lpg: 18.00 }, // PETREN
  "6": { gasoline95: 31.95, gasoline98: 34.65, diesel: 31.35, lpg: 17.95 }, // BATTAL
};

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  
  if (!prices[id as keyof typeof prices]) {
    return Response.json(
      { success: false, message: "Şirket fiyatları bulunamadı" },
      { status: 404 }
    );
  }

  return Response.json({
    success: true,
    data: {
      companyId: id,
      prices: prices[id as keyof typeof prices],
      lastUpdated: new Date().toISOString(),
    },
  });
}
