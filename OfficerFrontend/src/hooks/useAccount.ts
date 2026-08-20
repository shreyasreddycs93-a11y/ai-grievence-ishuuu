import { useEffect, useState } from 'react'
import { getMe, getToken, ApiError } from '../api/client'
import type { Account } from '../api/types'

// Loads the logged-in officer's profile via GET /auth/me using the token the
// Landing app wrote to localStorage. No token, or a rejected/expired one,
// sends the visitor back to Landing to sign in.
export function useAccount(): { account: Account | null; loading: boolean } {
  const [account, setAccount] = useState<Account | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!getToken()) {
      window.location.href = '/'
      return
    }
    getMe()
      .then(setAccount)
      .catch((err: unknown) => {
        if (err instanceof ApiError && err.status === 401) {
          window.location.href = '/'
        }
      })
      .finally(() => setLoading(false))
  }, [])

  return { account, loading }
}
