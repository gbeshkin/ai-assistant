import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Tallinn AI Assistant V2",
  description: "Digital city representative demo for Tallinn with voice and animated avatar"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
