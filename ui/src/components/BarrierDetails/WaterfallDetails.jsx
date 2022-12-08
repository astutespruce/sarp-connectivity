import React from 'react'
import PropTypes from 'prop-types'
import { Box, Paragraph, Text } from 'theme-ui'

import { Entry, Field, Section } from 'components/Sidebar'
import { isEmptyString } from 'util/string'

import IDInfo from './IDInfo'
import LocationInfo from './LocationInfo'
import NetworkInfo from './NetworkInfo'
import SpeciesInfo from './SpeciesInfo'

const WaterfallDetails = ({
  barrierType,
  source,
  hasnetwork,
  excluded,
  stream,
  intermittent,
  HUC12,
  HUC8Name,
  HUC12Name,
  falltype,
  tespp,
  statesgcnspp,
  regionalsgcnspp,
  trout,
  salmonidesu,
  // metrics
  totalupstreammiles,
  perennialupstreammiles,
  alteredupstreammiles,
  unalteredupstreammiles,
  freedownstreammiles,
  freeperennialdownstreammiles,
  freealtereddownstreammiles,
  freeunaltereddownstreammiles,
  landcover,
  sizeclasses,
}) => (
  <Box
    sx={{
      mt: '-1rem',
      mx: '-0.5rem',
    }}
  >
    <Section title="Location">
      <LocationInfo
        reachName={stream}
        HUC8Name={HUC8Name}
        HUC12Name={HUC12Name}
        HUC12={HUC12}
      />

      {falltype && !isEmptyString(falltype) ? (
        <Entry>
          <Field label="Waterfall type">{falltype}</Field>
        </Entry>
      ) : null}
    </Section>

    <Section title="Functional network information">
      {hasnetwork ? (
        <NetworkInfo
          barrierType={barrierType}
          totalupstreammiles={totalupstreammiles}
          perennialupstreammiles={perennialupstreammiles}
          alteredupstreammiles={alteredupstreammiles}
          unalteredupstreammiles={unalteredupstreammiles}
          freedownstreammiles={freedownstreammiles}
          freeperennialdownstreammiles={freeperennialdownstreammiles}
          freealtereddownstreammiles={freealtereddownstreammiles}
          freeunaltereddownstreammiles={freeunaltereddownstreammiles}
          sizeclasses={sizeclasses}
          landcover={landcover}
          intermittent={intermittent}
        />
      ) : (
        <>
          {excluded ? (
            <Entry>
              This waterfall was excluded from the connectivity analysis based
              on field reconnaissance or manual review of aerial imagery.
            </Entry>
          ) : (
            <Entry>
              <Text>
                This waterfall is off-network and has no functional network
                information.
              </Text>
              <Paragraph variant="help" sx={{ mt: '1rem' }}>
                Not all barriers could be correctly snapped to the aquatic
                network for analysis. Please contact us to report an error or
                for assistance interpreting these results.
              </Paragraph>
            </Entry>
          )}
        </>
      )}
    </Section>

    <Section title="Species information for this subwatershed">
      <SpeciesInfo
        barrierType={barrierType}
        tespp={tespp}
        regionalsgcnspp={regionalsgcnspp}
        statesgcnspp={statesgcnspp}
        trout={trout}
        salmonidesu={salmonidesu}
      />
    </Section>

    {!isEmptyString(source) ? (
      <Section title="Other information">
        <IDInfo source={source} />
      </Section>
    ) : null}
  </Box>
)

WaterfallDetails.propTypes = {
  barrierType: PropTypes.string.isRequired,
  hasnetwork: PropTypes.number.isRequired,
  excluded: PropTypes.number,
  source: PropTypes.string,
  stream: PropTypes.string,
  intermittent: PropTypes.number,
  HUC12: PropTypes.string,
  HUC8Name: PropTypes.string,
  HUC12Name: PropTypes.string,
  falltype: PropTypes.string,
  tespp: PropTypes.number,
  statesgcnspp: PropTypes.number,
  regionalsgcnspp: PropTypes.number,
  trout: PropTypes.number,
  salmonidesu: PropTypes.string,
  totalupstreammiles: PropTypes.number,
  perennialupstreammiles: PropTypes.number,
  alteredupstreammiles: PropTypes.number,
  unalteredupstreammiles: PropTypes.number,
  freedownstreammiles: PropTypes.number,
  freeperennialdownstreammiles: PropTypes.number,
  freealtereddownstreammiles: PropTypes.number,
  freeunaltereddownstreammiles: PropTypes.number,
  landcover: PropTypes.number,
  sizeclasses: PropTypes.number,
}

WaterfallDetails.defaultProps = {
  HUC12: null,
  HUC8Name: null,
  HUC12Name: null,
  excluded: 0,
  source: null,
  stream: null,
  intermittent: -1,
  falltype: null,
  tespp: 0,
  statesgcnspp: 0,
  regionalsgcnspp: 0,
  trout: 0,
  salmonidesu: null,
  totalupstreammiles: 0,
  perennialupstreammiles: 0,
  alteredupstreammiles: 0,
  unalteredupstreammiles: 0,
  freedownstreammiles: 0,
  freeperennialdownstreammiles: 0,
  freealtereddownstreammiles: 0,
  freeunaltereddownstreammiles: 0,
  landcover: null,
  sizeclasses: null,
}

export default WaterfallDetails
