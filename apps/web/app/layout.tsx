import "./globals.css";
import type { Metadata } from "next";
import { Noto_Sans_SC } from "next/font/google";
import type { ReactNode } from "react";

const notoSansSc = Noto_Sans_SC({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  display: "swap",
  variable: "--font-sans-zh",
});

export const metadata: Metadata = {
  title: "AI 配音导演台",
  description: "按单集生产，按整季沉淀角色资产。",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="zh-CN">
      <body className={notoSansSc.variable}>{children}</body>
    </html>
  );
}
