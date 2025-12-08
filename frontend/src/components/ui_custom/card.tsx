//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/card.tsx
//*       Custom Card extending shadcn with overflow-hidden
//*       (Placeholder for future customizations)
//*........................................................

import * as React from "react"
import {
  Card as ShadcnCard,
  CardHeader as ShadcnCardHeader,
  CardTitle as ShadcnCardTitle,
  CardDescription as ShadcnCardDescription,
  CardContent as ShadcnCardContent,
  CardFooter as ShadcnCardFooter,
} from "@/components/ui/card"
import { cn } from "@/lib/utils"

// Custom Card with overflow-hidden for proper rounded corners
const Card = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <ShadcnCard
    ref={ref}
    className={cn("overflow-hidden", className)}
    {...props}
  />
))
Card.displayName = "Card"

// Re-export shadcn components as-is (placeholder for future customizations)
const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <ShadcnCardHeader
    ref={ref}
    className={className}
    {...props}
  />
))
CardHeader.displayName = "CardHeader"

const CardTitle = ShadcnCardTitle
const CardDescription = ShadcnCardDescription

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <ShadcnCardContent
    ref={ref}
    className={className}
    {...props}
  />
))
CardContent.displayName = "CardContent"

const CardFooter = ShadcnCardFooter

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent }
