// load appropriate dotenv file
require('dotenv').config({
  path: `.env.${process.env.NODE_ENV}`,
})

const theme = require('./src/theme')
const { version, date } = require('./package.json')

const defaultHost = `https://aquaticbarriers.org`

module.exports = {
  siteMetadata: {
    version,
    date,
    siteUrl: process.env.GATSBY_SITE_URL || defaultHost,
    title: `National Aquatic Barrier Inventory & Prioritization Tool`,
    shortTitle: `Aquatic Barrier Tool`,
    description: `A tool to help prioritize aquatic barriers for removal or mitigation.`,
    author: `Brendan C. Ward`,
    googleAnalyticsId: process.env.GATSBY_GOOGLE_ANALYTICS_ID,
    sentryDSN: process.env.GATSBY_SENTRY_DSN,
    mapboxToken: process.env.GATSBY_MAPBOX_API_TOKEN,
    apiHost: process.env.GATSBY_API_HOST || defaultHost,
    tileHost: process.env.GATSBY_TILE_HOST || defaultHost,
    mailchimpConfig: {
      formURL: process.env.GATSBY_MAILCHIMP_URL,
      userID: process.env.GATSBY_MAILCHIMP_USER_ID,
      formID: process.env.GATSBY_MAILCHIMP_FORM_ID,
    },
  },
  flags: {
    FAST_DEV: true,
    DEV_SSR: true,
    PARALLEL_SOURCING: false, // uses a lot of memory on server, so disable
  },
  plugins: [
    {
      resolve: `gatsby-plugin-google-gtag`,
      options: {
        trackingIds: [process.env.GATSBY_GOOGLE_ANALYTICS_ID],
        gtagConfig: {
          anonymize_ip: true,
        },
        pluginConfig: {
          head: true,
          respectDNT: true,
        },
      },
    },
    {
      resolve: `gatsby-plugin-theme-ui`,
      options: {
        injectColorFlashScript: false,
        preset: theme,
      },
    },
    `gatsby-plugin-image`,
    `gatsby-transformer-sharp`,
    `gatsby-plugin-sharp`,
    {
      resolve: `gatsby-source-filesystem`,
      options: {
        name: `images`,
        path: `${__dirname}/src/images/`,
      },
    },
    {
      resolve: `gatsby-source-filesystem`,
      options: {
        name: `data`,
        path: `${__dirname}/data`,
      },
    },
    {
      resolve: `gatsby-transformer-json`,
      options: {
        // name the top-level type after the filename
        typeName: ({ node }) => `${node.name}Json`,
      },
    },
    `gatsby-plugin-catch-links`,
    `gatsby-plugin-sitemap`,
    {
      resolve: 'gatsby-plugin-robots-txt',
      options: {
        host: process.env.GATSBY_SITE_URL || `https://localhost`,
        policy: [{ userAgent: '*', disallow: ['/services', '*/api/*'] }],
      },
    },
    {
      resolve: `gatsby-plugin-manifest`,
      options: {
        name: `National Aquatic Barrier Inventory & Prioritization Tool`,
        short_name: `Aquatic Barrier Tool`,
        icon: 'src/images/favicon-64x64.svg',
        start_url: `/`,
        background_color: `#1891ac`,
        theme_color: `#1891ac`,
        display: `minimal-ui`,
      },
    },
  ],
}
