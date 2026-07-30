'use client'

import { Navigation } from '@/components/navigation'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import Link from 'next/link'
import {
  CheckCircle,
  TrendingUp,
  Users,
  Zap,
  Shield,
  ArrowRight,
  Target,
  Trophy,
  Code2,
  Sparkles,
  Github,
  Twitter,
  Linkedin,
  Star,
} from 'lucide-react'

const features = [
  {
    icon: Zap,
    title: 'Adaptive Testing',
    description:
      'Multi-round assessments that dynamically adjust difficulty based on your real-time performance.',
    color: 'from-amber-400 to-orange-500',
  },
  {
    icon: TrendingUp,
    title: 'Live Leaderboards',
    description:
      'Track your rank and compete with talent globally. See where you stand in real-time.',
    color: 'from-emerald-400 to-teal-500',
  },
  {
    icon: Users,
    title: 'Smart Matching',
    description:
      'Companies discover top talent aligned with their specific needs through intelligent filters.',
    color: 'from-blue-400 to-indigo-500',
  },
  {
    icon: Shield,
    title: 'Fair Assessment',
    description:
      'Anti-cheat technology and proctoring ensure integrity across all evaluations.',
    color: 'from-rose-400 to-pink-500',
  },
]

const steps = [
  {
    icon: Target,
    step: '01',
    title: 'Sign Up & Verify',
    description:
      'Create your profile in minutes. Verify your identity to unlock all challenges and features.',
  },
  {
    icon: Code2,
    step: '02',
    title: 'Take Adaptive Challenges',
    description:
      'Compete through three adaptive rounds that test your skills at the right difficulty level.',
  },
  {
    icon: Trophy,
    step: '03',
    title: 'Get Discovered',
    description:
      'Climb the leaderboard and get matched with companies looking for exactly your skill set.',
  },
]

const stats = [
  { value: '50K+', label: 'Active Participants' },
  { value: '1,200+', label: 'Companies Hiring' },
  { value: '98%', label: 'Match Accuracy' },
  { value: '24/7', label: 'Challenge Access' },
]

const testimonials = [
  {
    quote:
      'SkillSync completely changed how I approach technical interviews. The adaptive challenges felt just like real rounds.',
    author: 'Priya Sharma',
    role: 'Software Engineer at Google',
    rating: 5,
  },
  {
    quote:
      'As a hiring manager, the matching algorithm saves us weeks of screening. The quality of candidates is outstanding.',
    author: 'Rajesh Kumar',
    role: 'Engineering Lead at Microsoft',
    rating: 5,
  },
  {
    quote:
      'The leaderboard system kept me motivated. I went from top 500 to top 10 in two months of practice.',
    author: 'Ananya Patel',
    role: 'Full-Stack Developer',
    rating: 5,
  },
]

const footerLinks = {
  Platform: [
    { label: 'Challenges', href: '/challenges' },
    { label: 'Leaderboard', href: '/leaderboard' },
    { label: 'How It Works', href: '#how-it-works' },
    { label: 'FAQ', href: '/faq' },
  ],
  Company: [
    { label: 'About Us', href: '#' },
    { label: 'Blog', href: '#' },
    { label: 'Careers', href: '#' },
    { label: 'Contact', href: '#' },
  ],
  Legal: [
    { label: 'Privacy Policy', href: '#' },
    { label: 'Terms of Service', href: '#' },
    { label: 'Cookie Policy', href: '#' },
  ],
}

const socialLinks = [
  { icon: Github, href: '#', label: 'GitHub' },
  { icon: Twitter, href: '#', label: 'Twitter' },
  { icon: Linkedin, href: '#', label: 'LinkedIn' },
]

export default function Home() {
  return (
    <>
      <Navigation />
      <main>
        {/* ─── Hero Section ─────────────────────────────────────────────── */}
        <section className="relative min-h-screen flex items-center justify-center overflow-hidden px-4 sm:px-6 lg:px-8">
          {/* Decorative gradient orbs */}
          <div className="absolute inset-0 -z-10 overflow-hidden">
            <div className="absolute top-1/4 -left-20 w-[500px] h-[500px] rounded-full bg-primary/20 dark:bg-primary/10 blur-[120px] animate-float-slow" />
            <div className="absolute bottom-1/4 -right-20 w-[500px] h-[500px] rounded-full bg-accent/20 dark:bg-accent/10 blur-[120px] animate-float-slow" style={{ animationDelay: '4s' }} />
            <div className="absolute inset-0 bg-grid-pattern opacity-30 [mask-image:radial-gradient(ellipse_at_center,black_30%,transparent_70%)]" />
          </div>

          <div className="max-w-5xl mx-auto text-center">
            {/* Badge */}
            <div className="animate-fade-in-up mb-8 flex justify-center">
              <Badge variant="outline" className="px-4 py-1.5 text-sm border-primary/30 bg-primary/5 gap-2">
                <Sparkles className="w-3.5 h-3.5 text-primary" />
                <span className="text-primary/90">Now with AI-powered skill matching</span>
              </Badge>
            </div>

            {/* Headline */}
            <h1 className="animate-fade-in-up delay-100 text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight mb-6 leading-[1.05]">
              Prove Your Skills.
              <br />
              <span className="text-gradient">Get Discovered.</span>
            </h1>

            {/* Subtext */}
            <p className="animate-fade-in-up delay-200 text-lg sm:text-xl text-muted-foreground mb-10 max-w-2xl mx-auto leading-relaxed">
              SkillSync is an advanced talent assessment platform featuring
              adaptive multi-round testing, real-time leaderboards, and
              intelligent matching for forward-thinking companies.
            </p>

            {/* CTAs */}
            <div className="animate-fade-in-up delay-300 flex flex-col sm:flex-row gap-4 justify-center mb-16">
              <Button variant="gradient" size="xl" asChild>
                <Link href="/signup">
                  Get Started Free
                  <ArrowRight className="w-5 h-5" />
                </Link>
              </Button>
              <Button variant="outline" size="xl" asChild>
                <Link href="/leaderboard">View Leaderboard</Link>
              </Button>
            </div>

            {/* Stats row */}
            <div className="animate-fade-in-up delay-500 grid grid-cols-2 md:grid-cols-4 gap-8 max-w-3xl mx-auto pt-8 border-t border-border/60">
              {stats.map((stat) => (
                <div key={stat.label} className="text-center">
                  <div className="text-3xl sm:text-4xl font-bold text-gradient mb-1">
                    {stat.value}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ─── Features Section ─────────────────────────────────────────── */}
        <section className="relative py-20 sm:py-32 bg-background">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            {/* Section header */}
            <div className="text-center mb-16 max-w-2xl mx-auto">
              <Badge variant="outline" className="mb-4 text-primary border-primary/30">
                Features
              </Badge>
              <h2 className="text-4xl sm:text-5xl font-bold tracking-tight mb-4">
                Everything you need to
                <span className="text-gradient"> stand out</span>
              </h2>
              <p className="text-muted-foreground text-lg">
                Our platform combines cutting-edge assessment technology with
                an intuitive design to help you showcase your true potential.
              </p>
            </div>

            {/* Feature cards */}
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {features.map((feature, i) => {
                const Icon = feature.icon
                return (
                  <Card
                    key={feature.title}
                    className="gradient-border group relative overflow-hidden hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
                    style={{
                      animation: `fade-in-up 0.5s ease-out ${i * 100}ms forwards`,
                      opacity: 0,
                    }}
                  >
                    <CardHeader>
                      <div
                        className={`inline-flex w-12 h-12 rounded-xl bg-gradient-to-br ${feature.color} p-0.5 mb-2`}
                      >
                        <div className="flex-1 rounded-[10px] bg-card flex items-center justify-center">
                          <Icon className="w-6 h-6 text-foreground" />
                        </div>
                      </div>
                      <CardTitle className="text-lg">{feature.title}</CardTitle>
                      <CardDescription className="text-sm leading-relaxed">
                        {feature.description}
                      </CardDescription>
                    </CardHeader>
                    {/* Hover gradient sheen */}
                    <div className="absolute inset-0 -z-10 bg-gradient-to-br from-primary/5 to-accent/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  </Card>
                )
              })}
            </div>
          </div>
        </section>

        {/* ─── How It Works ─────────────────────────────────────────────── */}
        <section
          id="how-it-works"
          className="relative py-20 sm:py-32 bg-muted/30 overflow-hidden"
        >
          {/* Decorative dot pattern */}
          <div className="absolute inset-0 bg-dot-pattern opacity-50 [mask-image:radial-gradient(ellipse_at_center,black_20%,transparent_70%)]" />

          <div className="relative max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16 max-w-2xl mx-auto">
              <Badge variant="outline" className="mb-4 text-primary border-primary/30">
                How It Works
              </Badge>
              <h2 className="text-4xl sm:text-5xl font-bold tracking-tight mb-4">
                Three steps to your
                <span className="text-gradient"> dream career</span>
              </h2>
              <p className="text-muted-foreground text-lg">
                From sign-up to getting matched with top companies — it&apos;s
                simpler than you think.
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8 lg:gap-12">
              {steps.map((step, i) => {
                const Icon = step.icon
                return (
                  <div key={step.step} className="relative text-center group">
                    {/* Connector line (desktop) */}
                    {i < steps.length - 1 && (
                      <div className="hidden md:block absolute top-12 left-[60%] w-full h-px bg-gradient-to-r from-border to-transparent" />
                    )}

                    {/* Step icon */}
                    <div className="relative inline-flex mb-6">
                      <div className="absolute inset-0 bg-gradient-to-br from-primary to-accent rounded-2xl blur-md opacity-30 group-hover:opacity-60 transition-opacity" />
                      <div className="relative bg-gradient-to-br from-primary to-accent rounded-2xl p-4 shadow-lg">
                        <Icon className="w-8 h-8 text-primary-foreground" />
                      </div>
                    </div>

                    {/* Step number */}
                    <div className="text-sm font-bold text-primary/60 mb-2">
                      Step {step.step}
                    </div>

                    <h3 className="text-xl font-semibold mb-3">{step.title}</h3>
                    <p className="text-muted-foreground leading-relaxed max-w-xs mx-auto">
                      {step.description}
                    </p>
                  </div>
                )
              })}
            </div>
          </div>
        </section>

        {/* ─── Testimonials ─────────────────────────────────────────────── */}
        <section className="py-20 sm:py-32 bg-background">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16 max-w-2xl mx-auto">
              <Badge variant="outline" className="mb-4 text-primary border-primary/30">
                Testimonials
              </Badge>
              <h2 className="text-4xl sm:text-5xl font-bold tracking-tight mb-4">
                Loved by talent and
                <span className="text-gradient"> companies alike</span>
              </h2>
            </div>

            <div className="grid md:grid-cols-3 gap-6">
              {testimonials.map((t, i) => (
                <Card
                  key={t.author}
                  className="hover:shadow-lg transition-shadow"
                  style={{
                    animation: `fade-in-up 0.5s ease-out ${i * 100}ms forwards`,
                    opacity: 0,
                  }}
                >
                  <CardContent className="space-y-4">
                    {/* Stars */}
                    <div className="flex gap-0.5">
                      {Array.from({ length: t.rating }).map((_, idx) => (
                        <Star
                          key={idx}
                          className="w-4 h-4 fill-amber-400 text-amber-400"
                        />
                      ))}
                    </div>
                    {/* Quote */}
                    <p className="text-foreground/90 leading-relaxed">
                      &ldquo;{t.quote}&rdquo;
                    </p>
                    {/* Author */}
                    <div className="flex items-center gap-3 pt-2 border-t border-border">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-primary-foreground font-semibold text-sm">
                        {t.author.split(' ').map((n) => n[0]).join('')}
                      </div>
                      <div>
                        <div className="font-semibold text-sm">{t.author}</div>
                        <div className="text-xs text-muted-foreground">
                          {t.role}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* ─── CTA Section ──────────────────────────────────────────────── */}
        <section className="relative py-20 sm:py-32 overflow-hidden">
          {/* Gradient background */}
          <div className="absolute inset-0 bg-gradient-to-br from-primary via-primary to-accent animate-gradient" />
          {/* Pattern overlay */}
          <div className="absolute inset-0 bg-dot-pattern opacity-20" />
          {/* Glow orbs */}
          <div className="absolute top-0 left-1/4 w-96 h-96 rounded-full bg-white/10 blur-[100px] animate-pulse-glow" />
          <div className="absolute bottom-0 right-1/4 w-96 h-96 rounded-full bg-white/10 blur-[100px] animate-pulse-glow" style={{ animationDelay: '2s' }} />

          <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-4xl sm:text-5xl font-bold mb-4 text-white">
              Ready to Transform Your Career?
            </h2>
            <p className="text-lg mb-10 text-white/90 max-w-2xl mx-auto">
              Join thousands of professionals proving their skills and getting
              discovered by top companies on SkillSync.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                size="xl"
                variant="secondary"
                asChild
                className="bg-white text-primary hover:bg-white/90"
              >
                <Link href="/signup">
                  Start Your Journey
                  <ArrowRight className="w-5 h-5" />
                </Link>
              </Button>
              <Button
                size="xl"
                variant="outline"
                asChild
                className="border-white/30 text-white hover:bg-white/10 hover:text-white"
              >
                <Link href="/challenges">Browse Challenges</Link>
              </Button>
            </div>
          </div>
        </section>

        {/* ─── Footer ──────────────────────────────────────────────────── */}
        <footer className="bg-card border-t border-border">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
            <div className="grid md:grid-cols-5 gap-8 mb-12">
              {/* Brand */}
              <div className="md:col-span-2">
                <Link href="/" className="flex items-center gap-2 mb-4">
                  <div className="bg-gradient-to-br from-primary to-accent rounded-lg p-1.5">
                    <Sparkles className="w-5 h-5 text-primary-foreground" />
                  </div>
                  <span className="text-xl font-bold">
                    Skill<span className="text-gradient">Sync</span>
                  </span>
                </Link>
                <p className="text-sm text-muted-foreground max-w-xs leading-relaxed mb-6">
                  Advanced talent assessment and matching platform. Prove your
                  skills and get discovered by top companies.
                </p>
                {/* Social icons */}
                <div className="flex gap-3">
                  {socialLinks.map((social) => {
                    const Icon = social.icon
                    return (
                      <a
                        key={social.label}
                        href={social.href}
                        aria-label={social.label}
                        className="w-9 h-9 rounded-lg border border-border flex items-center justify-center text-muted-foreground hover:text-primary hover:border-primary/30 hover:bg-primary/5 transition-all"
                      >
                        <Icon className="w-4 h-4" />
                      </a>
                    )
                  })}
                </div>
              </div>

              {/* Link columns */}
              {Object.entries(footerLinks).map(([title, links]) => (
                <div key={title}>
                  <h4 className="font-semibold text-foreground mb-4">{title}</h4>
                  <ul className="space-y-3">
                    {links.map((link) => (
                      <li key={link.label}>
                        <Link
                          href={link.href}
                          className="text-sm text-muted-foreground hover:text-primary transition-colors"
                        >
                          {link.label}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>

            {/* Bottom bar */}
            <div className="flex flex-col sm:flex-row justify-between items-center gap-4 pt-8 border-t border-border">
              <p className="text-sm text-muted-foreground">
                &copy; {new Date().getFullYear()} SkillSync. All rights reserved.
              </p>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <CheckCircle className="w-4 h-4 text-emerald-500" />
                <span>SOC 2 compliant · GDPR ready</span>
              </div>
            </div>
          </div>
        </footer>
      </main>
    </>
  )
}
