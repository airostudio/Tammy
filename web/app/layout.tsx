import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ENDCOM.NET - AI Virtual Executive Assistant & Receptionist",
  description:
    "ENDCOM.NET's virtual assistant Tammy answers your calls, manages your calendar, and keeps your front desk running - a virtual executive assistant and receptionist for growing businesses.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className="h-full antialiased">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,600;1,500;1,600&family=Work+Sans:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-full flex flex-col font-sans">{children}</body>
    </html>
  );
}
