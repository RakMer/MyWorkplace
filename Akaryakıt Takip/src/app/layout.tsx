import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Akaryakıt Takip - Güncel Fiyatlar",
  description: "Türkiye'deki akaryakıt şirketlerinin güncel fiyatlarını görüntüleyin",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="tr">
      <body>{children}</body>
    </html>
  );
}
