import * as env from '$env/static/public'

export const SENTRY_DSN = env.PUBLIC_SENTRY_DSN || ''
export const GOOGLE_ANALYTICS_ID = env.PUBLIC_GOOGLE_ANALYTICS_ID || ''
export const CONTACT_EMAIL = env.PUBLIC_CONTACT_EMAIL || ''
export const DEPLOY_ENV = env.PUBLIC_DEPLOY_ENV || 'local'
export const NACC_HOME_URL = env.PUBLIC_NACC_URL || 'https://aquaticbarriers.org'

export const API_HOST = env.PUBLIC_API_HOST || ''

export const SITE_NAME = 'National Aquatic Barrier Inventory & Prioritization Tool'
