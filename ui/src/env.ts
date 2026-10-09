import { defineEnvVars } from '@sveltejs/kit/env'

export const variables = defineEnvVars({
	SENTRY_DSN: { public: true, static: true },
	GOOGLE_ANALYTICS_ID: { public: true, static: true },
	MAPBOX_API_TOKEN: { public: true, static: true },
	DEPLOY_ENV: { public: true, static: true },
	CONTACT_EMAIL: { public: true, static: true },
	NACC_HOME_URL: { public: true, static: true },
	MAILCHIMP_URL: { public: true, static: true },
	MAILCHIMP_USER_ID: { public: true, static: true },
	MAILCHIMP_FORM_ID: { public: true, static: true },
	MAILCHIMP_FORM_ID2: { public: true, static: true }
})
