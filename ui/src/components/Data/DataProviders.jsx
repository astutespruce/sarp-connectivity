import React from 'react'
import PropTypes from 'prop-types'

import { Box, Grid, Image } from 'theme-ui'

import { dynamicallyLoadImage } from 'util/dom'

const DataProviders = ({ dataProviders }) =>
  dataProviders.map(({ key, description, logo, logoWidth }) => (
    <Grid
      key={key}
      columns="2fr 1fr"
      gap={5}
      sx={{
        '&:not(:first-of-type)': {
          mt: '2rem',
        },
      }}
    >
      <Box sx={{ fontSize: [2, 3] }}>
        <div dangerouslySetInnerHTML={{ __html: description }} />
      </Box>
      {logo ? (
        <Box sx={{ maxWidth: logoWidth }}>
          <Image src={dynamicallyLoadImage(logo)} />
        </Box>
      ) : null}
    </Grid>
  ))

DataProviders.propTypes = {
  dataProviders: PropTypes.arrayOf(
    PropTypes.shape({
      key: PropTypes.string.isRequired,
      description: PropTypes.string.isRequired,
      logo: PropTypes.string.isRequired,
      logoWidth: PropTypes.string.isRequired,
    })
  ),
}

export default DataProviders
