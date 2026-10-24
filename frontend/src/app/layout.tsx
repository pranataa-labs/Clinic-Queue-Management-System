import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";

const plusJakartaSans = Plus_Jakarta_Sans({
  variable: "--font-sans",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Display Antrean Poliklinik - Audio Queue Calling System",
  description: "Display antrean poliklinik dengan pemanggilan suara otomatis Web Speech Synthesis API",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id" className={`${plusJakartaSans.variable} h-full`}>
      <body className="h-full flex flex-col font-sans bg-[#fafafa] text-zinc-950 font-medium">
        {children}
      </body>
    </html>
  );
}
