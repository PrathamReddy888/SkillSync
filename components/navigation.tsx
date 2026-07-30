'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Menu, X, LogOut, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ThemeToggle } from '@/components/theme-toggle'
import { cn } from '@/lib/utils'

export function Navigation() {
  const [isOpen, setIsOpen] = useState(false)
  const [isAuthenticated] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const pathname = usePathname()

  // Scroll-aware navbar: transparent at top, glass-blur after scrolling
  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 8)
    handleScroll()
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // Close mobile menu on route change
  useEffect(() => {
    setIsOpen(false)
  }, [pathname])

  // Lock body scroll when mobile menu is open
  useEffect(() => {
    document.body.style.overflow = isOpen ? 'hidden' : ''
    return () => {
      document.body.style.overflow = ''
    }
  }, [isOpen])

  const navLinks = [
    { href: '/challenges', label: 'Challenges' },
    { href: '/leaderboard', label: 'Leaderboard' },
    ...(isAuthenticated
      ? [{ href: '/dashboard', label: 'Dashboard' }]
      : []),
  ]

  return (
    <nav
      className={cn(
        'sticky top-0 z-50 transition-all duration-300',
        scrolled
          ? 'glass border-b border-border/60 shadow-sm'
          : 'bg-transparent border-b border-transparent',
      )}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="flex-shrink-0 flex items-center gap-2 group">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-primary to-accent rounded-lg blur-md opacity-50 group-hover:opacity-75 transition-opacity" />
              <div className="relative bg-gradient-to-br from-primary to-accent rounded-lg p-1.5">
                <Sparkles className="w-5 h-5 text-primary-foreground" />
              </div>
            </div>
            <span className="text-xl font-bold tracking-tight">
              Skill<span className="text-gradient">Sync</span>
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  'px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200',
                  pathname === link.href
                    ? 'text-primary bg-primary/10'
                    : 'text-muted-foreground hover:text-foreground hover:bg-muted/60',
                )}
              >
                {link.label}
              </Link>
            ))}
          </div>

          {/* Desktop Right Side */}
          <div className="hidden md:flex items-center gap-2">
            <ThemeToggle />
            {!isAuthenticated ? (
              <>
                <Button variant="ghost" asChild>
                  <Link href="/login">Sign In</Link>
                </Button>
                <Button asChild className="bg-gradient-to-r from-primary to-accent hover:opacity-90 transition-opacity">
                  <Link href="/signup">Get Started</Link>
                </Button>
              </>
            ) : (
              <>
                <Button variant="ghost" size="sm" asChild>
                  <Link href="/profile">Profile</Link>
                </Button>
                <Button variant="ghost" size="sm">
                  <LogOut className="w-4 h-4 mr-2" />
                  Logout
                </Button>
              </>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center gap-1">
            <ThemeToggle />
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="inline-flex items-center justify-center p-2 rounded-lg text-foreground hover:bg-muted transition-colors"
              aria-label={isOpen ? 'Close menu' : 'Open menu'}
              aria-expanded={isOpen}
            >
              <div className="relative w-6 h-6">
                <Menu
                  className={cn(
                    'absolute inset-0 transition-all duration-300',
                    isOpen
                      ? 'rotate-90 opacity-0'
                      : 'rotate-0 opacity-100',
                  )}
                />
                <X
                  className={cn(
                    'absolute inset-0 transition-all duration-300',
                    isOpen
                      ? 'rotate-0 opacity-100'
                      : '-rotate-90 opacity-0',
                  )}
                />
              </div>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation Overlay */}
      <div
        className={cn(
          'md:hidden fixed inset-x-0 top-16 bottom-0 z-40 transition-all duration-300',
          isOpen
            ? 'opacity-100 pointer-events-auto'
            : 'opacity-0 pointer-events-none',
        )}
      >
        <div
          className="absolute inset-0 bg-background/80 backdrop-blur-sm"
          onClick={() => setIsOpen(false)}
        />
        <div
          className={cn(
            'relative bg-card border-t border-border shadow-xl transition-transform duration-300',
            isOpen ? 'translate-y-0' : '-translate-y-4',
          )}
        >
          <div className="px-4 py-6 space-y-1">
            {navLinks.map((link, i) => (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  'block px-4 py-3 rounded-lg text-base font-medium transition-colors',
                  pathname === link.href
                    ? 'text-primary bg-primary/10'
                    : 'text-foreground hover:bg-muted',
                )}
                style={{
                  animation: isOpen
                    ? `fade-in-up 0.3s ease-out ${i * 50}ms forwards`
                    : 'none',
                }}
              >
                {link.label}
              </Link>
            ))}

            <div className="pt-4 mt-4 border-t border-border space-y-2">
              {!isAuthenticated ? (
                <>
                  <Button
                    variant="outline"
                    className="w-full"
                    asChild
                  >
                    <Link href="/login">Sign In</Link>
                  </Button>
                  <Button
                    className="w-full bg-gradient-to-r from-primary to-accent"
                    asChild
                  >
                    <Link href="/signup">Get Started</Link>
                  </Button>
                </>
              ) : (
                <>
                  <Button className="w-full" variant="outline" asChild>
                    <Link href="/profile">Profile</Link>
                  </Button>
                  <Button className="w-full" variant="outline">
                    <LogOut className="w-4 h-4 mr-2" />
                    Logout
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}
