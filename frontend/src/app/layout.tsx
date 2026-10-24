import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Display Antrean Poliklinik - Husada Medika",
  description: "Display antrean poliklinik dengan pemanggilan suara otomatis Web Speech Synthesis API",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id" className={`${inter.variable} h-full`}>
      <body className="h-full flex flex-col font-sans bg-background text-foreground font-medium">
        {children}
      </body>
    </html>
  );
}
