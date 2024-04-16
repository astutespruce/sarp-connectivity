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

import Chart from './Chart'
import UnitListItem from './UnitListItem'
import { layers } from './layers'
import { extractYearRemovedStats } from './util'

const defaultDownloaderConfig = {
  filters: {
    removed: new Set([true]),
  },
}

const UnitSummary = ({
  barrierType,
  system,
  summaryUnits,
  metric,
  onChangeMetric,
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
  let removedDams = 0
  let removedDamsGainMiles = 0
  let totalSmallBarriers = 0
  let removedSmallBarriers = 0
  let removedSmallBarriersGainMiles = 0

  let removedBarriersByYear = []

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
        title = `${name} County`
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
        removedDams: curRemovedDams = 0,
        removedDamsGainMiles: curRemovedDamsGainMiles = 0,
        removedDamsByYear: curRemovedDamsByYear = '',
        totalSmallBarriers: curTotalSmallBarriers = 0,
        removedSmallBarriers: curRemovedSmallBarriers = 0,
        removedSmallBarriersGainMiles: curRemovedSmallBarriersGainMiles = 0,
        removedSmallBarriersByYear: curRemovedSmallBarriersByYear = '',
      }) => {
        dams += curDams
        removedDams += curRemovedDams
        removedDamsGainMiles += curRemovedDamsGainMiles
        totalSmallBarriers += curTotalSmallBarriers
        removedSmallBarriers += curRemovedSmallBarriers
        removedSmallBarriersGainMiles += curRemovedSmallBarriersGainMiles

        const curRemovedBarriersByYear = extractYearRemovedStats(
          curRemovedDamsByYear,
          curRemovedSmallBarriersByYear
        )

        if (removedBarriersByYear.length === 0) {
          removedBarriersByYear = curRemovedBarriersByYear
        } else if (curRemovedBarriersByYear.length > 0) {
          // splice together; entries are in same order
          removedBarriersByYear = removedBarriersByYear.map((prev, i) => {
            const cur = curRemovedBarriersByYear[i]
            return Object.fromEntries(
              Object.entries(prev).map(([key, value]) => [
                key,
                key === 'label' ? value : value + cur[key],
              ])
            )
          })
        }
      }
    )

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
    ...defaultDownloaderConfig,
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
        <Box sx={{ width: '12rem' }}>
          <Flex sx={{ ml: '1rem', flex: '1 1 auto' }}>
            <Downloader
              barrierType="small_barriers"
              label={barrierTypeLabels.small_barriers}
              config={downloaderConfig}
              disabled={totalSmallBarriers === 0}
              showOptions={false}
              includeUnranked
            />
          </Flex>
        </Box>
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
          <Paragraph sx={{ mt: '0.5rem' }}>
            {removedDams > 0 ? (
              <>
                <b>
                  {formatNumber(removedDams, 0)} {pluralize('dam', removedDams)}
                </b>{' '}
                that{' '}
                {removedDams === 1
                  ? 'has been or is actively being'
                  : 'have been or are actively being'}{' '}
                removed or mitigated, gaining{' '}
                <b>{formatNumber(removedDamsGainMiles)} miles</b> of reconnected
                rivers and streams
              </>
            ) : (
              <>
                <b>0</b> dams that are known to have been removed or mitigated
              </>
            )}
          </Paragraph>
        ) : null}

        {barrierType === 'small_barriers' ||
        barrierType === 'combined_barriers' ? (
          <Paragraph
            sx={{
              mt: barrierType === 'combined_barriers' ? '1.5rem' : '0.5rem',
            }}
          >
            {removedSmallBarriers ? (
              <>
                <b>{formatNumber(removedSmallBarriers, 0)}</b>{' '}
                {pluralize('road-related barrier', removedSmallBarriers)} that{' '}
                {removedSmallBarriers === 1
                  ? 'has been or is actively being'
                  : 'have been or are actively being'}{' '}
                removed or mitigated, gaining{' '}
                <b>{formatNumber(removedSmallBarriersGainMiles)} miles</b> of
                reconnected rivers and streams
              </>
            ) : (
              <>
                <b>0</b> road-related barriers that are known to have been
                removed or mitigated
              </>
            )}
          </Paragraph>
        ) : null}

        <Box sx={{ mt: '2rem' }}>
          <Chart
            barrierType={barrierType}
            removedBarriersByYear={removedBarriersByYear}
            metric={metric}
            onChangeMetric={onChangeMetric}
          />
        </Box>

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
            Note: These statistics are based on <b>{formatNumber(dams, 0)}</b>{' '}
            inventoried {pluralize('dam', dams)} and available information on
            dams that have been or are actively being removed or mitigated,
            including projects starting in 2024. Because the inventory is
            incomplete in many areas, areas with a high number of dams may
            simply represent areas that have a more complete inventory.
          </Paragraph>
        ) : null}

        {barrierType === 'small_barriers' ? (
          <Paragraph variant="help" sx={{ mt: '2rem' }}>
            Note: These statistics are based on{' '}
            {formatNumber(totalSmallBarriers, 0)} road/stream crossings that
            have been assessed for impacts to aquatic organisms and available
            information on barriers that have been removed or mitigated. Because
            the inventory is incomplete in many areas, areas with a high number
            of barriers may simply represent areas that have a more complete
            inventory.
          </Paragraph>
        ) : null}

        {barrierType === 'combined_barriers' ? (
          <Paragraph variant="help" sx={{ mt: '2rem' }}>
            Note: These statistics are based on {formatNumber(dams, 0)}{' '}
            inventoried {pluralize('dam', dams)} and{' '}
            {formatNumber(totalSmallBarriers, 0)} inventoried{' '}
            {pluralize('road-related barrier', totalSmallBarriers)} that have
            been assessed for impacts to aquatic organisms, and available
            information on barriers that have been or are actively being removed
            or mitigated, including projects starting in 2024. Because the
            inventory is incomplete in many areas, areas with a high number of
            barriers may simply represent areas that have a more complete
            inventory.
          </Paragraph>
        ) : null}

        <Paragraph variant="help" sx={{ mt: '1rem' }}>
          Miles gained are based on aquatic networks cut by{' '}
          {barrierType === 'dams'
            ? 'waterfalls and dams'
            : 'waterfalls, dams, and road-related barriers'}{' '}
          that were present at the time a given barrier was removed, with the
          exception of those directly upstream that were removed in the same
          year as a given barrier.
        </Paragraph>
      </Box>

      <Flex
        sx={{
          flex: '0 0 auto',
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
            justifyContent: 'flex-end',
          }}
        >
          {downloadButtons}
        </Flex>
      </Flex>
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
      removedDams: PropTypes.number,
      removedDamsGainMiles: PropTypes.number,
      removedDamsByYear: PropTypes.string,
      totalSmallBarriers: PropTypes.number,
      removedSmallBarriers: PropTypes.number,
      removedSmallBarriersGainMiles: PropTypes.number,
      removedSmallBarriersByYear: PropTypes.string,
    })
  ).isRequired,
  metric: PropTypes.string.isRequired,
  onChangeMetric: PropTypes.func.isRequired,
  onSelectUnit: PropTypes.func.isRequired,
  onReset: PropTypes.func.isRequired,
}

export default UnitSummary
