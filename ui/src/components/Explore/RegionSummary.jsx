/* eslint-disable camelcase */

import React, { useEffect, useRef } from 'react'
import PropTypes from 'prop-types'
import { AngleDoubleRight } from '@emotion-icons/fa-solid'
import { Box, Flex, Paragraph, Divider, Text } from 'theme-ui'

import { MAP_SERVICES, barrierTypeLabels } from 'config'
import { Downloader } from 'components/Download'
import { Link, OutboundLink } from 'components/Link'
import { UnitSearch } from 'components/UnitSearch'
import { formatNumber } from 'util/format'

const Summary = ({
  barrierType,
  region,
  url,
  urlLabel,
  name,
  dams,
  reconDams,
  rankedDams,
  removedDams,
  removedDamsGainMiles,
  totalSmallBarriers,
  smallBarriers,
  rankedSmallBarriers,
  removedSmallBarriers,
  removedSmallBarriersGainMiles,
  unsurveyedRoadCrossings,
  system,
  onSelectUnit,
}) => {
  const contentNodeRef = useRef(null)

  useEffect(() => {
    // force scroll to top on change
    if (contentNodeRef.current !== null) {
      contentNodeRef.current.scrollTo(0, 0)
    }
  }, [])

  const unrankedDams = dams - rankedDams
  const unrankedBarriers = smallBarriers - rankedSmallBarriers
  const totalRoadBarriers = totalSmallBarriers + unsurveyedRoadCrossings

  return (
    <Flex sx={{ flexDirection: 'column', height: '100%' }}>
      <Box
        ref={contentNodeRef}
        sx={{
          pt: '0.5rem',
          pb: '1rem',
          px: '1rem',
          flex: '1 1 auto',
          overflowY: 'auto',
          height: '100%',
        }}
      >
        {url ? (
          <Box sx={{ mb: '1rem' }}>
            <Link to={url}>
              {urlLabel} <AngleDoubleRight size="1em" />
            </Link>
          </Box>
        ) : null}

        <Paragraph sx={{ fontSize: [3, 4] }}>
          Across {name}, there are:
        </Paragraph>

        {barrierType === 'dams' || barrierType === 'combined_barriers' ? (
          <>
            <Paragraph sx={{ mt: '0.5rem' }}>
              <b>{formatNumber(dams, 0)}</b> inventoried dams, including:
            </Paragraph>
            <Box as="ul" sx={{ mt: '0.5rem', fontSize: 2 }}>
              <li>
                <b>{formatNumber(reconDams)}</b> that have been reconned for
                social feasibility of removal
              </li>
              <li>
                <b>{formatNumber(rankedDams, 0)}</b> that have been analyzed for
                their impacts to aquatic connectivity in this tool
              </li>
              {removedDams > 0 ? (
                <li>
                  <b>{formatNumber(removedDams, 0)}</b> that have been removed
                  or mitigated, gaining{' '}
                  <b>{formatNumber(removedDamsGainMiles)} miles</b> of
                  reconnected rivers and streams
                </li>
              ) : null}
            </Box>
          </>
        ) : null}

        {barrierType === 'small_barriers' ||
        barrierType === 'combined_barriers' ? (
          <>
            <Paragraph
              sx={{
                mt: barrierType === 'combined_barriers' ? '1.5rem' : '0.5rem',
              }}
            >
              <b>{formatNumber(totalRoadBarriers, 0)}</b> or more road/stream
              crossings (potential aquatic barriers), including:
            </Paragraph>
            <Box as="ul" sx={{ mt: '0.5rem', fontSize: 2 }}>
              <li>
                <b>
                  {formatNumber(totalSmallBarriers - removedSmallBarriers, 0)}
                </b>{' '}
                that have been assessed for impacts to aquatic organisms
              </li>
              <li>
                <b>{formatNumber(smallBarriers - removedSmallBarriers, 0)}</b>{' '}
                that have been assessed so far that are likely to impact aquatic
                organisms
              </li>
              <li>
                <b>{formatNumber(rankedSmallBarriers, 0)}</b> that have been
                analyzed for their impacts to aquatic connectivity in this tool
              </li>
              {removedSmallBarriers > 0 ? (
                <li>
                  <b>{formatNumber(removedSmallBarriers, 0)}</b> that have been
                  removed or mitigated, gaining{' '}
                  <b>{formatNumber(removedSmallBarriersGainMiles)} miles</b> of
                  reconnected rivers and streams
                </li>
              ) : null}
              <li>
                <b>{formatNumber(unsurveyedRoadCrossings, 0)}</b> unsurveyed
                road/stream crossings
              </li>
            </Box>
          </>
        ) : null}

        <Divider
          sx={{
            borderBottom: '2px solid',
            borderBottomColor: 'grey.3',
            mt: '1.5rem',
            mb: '2rem',
          }}
        />

        <Text
          variant="help"
          sx={{
            mt: '0.5rem',
            pb: '1.5rem',
          }}
        >
          Select {system === 'ADM' ? 'states / counties' : 'hydrologic units'}{' '}
          by clicking on them on the map or searching by name. You can then
          download data for all selected areas.
        </Text>

        <UnitSearch
          barrierType={barrierType}
          system={system}
          onSelect={onSelectUnit}
        />

        <Divider
          sx={{
            borderBottom: '2px solid',
            borderBottomColor: 'grey.3',
            mt: '3rem',
          }}
        />

        {barrierType === 'dams' ? (
          <Paragraph variant="help" sx={{ mt: '3rem' }}>
            Note: These statistics are based on <i>inventoried</i> dams. Because
            the inventory is incomplete in many areas, areas with a high number
            of dams may simply represent areas that have a more complete
            inventory.
            <br />
            <br />
            {formatNumber(unrankedDams, 0)} dams were not analyzed because they
            could not be correctly located on the aquatic network or were
            otherwise excluded from the analysis.
          </Paragraph>
        ) : null}

        {barrierType === 'small_barriers' ? (
          <Paragraph variant="help" sx={{ mt: '3rem' }}>
            Note: These statistics are based on <i>inventoried</i> road-related
            barriers. Because the inventory is incomplete in many areas, areas
            with a high number of road-related barriers may simply represent
            areas that have a more complete inventory.
            <br />
            <br />
            {formatNumber(unrankedBarriers, 0)} road-related barriers could not
            be correctly located on the aquatic network or were otherwise
            excluded from the analysis.
          </Paragraph>
        ) : null}

        {barrierType === 'combined_barriers' ? (
          <Paragraph variant="help" sx={{ mt: '3rem' }}>
            Note: These statistics are based on <i>inventoried</i> dams and
            road-related barriers. Because the inventory is incomplete in many
            areas, areas with a high number of dams or road-related barriers may
            simply represent areas that have a more complete inventory.
            <br />
            <br />
            {formatNumber(unrankedDams, 0)} dams and{' '}
            {formatNumber(unrankedBarriers, 0)} road-related barriers could not
            be correctly located on the aquatic network or were otherwise
            excluded from the analysis.
          </Paragraph>
        ) : null}

        {!region ? (
          <Box sx={{ mt: '2rem' }}>
            To access an ArcGIS map service of a recent version of these
            barriers and associated connectivity results,{' '}
            <OutboundLink to={MAP_SERVICES[barrierType]}>
              click here
            </OutboundLink>
            .
            <Text variant="help">
              Note: may not match the exact version available for download in
              this tool
            </Text>
          </Box>
        ) : null}
      </Box>

      {!region ? (
        <Flex
          sx={{
            flex: '0 0 auto',
            alignItems: 'center',
            // justifyContent: 'space-between',
            gap: '1rem',
            pt: '0.5rem',
            px: '1rem',
            pb: '1rem',
            borderTop: '1px solid #DDD',
            bg: '#f6f6f2',
            '& button': {
              fontSize: 1,
              textAlign: 'left',
              p: '0.5rem',
            },
          }}
        >
          <Text sx={{ lineHeight: 1, flex: '1 1 auto' }}>Download:</Text>

          <Box sx={{ flex: '0 0 auto' }}>
            <Downloader
              barrierType={barrierType}
              label={barrierTypeLabels[barrierType]}
              showOptions={false}
              includeUnranked
            />
          </Box>
        </Flex>
      ) : null}
    </Flex>
  )
}

Summary.propTypes = {
  region: PropTypes.string,
  url: PropTypes.string,
  urlLabel: PropTypes.string,
  name: PropTypes.string.isRequired,
  barrierType: PropTypes.string.isRequired,
  dams: PropTypes.number,
  reconDams: PropTypes.number,
  rankedDams: PropTypes.number,
  removedDams: PropTypes.number,
  removedDamsGainMiles: PropTypes.number,
  totalSmallBarriers: PropTypes.number,
  smallBarriers: PropTypes.number,
  rankedSmallBarriers: PropTypes.number,
  removedSmallBarriers: PropTypes.number,
  removedSmallBarriersGainMiles: PropTypes.number,
  unsurveyedRoadCrossings: PropTypes.number,
  system: PropTypes.string.isRequired,
  onSelectUnit: PropTypes.func.isRequired,
}

Summary.defaultProps = {
  region: null,
  url: null,
  urlLabel: null,
  dams: 0,
  reconDams: 0,
  rankedDams: 0,
  removedDams: 0,
  removedDamsGainMiles: 0,
  totalSmallBarriers: 0,
  smallBarriers: 0,
  rankedSmallBarriers: 0,
  removedSmallBarriers: 0,
  removedSmallBarriersGainMiles: 0,
  unsurveyedRoadCrossings: 0,
}

export default Summary
