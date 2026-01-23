import type { NextApiRequest, NextApiResponse } from "next"
import crypto from "crypto"

interface HmacRequest extends NextApiRequest {
  query: {
    userId: string
  }
}

type ResponseData = {
  hmac: string
}

export default function handler(
  req: HmacRequest,
  res: NextApiResponse<ResponseData>
) {
  const { userId } = req.query

  if (!userId) {
    res.status(400).json({ hmac: "" })
    return
  }

  const apiSecret = process.env.MAGICBELL_API_SECRET

  if (!apiSecret) {
    res.status(500).json({ hmac: "" })
    return
  }

  const hmac = crypto
    .createHmac("sha256", apiSecret)
    .update(userId)
    .digest("base64")

  res.status(200).json({ hmac })
}
