import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap text-sm font-medium transition-all duration-150 disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default: "rounded-[10px] border border-primary/20 bg-card text-card-foreground shadow-sm hover:-translate-y-px hover:shadow-md hover:bg-primary/10 hover:border-primary/40",
        solid: "rounded-[10px] border-0 bg-primary text-primary-foreground shadow-lg shadow-primary/30 hover:opacity-90 hover:-translate-y-px hover:shadow-xl hover:shadow-primary/40",
        danger: "rounded-[10px] border-0 bg-destructive text-destructive-foreground shadow-lg shadow-destructive/30 hover:opacity-90 hover:-translate-y-px hover:shadow-xl hover:shadow-destructive/40",
        ghost: "hover:bg-accent hover:text-accent-foreground",
      },
      size: {
        default: "px-3 py-2",
        sm: "px-2 py-1 text-xs",
        lg: "px-4 py-3",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
