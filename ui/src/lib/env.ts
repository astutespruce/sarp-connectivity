import { browser } from '$app/env'
export * from '$app/env/public'

export const HOST_URL = browser ? `${window.location.protocol}//${window.location.host}` : ''
export const API_URL = `${HOST_URL}/api/v1/internal`
export const TILES_URL = `${HOST_URL}/tiles`
