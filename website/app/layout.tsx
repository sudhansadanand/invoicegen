import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BillThis – Free GST Invoice Generator for Indian Businesses",
  description:
    "Create professional GST-compliant invoices in seconds. Free, simple, and built for Indian businesses. No sign-up required.",
  keywords: ["GST invoice", "invoice generator", "Indian invoice", "tax invoice", "CGST", "SGST", "free invoice maker"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
