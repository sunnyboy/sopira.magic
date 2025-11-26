import React from 'react'

interface BaseComponentProps {
  children?: React.ReactNode
  className?: string
}

export default function BaseComponent({ children, className }: BaseComponentProps) {
  return <div className={className}>{children}</div>
}

