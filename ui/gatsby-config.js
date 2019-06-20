const googleAnalyticsId = `UA-XXXXX`

module.exports = {
  siteMetadata: {
    siteUrl: `https://connectivity.sarpdata.com/`,
    title: `Southeast Aquatic Barrier Prioritization Tool`,
    shortTitle: `Southeast Aquatic Barrier Tool`,
    description: `A tool to help prioritize aquatic barriers for removal or mitigation.`,
    author: `Brendan C. Ward`,
    googleAnalyticsId,
    mapboxToken:
      'pk.eyJ1IjoiYmN3YXJkIiwiYSI6InJ5NzUxQzAifQ.CVyzbyOpnStfYUQ_6r8AgQ',
  },
  plugins: [
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
    {
      resolve: `gatsby-plugin-google-analytics`,
      options: {
        trackingId: googleAnalyticsId,
        anonymize: true,
      },
    },
  ],
}
