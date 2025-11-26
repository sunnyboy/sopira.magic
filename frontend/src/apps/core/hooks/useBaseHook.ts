import { useState } from 'react'

export default function useBaseHook() {
  const [state, setState] = useState(null)
  return { state, setState }
}

