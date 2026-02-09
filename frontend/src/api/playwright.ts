import request from './request'

export interface PlaywrightSession {
  session_id: string
  websocket_url: string
  expires_in: number
}

export const startPlaywrightSession = async (platform: string) => {
  const response = await request.post(`/oauth/authorize/start`, { platform })
  return response.data
}

export const getPlaywrightStatus = async (platform: string) => {
  const response = await request.get(`/oauth/authorize/status`, { params: { platform } })
  return response.data
}

export const completePlaywrightAuth = async (platform: string, account_name?: string) => {
  const response = await request.post(`/oauth/authorize/complete`, null, { 
    params: { platform, account_name } 
  })
  return response.data
}

export const executePlaywrightCommand = async (
  session_id: string,
  command: string,
  params: Record<string, any> = {}
) => {
  return {
    command,
    params,
    session_id
  }
}
