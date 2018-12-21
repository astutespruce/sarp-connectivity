const currentHost = `${window.location.protocol}//${window.location.host}`

export const TILE_HOST = process.env.NODE_ENV === "production" ? currentHost : "http://localhost:8000"

export const API_HOST = process.env.NODE_ENV === "production" ? currentHost : "http://localhost:5000"
