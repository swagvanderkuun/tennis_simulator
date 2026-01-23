import type { Metadata, Viewport } from 'next';
import Script from 'next/script';
import { Space_Grotesk, Inter, IBM_Plex_Mono } from 'next/font/google';
import '@/styles/globals.css';

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-display',
  display: 'swap',
});

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-body',
  display: 'swap',
});

const ibmPlexMono = IBM_Plex_Mono({
  subsets: ['latin'],
  weight: ['400', '500', '600'],
  variable: '--font-mono',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'RacketRoute | Tennis Analytics',
  description: 'Professional tennis tournament analytics, simulations, and fantasy optimization',
  applicationName: 'RacketRoute',
  manifest: '/manifest.webmanifest',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: 'RacketRoute',
  },
  icons: {
    icon: '/racketroute-logo.png',
    apple: '/racketroute-logo.png',
  },
  themeColor: '#0B0F16',
};

export const viewport: Viewport = {
  themeColor: '#0B0F16',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: 'cover',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`dark ${spaceGrotesk.variable} ${inter.variable} ${ibmPlexMono.variable}`}
    >
      <body className="min-h-screen bg-background antialiased overscroll-none">
        <Script
          src="http://100.73.243.20:3004/script.js"
          data-website-id="12afec66-74a5-48ca-8049-5a6f5e5762f6"
          strategy="afterInteractive"
        />
        {children}
      </body>
    </html>
  );
}



