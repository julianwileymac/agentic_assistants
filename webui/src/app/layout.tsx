import type { Metadata } from "next";
import { JetBrains_Mono, Space_Grotesk } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";
import { SidebarProvider, SidebarInset } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/layout/app-sidebar";
import { Header } from "@/components/layout/header";
import { HelpPanel } from "@/components/help/help-panel";
import { NotesPanel } from "@/components/learning/notes-panel";
import { FloatingActions } from "@/components/layout/floating-actions";

const spaceGrotesk = Space_Grotesk({
  variable: "--font-sans",
  subsets: ["latin"],
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Agentic Control Panel",
  description: "Multi-Agent Development Environment Control Panel",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${spaceGrotesk.variable} ${jetbrainsMono.variable} font-sans antialiased`}
      >
        <Providers>
          <SidebarProvider>
            <AppSidebar />
            <SidebarInset>
              <Header />
              <div className="relative flex-1">
                <main className="h-full overflow-auto p-6 pr-6 md:pr-8">
                  {children}
                </main>
                <HelpPanel />
                <NotesPanel />
                <FloatingActions />
              </div>
            </SidebarInset>
          </SidebarProvider>
        </Providers>
      </body>
    </html>
  );
}
