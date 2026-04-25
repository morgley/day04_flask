---
name: Linen & Logic
colors:
  surface: '#fafaef'
  surface-dim: '#dadbd0'
  surface-bright: '#fafaef'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f4f4e9'
  surface-container: '#efeee3'
  surface-container-high: '#e9e9de'
  surface-container-highest: '#e3e3d8'
  on-surface: '#1a1c16'
  on-surface-variant: '#444748'
  inverse-surface: '#2f312a'
  inverse-on-surface: '#f1f1e6'
  outline: '#747878'
  outline-variant: '#c4c7c7'
  surface-tint: '#5f5e5e'
  primary: '#181919'
  on-primary: '#ffffff'
  primary-container: '#2d2d2d'
  on-primary-container: '#959494'
  inverse-primary: '#c8c6c6'
  secondary: '#5e604d'
  on-secondary: '#ffffff'
  secondary-container: '#e1e1c9'
  on-secondary-container: '#636451'
  tertiary: '#091a25'
  on-tertiary: '#ffffff'
  tertiary-container: '#1f2f3b'
  on-tertiary-container: '#8697a5'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e4e2e1'
  primary-fixed-dim: '#c8c6c6'
  on-primary-fixed: '#1b1c1c'
  on-primary-fixed-variant: '#474747'
  secondary-fixed: '#e4e4cc'
  secondary-fixed-dim: '#c8c8b0'
  on-secondary-fixed: '#1b1d0e'
  on-secondary-fixed-variant: '#474836'
  tertiary-fixed: '#d3e5f4'
  tertiary-fixed-dim: '#b7c9d8'
  on-tertiary-fixed: '#0c1d28'
  on-tertiary-fixed-variant: '#384955'
  background: '#fafaef'
  on-background: '#1a1c16'
  surface-variant: '#e3e3d8'
typography:
  headline-xl:
    fontFamily: Manrope
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Manrope
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Manrope
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Newsreader
    fontSize: 20px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Newsreader
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  label-md:
    fontFamily: Work Sans
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1.2'
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 8px
  container-max: 800px
  gutter: 24px
  section-gap: 80px
  stack-sm: 12px
  stack-md: 24px
---

## Brand & Style

This design system is built upon a philosophy of "Warm Minimalism." It seeks to bridge the gap between technical precision and human warmth. The target audience includes developers, designers, and thinkers who appreciate long-form content delivered in a distraction-free environment.

The UI style is strictly **Minimalist** with an editorial lean. It prioritizes white space (negative space) as a structural element rather than a void. By utilizing a warm base palette instead of sterile white, the design evokes the feeling of high-quality paper, reducing digital eye strain and encouraging deep reading.

## Colors

The color palette is grounded in natural, earthy tones to provide a "warm tech" aesthetic. 

- **Background (Secondary):** The primary canvas is a warm beige (#F5F5DC), providing a soft, low-contrast foundation.
- **Text (Primary):** Deep Charcoal (#2D2D2D) is used for all primary communication to ensure high legibility while remaining softer than pure black.
- **Accent (Tertiary):** A muted Slate Blue (#7A8B99) serves as a soft accent for links, active states, and subtle highlights.
- **Surface (Neutral):** A slightly darker beige (#EBEBE0) is used for component backgrounds to create subtle separation from the main canvas.

## Typography

The typography strategy employs a dual-font system to balance modern tech with literary depth.

- **Headings:** **Manrope** provides a clean, geometric sans-serif look for titles. Its balanced proportions ensure technical clarity.
- **Body:** **Newsreader** is a serif font designed for on-screen readability. Its classic, editorial feel is essential for the "warm" aspect of the design system, making long-form articles feel sophisticated.
- **Labels & Metadata:** **Work Sans** is used at smaller scales for dates, tags, and UI labels to provide a grounded, functional contrast to the serif body text.

## Layout & Spacing

This design system utilizes a **Fixed Grid** philosophy for article content to maximize readability, while maintaining fluid margins for the overall viewport.

- **Content Width:** The primary reading column is capped at 800px to maintain optimal line lengths for the Newsreader typeface.
- **Vertical Rhythm:** A generous 80px gap is used between major sections to emphasize the minimalist aesthetic.
- **Responsive Behavior:** On mobile devices, margins scale down to 24px, and the grid becomes a single-column fluid layout.

## Elevation & Depth

To maintain a minimalist and "flat" aesthetic, this design system avoids heavy drop shadows. Depth is communicated through:

- **Tonal Layers:** Using the Neutral color (#EBEBE0) to create "Surface" areas that sit slightly above the main Beige background.
- **Low-Contrast Outlines:** Components like cards use a very thin (1px) border that is only slightly darker than the background color.
- **Soft Insets:** Input fields use a subtle inner shadow or a darker tonal background to indicate interactivity without breaking the flat aesthetic.

## Shapes

The shape language is **Soft**. Sharp corners are avoided to maintain the "warm" and approachable personality, but extreme roundness is also avoided to ensure the UI feels structural and organized. 

Standard components utilize a 0.25rem corner radius, while larger containers like featured image masks may use up to 0.5rem. Buttons are never pill-shaped; they remain rectangular with soft corners to align with the technical nature of the blog.

## Components

### Minimalist Cards
Cards are used for blog post previews. They feature no shadows, utilizing a 1px border (#D1D1C2) or a subtle tonal shift. Typography within cards should lead with the Headline-MD style, followed by a brief metadata label.

### Simple Buttons
Buttons are solid Deep Charcoal (#2D2D2D) with Beige (#F5F5DC) text. There are no gradients. Hover states should involve a slight opacity shift or a transition to the Slate Blue accent color.

### Clear Input Fields
Search bars and newsletter inputs should be transparent with a bottom-border only, or a solid background of #EBEBE0. The focus state should be a subtle 1px solid line in the Slate Blue accent color.

### Article Navigation
Pagination and "Next/Previous" links should be purely typographic, using Work Sans to distinguish them from the narrative flow of the article.