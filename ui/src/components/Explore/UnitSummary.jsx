/* eslint-disable camelcase */
import React, { useRef, useEffect } from 'react'
import PropTypes from 'prop-types'
import { Box, Button, Heading, Flex, Text, Paragraph } from 'theme-ui'
import { AngleDoubleRight } from '@emotion-icons/fa-solid'

import { Link } from 'components/Link'
import { Downloader } from 'components/Download'
import { UnitSearch } from 'components/UnitSearch'
import { STATE_FIPS, STATES, barrierTypeLabels } from 'config'
import { formatNumber, pluralize } from 'util/format'

import UnitListItem from './UnitListItem'
import { layers } from './layers'

const UnitSummary = ({
  barrierType,
  system,
  summaryUnits,
  onSelectUnit,
  onReset,
}) => {
  const contentNodeRef = useRef(null)

  useEffect(() => {
    // force scroll to top on change
    if (contentNodeRef.current !== null) {
      contentNodeRef.current.scrollTo(0, 0)
    }
  }, [])

  const [{ id, name = '', layer }] = summaryUnits

  let dams = 0
  let rankedDams = 0
  let removedDams = 0
  let removedDamsGainMiles = 0
  let smallBarriers = 0
  let totalSmallBarriers = 0
  let rankedSmallBarriers = 0
  let removedSmallBarriers = 0
  let removedSmallBarriersGainMiles = 0
  let totalRoadCrossings = 0
  let unsurveyedRoadCrossings = 0

  // ignore any unit that is contained within another unit
  const ignoreIds = new Set()

  let title = null
  let subtitle = null
  let idline = null
  if (summaryUnits.length === 1) {
    switch (layer) {
      case 'State': {
        title = STATES[id]
        break
      }
      case 'County': {
        title = name
        subtitle = STATE_FIPS[id.slice(0, 2)]
        break
      }
      case 'HUC2': {
        title = name
        idline = `${layer}: ${id}`
        break
      }
      default: {
        // all remaining HUC cases
        title = name
        const [{ title: layerTitle }] = layers.filter(
          ({ id: lyrID }) => lyrID === layer
        )
        subtitle = layerTitle
        idline = `${layer}: ${id}`
        break
      }
    }
  } else {
    title = 'Statistics for selected areas'

    if (system === 'ADM') {
      const statesPresent = new Set(
        summaryUnits
          .filter(({ layer: l }) => l === 'State')
          .map(({ id: i }) => STATES[i])
      )
      summaryUnits
        .filter(({ layer: l }) => l === 'County')
        .forEach(({ id: i }) => {
          const state = STATE_FIPS[i.slice(0, 2)]
          if (statesPresent.has(state)) {
            ignoreIds.add(i)
          }
        })
    } else {
      const hucsPresent = new Set(summaryUnits.map(({ id: huc }) => huc))
      const ids = [...hucsPresent]
      ids.forEach((parentHuc) => {
        ids.forEach((childHuc) => {
          if (parentHuc !== childHuc && childHuc.startsWith(parentHuc)) {
            ignoreIds.add(childHuc)
          }
        })
      })
    }
  }

  // aggregate statistics
  summaryUnits
    .filter(({ id: i }) => !ignoreIds.has(i))
    .forEach(
      ({
        dams: curDams = 0,
        rankedDams: curRankedDams = 0,
        removedDams: curRemovedDams = 0,
        removedDamsGainMiles: curRemovedDamsGainMiles = 0,
        smallBarriers: curSmallBarriers = 0,
        totalSmallBarriers: curTotalSmallBarriers = 0,
        rankedSmallBarriers: curRankedSmallBarriers = 0,
        removedSmallBarriers: curRemovedSmallBarriers = 0,
        removedSmallBarriersGainMiles: curRemovedSmallBarriersGainMiles = 0,
        totalRoadCrossings: curRoadCrossings = 0,
        unsurveyedRoadCrossings: curUnsurveyedCrossings = 0,
      }) => {
        dams += curDams
        rankedDams += curRankedDams
        removedDams += curRemovedDams
        removedDamsGainMiles += curRemovedDamsGainMiles
        smallBarriers += curSmallBarriers
        totalSmallBarriers += curTotalSmallBarriers
        rankedSmallBarriers += curRankedSmallBarriers
        removedSmallBarriers += curRemovedSmallBarriers
        removedSmallBarriersGainMiles += curRemovedSmallBarriersGainMiles
        totalRoadCrossings += curRoadCrossings
        unsurveyedRoadCrossings += curUnsurveyedCrossings
      }
    )

  const unrankedDams = dams - rankedDams
  const unrankedBarriers = smallBarriers - rankedSmallBarriers
  const totalRoadBarriers = totalSmallBarriers + unsurveyedRoadCrossings

  const summaryUnitsForDownload = summaryUnits.reduce(
    (prev, { layer: l, id: i }) =>
      Object.assign(prev, {
        [l]: prev[l] ? prev[l].concat([i]) : [i],
      }),
    {}
  )

  const downloaderConfig = {
    // aggregate summary unit ids to list per summary unit layer
    summaryUnits: summaryUnitsForDownload,
    scenario: 'ncwc',
  }

  let downloadButtons = null

  switch (barrierType) {
    case 'dams': {
      downloadButtons = (
        <Box sx={{ width: '10rem' }}>
          <Flex sx={{ ml: '1rem', flex: '1 1 auto' }}>
            <Downloader
              barrierType="dams"
              label={barrierTypeLabels.dams}
              config={downloaderConfig}
              disabled={dams === 0}
              showOptions={false}
              includeUnranked
            />
          </Flex>
        </Box>
      )

      break
    }
    case 'small_barriers': {
      downloadButtons = (
        <Flex sx={{ justifyContent: 'space-between', gap: '1rem' }}>
          <Downloader
            barrierType="small_barriers"
            label={barrierTypeLabels.small_barriers}
            config={downloaderConfig}
            disabled={totalSmallBarriers === 0}
            showOptions={false}
            includeUnranked
          />

          <Downloader
            barrierType="road_crossings"
            label={barrierTypeLabels.road_crossings}
            config={{
              summaryUnits: summaryUnitsForDownload,
            }}
            disabled={totalRoadCrossings === 0}
            showOptions={false}
            includeUnranked
          />
        </Flex>
      )
      break
    }
    case 'combined_barriers': {
      downloadButtons = (
        <Flex sx={{ justifyContent: 'space-between', gap: '1rem' }}>
          <Downloader
            barrierType="dams"
            label={barrierTypeLabels.dams}
            config={downloaderConfig}
            disabled={dams === 0}
            showOptions={false}
            includeUnranked
          />
          <Downloader
            barrierType="small_barriers"
            label={barrierTypeLabels.small_barriers}
            config={downloaderConfig}
            disabled={totalSmallBarriers === 0}
            showOptions={false}
            includeUnranked
          />
        </Flex>
      )
      break
    }
    default: {
      break
    }
  }

  return (
    <Flex sx={{ flexDirection: 'column', height: '100%' }}>
      <Flex
        sx={{
          py: '1rem',
          pl: '1rem',
          pr: '0.5rem',
          justifyContent: 'center',
          alignItems: 'flex-start',
          borderBottom: '1px solid #DDD',
          bg: '#f6f6f2',
          lineHeight: 1.2,
        }}
      >
        <Box sx={{ flex: '1 1 auto' }}>
          <Heading as="h3" sx={{ m: 0, fontSize: '1.25rem' }}>
            {title}
          </Heading>
          {subtitle ? (
            <Text sx={{ fontSize: '1.25rem' }}>{subtitle}</Text>
          ) : null}
          {idline ? <Text sx={{ color: 'grey.7' }}>{idline}</Text> : null}
        </Box>

        <Button variant="close" onClick={onReset}>
          &#10006;
        </Button>
      </Flex>
      <Box
        ref={contentNodeRef}
        sx={{
          p: '1rem',
          flex: '1 1 auto',
          height: '100%',
          overflowY: 'auto',
        }}
      >
        {summaryUnits.length === 1 && layer === 'State' ? (
          <Box sx={{ mt: '-0.5rem', mb: '1rem' }}>
            <Link to={`/states/${id}`}>
              view state page for more information{' '}
              <AngleDoubleRight size="1em" />
            </Link>
          </Box>
        ) : null}

        <Paragraph>
          {summaryUnits.length === 1
            ? 'This area contains:'
            : 'These areas contain:'}
        </Paragraph>
        {barrierType === 'dams' || barrierType === 'combined_barriers' ? (
          <>
            {dams > 0 ? (
              <>
                <Paragraph sx={{ mt: '0.5rem' }}>
                  <b>{formatNumber(dams, 0)}</b> inventoried{' '}
                  {dams === 1 ? 'dam' : 'dams'}, including:
                </Paragraph>

                <Box as="ul" sx={{ mt: '0.5rem' }}>
                  <li>
                    <b>{formatNumber(rankedDams, 0)}</b> that{' '}
                    {rankedDams === 1 ? 'was ' : 'were '} analyzed for impacts
                    to aquatic connectivity in this tool
                  </li>
                  {removedDams > 0 ? (
                    <li>
                      <b>{formatNumber(removedDams, 0)}</b> that have been
                      removed or mitigated, gaining{' '}
                      <b>{formatNumber(removedDamsGainMiles)} miles</b> of
                      reconnected rivers and streams
                    </li>
                  ) : null}
                </Box>
              </>
            ) : (
              <Text sx={{ mt: '0.5rem' }}>
                <b>0</b> inventoried dams
              </Text>
            )}
          </>
        ) : null}
        {barrierType === 'small_barriers' ||
        barrierType === 'combined_barriers' ? (
          <>
            {totalRoadBarriers > 0 ? (
              <>
                <Paragraph
                  sx={{
                    mt:
                      barrierType === 'combined_barriers' ? '1.5rem' : '0.5rem',
                  }}
                >
                  <b>{formatNumber(totalRoadBarriers, 0)}</b> or more
                  road/stream crossings (potential aquatic barriers), including:
                </Paragraph>
                <Box as="ul" sx={{ mt: '0.5rem' }}>
                  <li>
                    <b>
                      {formatNumber(
                        totalSmallBarriers - removedSmallBarriers,
                        0
                      )}
                    </b>{' '}
                    that{' '}
                    {totalSmallBarriers - removedSmallBarriers === 1
                      ? 'has '
                      : 'have '}{' '}
                    been assessed for impacts to aquatic organisms.
                  </li>
                  <li>
                    <b>
                      {formatNumber(smallBarriers - removedSmallBarriers, 0)}
                    </b>{' '}
                    that{' '}
                    {smallBarriers - removedSmallBarriers === 1 ? 'is' : 'are'}{' '}
                    likely to impact aquatic organisms
                  </li>
                  <li>
                    <b>{formatNumber(rankedSmallBarriers, 0)}</b> that{' '}
                    {rankedSmallBarriers === 1 ? 'was ' : 'were '} analyzed for
                    impacts to aquatic connectivity in this tool
                  </li>
                  {removedSmallBarriers > 0 ? (
                    <li>
                      <b>{formatNumber(removedSmallBarriers, 0)}</b> that have
                      been removed or mitigated, gaining{' '}
                      <b>{formatNumber(removedSmallBarriersGainMiles)} miles</b>{' '}
                      of reconnected rivers and streams
                    </li>
                  ) : null}
                  <li>
                    <b>{formatNumber(unsurveyedRoadCrossings, 0)}</b> that have
                    not yet been surveyed
                  </li>
                </Box>
              </>
            ) : (
              <Text sx={{ mt: '0.5rem' }}>
                <b>0</b> known road/stream crossings
              </Text>
            )}
          </>
        ) : null}

        {summaryUnits.length > 1 ? (
          <Box>
            <Box
              sx={{
                mt: '2rem',
                mb: '0.5rem',
                mx: '-1rem',
                px: '1rem',
                py: '0.25rem',
                bg: 'grey.0',
                borderTop: '1px solid',
                borderTopColor: 'grey.2',
                borderBottom: '1px solid',
                borderBottomColor: 'grey.2',
              }}
            >
              <Text sx={{ fontWeight: 'bold' }}>Selected areas:</Text>
            </Box>
            <Box
              as="ul"
              sx={{
                m: 0,
                p: 0,
                listStyle: 'none',
              }}
            >
              {summaryUnits.map((unit) => (
                <UnitListItem
                  key={unit.id}
                  barrierType={barrierType}
                  system={system}
                  unit={unit}
                  ignore={ignoreIds.has(unit.id)}
                  onDelete={() => onSelectUnit(unit)}
                />
              ))}
            </Box>
          </Box>
        ) : null}

        <Box
          sx={{
            mt: summaryUnits.length === 1 ? '2rem' : undefined,
            mx: '-1rem',
            pt: '1rem',
            pb: '2rem',
            px: '1rem',
            borderBottom: '2px solid',
            borderBottomColor: 'grey.2',
            borderTop: summaryUnits.length === 1 ? '2px solid' : undefined,
            borderTopColor: 'grey.2',
          }}
        >
          <Text
            variant="help"
            sx={{
              mt: '0.5rem',
              pb: '1.5rem',
            }}
          >
            Select {summaryUnits.length > 0 ? 'additional' : ''}{' '}
            {system === 'ADM' ? 'states / counties' : 'hydrologic units'} by
            clicking on them on the map or searching by name. You can then
            download data for all selected areas.
          </Text>
          <UnitSearch
            barrierType={barrierType}
            system={system}
            ignoreIds={
              summaryUnits && summaryUnits.length > 0
                ? new Set(summaryUnits.map(({ id: unitId }) => unitId))
                : null
            }
            onSelect={onSelectUnit}
          />
        </Box>

        {barrierType === 'dams' ? (
          <Paragraph variant="help" sx={{ mt: '2rem' }}>
            Note: These statistics are based on <i>inventoried</i> dams. Because
            the inventory is incomplete in many areas, areas with a high number
            of dams may simply represent areas that have a more complete
            inventory.
            {unrankedDams > 0 ? (
              <>
                <br />
                <br />
                {formatNumber(unrankedDams, 0)} {pluralize('dam', unrankedDams)}{' '}
                {unrankedDams === 1 ? 'was' : 'were'} not analyzed because{' '}
                {unrankedDams === 1 ? 'it was' : 'they were'} not on the aquatic
                network or could not be correctly located on the network.
              </>
            ) : null}
          </Paragraph>
        ) : null}

        {barrierType === 'small_barriers' ? (
          <Paragraph variant="help" sx={{ mt: '2rem' }}>
            Note: These statistics are based on <i>inventoried</i> road-related
            barriers that have been assessed for impacts to aquatic organisms.
            Because the inventory is incomplete in many areas, areas with a high
            number of barriers may simply represent areas that have a more
            complete inventory.
            {unrankedBarriers > 0 ? (
              <>
                <br />
                <br />
                {formatNumber(unrankedBarriers, 0)} road-related{' '}
                {pluralize('barrier', unrankedBarriers)}{' '}
                {unrankedBarriers === 1 ? 'was' : 'were'} not analyzed because{' '}
                {unrankedBarriers === 1 ? 'it was' : 'they were'} not on the
                aquatic network or could not be correctly located on the network
              </>
            ) : null}
          </Paragraph>
        ) : null}

        {barrierType === 'combined_barriers' ? (
          <Paragraph variant="help" sx={{ mt: '2rem' }}>
            Note: These statistics are based on <i>inventoried</i> dams and
            road-related barriers that have been assessed for impacts to aquatic
            organisms. Because the inventory is incomplete in many areas, areas
            with a high number of barriers may simply represent areas that have
            a more complete inventory.
            {unrankedDams > 0 || unrankedBarriers > 0 ? (
              <>
                <br />
                <br />
                {unrankedDams > 0
                  ? `${formatNumber(unrankedDams, 0)} dams`
                  : null}
                {unrankedDams > 0 && unrankedBarriers > 0 ? ' and ' : null}
                {unrankedBarriers > 0
                  ? `${formatNumber(unrankedBarriers, 0)} road-related barriers`
                  : null}{' '}
                {unrankedDams + unrankedBarriers === 1 ? 'was' : 'were'} not
                analyzed because{' '}
                {unrankedDams + unrankedBarriers === 1 ? 'it was' : 'they were'}{' '}
                not on the aquatic network or could not be correctly located on
                the network
              </>
            ) : null}
          </Paragraph>
        ) : null}
      </Box>

      <Box
        sx={{
          flex: '0 0 auto',
          display:
            barrierType === 'dams' || barrierType === 'combined_barriers'
              ? 'flex'
              : null,
          alignItems: 'center',
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
        <Text sx={{ lineHeight: 1, flex: '0 0 auto' }}>Download:</Text>
        <Flex
          sx={{
            flex: '1 1 auto',
            mt: '0.5rem',
            justifyContent:
              barrierType === 'small_barriers' ? 'center' : 'flex-end',
          }}
        >
          {downloadButtons}
        </Flex>
      </Box>
    </Flex>
  )
}

UnitSummary.propTypes = {
  barrierType: PropTypes.string.isRequired,
  system: PropTypes.string.isRequired,
  summaryUnits: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
      layer: PropTypes.string.isRequired,
      name: PropTypes.string,
      dams: PropTypes.number,
      rankedDams: PropTypes.number,
      removedDams: PropTypes.number,
      removedDamsGainMiles: PropTypes.number,
      smallBarriers: PropTypes.number,
      totalSmallBarriers: PropTypes.number,
      rankedSmallBarriers: PropTypes.number,
      removedSmallBarriers: PropTypes.number,
      removedSmallBarriersGainMiles: PropTypes.number,
      totalRoadCrossings: PropTypes.number,
      unsurveyedRoadCrossings: PropTypes.number,
      miles: PropTypes.number,
    })
  ).isRequired,
  onSelectUnit: PropTypes.func.isRequired,
  onReset: PropTypes.func.isRequired,
}

export default UnitSummary
