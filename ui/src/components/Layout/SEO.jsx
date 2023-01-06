import React from 'react'
import PropTypes from 'prop-types'
import { useStaticQuery, graphql, withPrefix } from 'gatsby'

function SEO({ title: rawTitle }) {
  const {
    site: {
      siteMetadata: { title: siteTitle, description, author },
    },
  } = useStaticQuery(
    graphql`
      query {
        site {
          siteMetadata {
            title
            description
            author
          }
        }
      }
    `
  )

  const title = rawTitle ? `${rawTitle} | ${siteTitle}` : siteTitle

  return (
    <>
      <title>{title}</title>
      <meta
        name="viewport"
        content="width=device-width, initial-scale=1, shrink-to-fit=no"
      />
      <meta name="lang" content="en" />
      <meta name="description" content={description} />
      <meta name="og:title" content={title} />
      <meta name="og:description" content={description} />
      <meta name="og:type" content="website" />
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:card" content="summary" />
      <meta name="twitter:creator" content={author} />
      <link rel="icon" type="image/png" href={withPrefix('/favicon.ico')} />
      <link
        rel="icon"
        type="image/svg+xml"
        href={withPrefix('/favicon-64x64.svg')}
      />
      <link
        rel="icon"
        type="image/png"
        sizes="16x16"
        href={withPrefix('/favicon-16x16.png')}
      />
      <link
        rel="icon"
        type="image/png"
        sizes="32x32"
        href={withPrefix('/favicon-32x32.png')}
      />
      <link
        rel="icon"
        type="image/png"
        sizes="64x64"
        href={withPrefix('/favicon-64x64.png')}
      />

      {/* Have to set HTML height manually for mobile browsers */}
      <style>{`html {height: 100%; width: 100%; margin: 0;}`}</style>
    </>
  )
}

SEO.propTypes = {
  title: PropTypes.string,
}

SEO.defaultProps = {
  title: null,
}

export default SEO
