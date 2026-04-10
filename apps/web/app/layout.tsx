import type { ReactNode } from "react";
import "./globals.css";

export const metadata = {
  title: "Anime With Her Console",
  description: "Role-level dubbing operations console",
};

type RootLayoutProps = {
  children: ReactNode;
};

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
