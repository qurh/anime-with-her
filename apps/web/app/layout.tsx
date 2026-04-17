import "./globals.css";
import Link from "next/link";
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
      <body className={notoSansSc.variable}>
        <header className="topbar">
          <div className="topbar-inner">
            <Link className="brand" href="/">
              AI 配音导演台
            </Link>
            <nav className="topbar-nav" aria-label="主导航">
              <Link href="/">创建任务</Link>
              <Link href="/runs?episode_id=episode_1">任务历史</Link>
            </nav>
          </div>
        </header>
        <div className="shell-body">{children}</div>
      </body>
    </html>
  );
}
