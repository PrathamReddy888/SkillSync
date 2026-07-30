import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import { ThemeProvider } from '@/components/theme-provider'
import './globals.css'

const geistSans = Geist({
  subsets: ['latin'],
  variable: '--font-sans',
  display: 'swap',
})

const geistMono = Geist_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  display: 'swap',
})

export const metadata: Metadata = {
  title: {
    default: 'SkillSync — Prove Your Skills. Get Discovered.',
    template: '%s · SkillSync',
  },
  description:
    'SkillSync is an advanced talent assessment platform featuring adaptive multi-round testing, real-time leaderboards, and intelligent matching for forward-thinking companies.',
  keywords: [
    'skill assessment',
    'talent platform',
    'coding challenges',
    'technical hiring',
    'adaptive testing',
    'leaderboard',
    'developer assessment',
  ],
  authors: [{ name: 'SkillSync' }],
  creator: 'SkillSync',
  openGraph: {
    title: 'SkillSync — Prove Your Skills. Get Discovered.',
    description:
      'Adaptive multi-round testing, real-time leaderboards, and intelligent talent matching.',
    type: 'website',
    siteName: 'SkillSync',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'SkillSync — Prove Your Skills. Get Discovered.',
    description:
      'Adaptive multi-round testing, real-time leaderboards, and intelligent talent matching.',
  },
  icons: {
    icon: [
      {
        url: '/icon-light-32x32.png',
        media: '(prefers-color-scheme: light)',
      },
      {
        url: '/icon-dark-32x32.png',
        media: '(prefers-color-scheme: dark)',
      },
      {
        url: '/icon.svg',
        type: 'image/svg+xml',
      },
    ],
    apple: '/apple-icon.png',
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${geistSans.variable} ${geistMono.variable}`}
    >
      <body className="font-sans antialiased bg-background text-foreground min-h-screen">
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
        {process.env.NODE_ENV === 'production' && <Analytics />}
      </body>
    </html>
  )
}
