import "@/styles/globals.css"
import type { AppProps } from "next/app"
import { Analytics } from "@vercel/analytics/react"
import { MagicBellProvider } from "@magicbell/react-headless"
import { SubscriptionManager } from "@/services/subscriptionManager"
import { DeviceInfoProvider } from "@/hooks/useDeviceInfo"
import { useEffect, useState } from "react"

export default function App({ Component, pageProps }: AppProps) {
  const [userHmac, setUserHmac] = useState<string | null>(null)
  const userId = SubscriptionManager.getOrSetUserId()

  useEffect(() => {
    async function fetchHmac() {
      try {
        const response = await fetch(`/api/hmac?userId=${encodeURIComponent(userId)}`)
        const data = await response.json()
        setUserHmac(data.hmac)
      } catch (error) {
        console.error("Failed to fetch HMAC:", error)
      }
    }
    fetchHmac()
  }, [userId])

  if (!userHmac) {
    return <div>Loading...</div>
  }

  return (
    <>
      <MagicBellProvider
        apiKey={process.env.NEXT_PUBLIC_MAGICBELL_API_KEY}
        userExternalId={userId}
        userKey={userHmac}
      >
        <DeviceInfoProvider>
          <Component {...pageProps} />
        </DeviceInfoProvider>
      </MagicBellProvider>
      <Analytics />
    </>
  )
}
