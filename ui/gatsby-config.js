// load appropriate dotenv file
require('dotenv').config({
  path: `.env.${process.env.NODE_ENV}`,
})
const { version, date } = require('./package.json')

const defaultHost = `https://connectivity.sarpdata.com`

module.exports = {
  siteMetadata: {
    version,
    date,
    siteUrl: process.env.GATSBY_SITE_URL || defaultHost,
    title: `Southeast Aquatic Barrier Prioritization Tool`,
    shortTitle: `Southeast Aquatic Barrier Tool`,
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
    `gatsby-plugin-react-helmet`,
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
    {
      resolve: `gatsby-plugin-styled-components`,
      options: {
        displayName: process.env.NODE_ENV !== `production`,
        fileName: false,
      },
    },
    {
      resolve: `gatsby-plugin-typography`,
      options: {
        pathToConfigModule: `./config/typography.js`,
      },
    },
    `gatsby-plugin-catch-links`,
    `gatsby-plugin-sitemap`,
  ],
}
