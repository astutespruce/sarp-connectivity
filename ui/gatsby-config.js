// load appropriate dotenv file
require('dotenv').config({
  path: `.env.${process.env.NODE_ENV}`,
})

const theme = require('./src/theme')

const { version, date } = require('./package.json')

const defaultHost = `https://connectivity.sarpdata.com`

module.exports = {
  siteMetadata: {
    version,
    date,
    siteUrl: process.env.GATSBY_SITE_URL || defaultHost,
    title: `Aquatic Barrier Prioritization Tool`,
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
    DEV_SSR: false, // appears to throw '"filePath" is not allowed to be empty' when true
    PARALLEL_SOURCING: false, // process.env.NODE_ENV !== `production`, // uses a lot of memory on server
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
    `gatsby-plugin-react-helmet`,
    `gatsby-plugin-image`,
    `gatsby-transformer-sharp`,
    `gatsby-plugin-sharp`,
    {
      resolve: `gatsby-plugin-create-client-paths`,
      options: {
        prefixes: [`/report/*`],
      },
    },
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
  ],
}
