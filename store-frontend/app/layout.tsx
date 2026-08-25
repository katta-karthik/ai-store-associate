import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ShopAgent — AI Store Associate Experience",
  description: "Next-generation e-commerce storefront powered by an agentic AI Store Associate that controls filters, compares products, and manages your shopping cart in real time.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased min-h-screen bg-[#09090b] text-[#f4f4f5]">
        {children}
      </body>
    </html>
  );
}
