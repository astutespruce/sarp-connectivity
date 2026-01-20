import * as env from '$env/static/public'

export const MAPBOX_TOKEN = env.PUBLIC_MAPBOX_API_TOKEN
export const SENTRY_DSN = env.PUBLIC_SENTRY_DSN || ''
export const GOOGLE_ANALYTICS_ID = env.PUBLIC_GOOGLE_ANALYTICS_ID || ''
export const CONTACT_EMAIL = env.PUBLIC_CONTACT_EMAIL || ''
export const DEPLOY_ENV = env.PUBLIC_DEPLOY_ENV || 'local'
export const NACC_HOME_URL = env.PUBLIC_NACC_URL || 'https://aquaticbarriers.org'

export const API_HOST = env.PUBLIC_API_HOST || ''
export const TILE_HOST = env.PUBLIC_TILE_HOST || ''

export const SITE_NAME = 'National Aquatic Barrier Inventory & Prioritization Tool'
export const SITE_URL = env.PUBLIC_SITE_URL || 'https://tool.aquaticbarriers.org'

// Mailchimp form used for submitting user info for download
export const MAILCHIMP_FORM = {
	url: env.PUBLIC_MAILCHIMP_URL,
	userId: env.PUBLIC_MAILCHIMP_USER_ID,
	formId1: env.PUBLIC_MAILCHIMP_FORM_ID,
	formId2: env.PUBLIC_MAILCHIMP_FORM_ID2
}
