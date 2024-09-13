import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { ChartBar, Fish, SearchLocation } from '@emotion-icons/fa-solid'
import {
  Box,
  Button,
  Flex,
  Container,
  Divider,
  Grid,
  Image,
  Heading,
  Paragraph,
  Text,
} from 'theme-ui'
import { useQuery } from '@tanstack/react-query'

import { fetchUnitDetails } from 'components/Data'
import { Chart } from 'components/Restoration'
import Downloader from 'components/Download/Downloader'
import { Layout, SEO, PageError, PageLoading } from 'components/Layout'
import { Link, OutboundLink } from 'components/Link'
import { FISH_HABITAT_PARTNERSHIPS } from 'config'
import { dynamicallyLoadImage } from 'util/dom'
import { formatNumber, pluralize } from 'util/format'

const downloadConfig = { scenario: 'NCWC', layer: 'FishHabitatPartnership' }

const FHPRoute = ({ params: { id } }) => {
  const {
    name,
    description,
    url,
    logo,
    logoWidth = 140,
  } = FISH_HABITAT_PARTNERSHIPS[id] || {}

  const [metric, setMetric] = useState('gainmiles')

  const { isLoading, error, data } = useQuery({
    queryKey: ['FishHabitatPartnership', id],
    queryFn: async () => fetchUnitDetails('FishHabitatPartnership', id),

    staleTime: 60 * 60 * 1000, // 60 minutes
    // staleTime: 1, // use then reload to force refresh of underlying data during dev
    refetchOnWindowFocus: false,
    refetchOnMount: false,
  })

  if (isLoading) {
    return (
      <Layout>
        <PageLoading />
      </Layout>
    )
  }

  if (error) {
    console.error(`Error loading fish habitat partnership page: ${id}`)

    return (
      <Layout>
        <PageError />
      </Layout>
    )
  }

  const {
    dams,
    rankedDams,
    reconDams,
    removedDams,
    removedDamsGainMiles,
    totalSmallBarriers,
    smallBarriers,
    rankedSmallBarriers,
    removedSmallBarriers,
    removedSmallBarriersGainMiles,
    // totalRoadCrossings,
    unsurveyedRoadCrossings,
    removedBarriersByYear,
  } = data

  const hasRemovedBarriers =
    removedBarriersByYear.filter(({ dams: d, smallBarriers: sb }) => d + sb > 0)
      .length > 0

  const NFHPContent = (
    <>
      The {name} is one of the Fish Habitat Partnerships under the{' '}
      <OutboundLink to="https://www.fishhabitat.org/">
        {' '}
        National Fish Habitat Partnership
      </OutboundLink>{' '}
      umbrella that works to conserve and protect the nation&apos;s fisheries
      and aquatic systems through a network of 20 Fish Habitat Partnerships.
    </>
  )

  return (
    <Layout>
      <Container>
        <Flex
          sx={{
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '2rem',
            pb: '0.25rem',
          }}
        >
          <Heading as="h1" sx={{ flex: '1 1 auto' }}>
            {name}
          </Heading>
          {logo ? (
            <Box sx={{ maxWidth: logoWidth }}>
              <OutboundLink to={url}>
                <Image src={dynamicallyLoadImage(logo)} alt={`${name} logo`} />
              </OutboundLink>
            </Box>
          ) : null}
        </Flex>

        <Box>
          <Flex
            columns="1fr 1fr 1.5fr"
            gap={3}
            sx={{
              borderTop: '1px solid',
              borderTopColor: 'grey.3',
              borderBottom: '1px solid',
              borderBottomColor: 'grey.3',
              bg: 'grey.1',
              py: '0.5rem',
              px: '0.5rem',
              fontSize: 1,
              gap: '1rem',
              justifyContent: 'flex-end',
              alignItems: 'center',
              '& button': { py: '0.5rem', px: '0.5rem' },
            }}
          >
            <Text sx={{ flex: '0 0 auto' }}>Download:</Text>
            <Box sx={{ flex: '0 0 auto' }}>
              <Downloader
                label="dams"
                asButton
                barrierType="dams"
                disabled={dams === 0}
                config={{
                  ...downloadConfig,
                  summaryUnits: { fishhabitatpartnership: [id] },
                }}
              />
            </Box>

            <Box sx={{ flex: '0 0 auto' }}>
              <Downloader
                label="barriers"
                asButton
                barrierType="small_barriers"
                disabled={totalSmallBarriers === 0}
                config={{
                  ...downloadConfig,
                  summaryUnits: { fishhabitatpartnership: [id] },
                }}
              />
            </Box>

            {/* FHP boundaries generally have too many crossings for current downloader */}
            {/* <Box sx={{ flex: '0 0 auto' }}>
              <Downloader
                barrierType="road_crossings"
                label="road crossings"
                disabled={totalRoadCrossings === 0}
                config={{
                  ...downloadConfig,
                  summaryUnits: { fishhabitatpartnership: [id] },
                }}
              />
            </Box> */}
          </Flex>
        </Box>

        {description ? (
          <Grid columns="2fr 1fr" gap={4} sx={{ mt: '1rem' }}>
            <Paragraph>
              {description}
              <br />
              <br />
              Learn more about the <OutboundLink to={url}>{name}</OutboundLink>.
            </Paragraph>
            <Box sx={{ bg: 'blue.1', p: '1rem', borderRadius: '1rem' }}>
              {NFHPContent}
            </Box>
          </Grid>
        ) : (
          <Paragraph sx={{ mt: '1rem' }}>
            {NFHPContent}
            <br />
            <br />
            Learn more about the <OutboundLink to={url}>{name}</OutboundLink>.
          </Paragraph>
        )}

        <Divider />

        <Grid columns={2} gap={5} sx={{ mt: '2rem' }}>
          <Box>
            <Box sx={{ border: '1px solid', borderColor: 'grey.4' }}>
              <Image
                src={dynamicallyLoadImage(`maps/fhp/${id}.png`)}
                alt={`${name} map`}
                sx={{ border: '1px solid', borderColor: 'grey.3' }}
              />
            </Box>
            <Text sx={{ fontSize: 1, color: 'grey.7' }}>
              Map of {formatNumber(dams)} inventoried dams and{' '}
              {formatNumber(smallBarriers)} road-related barriers likely to
              impact aquatic organisms in the {name} boundary.
            </Text>
          </Box>
          <Box>
            <Heading as="h4">
              The inventory within the {name} boundary currently includes
            </Heading>
            <Text sx={{ mt: '0.5rem' }}>
              <b>{formatNumber(dams)}</b> inventoried {pluralize('dam', dams)},
              including:
            </Text>
            <Box as="ul" sx={{ ml: '1rem', mb: '1rem', mt: '0.5rem' }}>
              <li>
                <b>{formatNumber(rankedDams, 0)}</b> that{' '}
                {rankedDams === 1 ? 'was ' : 'were '} analyzed for impacts to
                aquatic connectivity in this tool
              </li>
              <li>
                <b>{formatNumber(reconDams)}</b> that{' '}
                {reconDams === 1 ? 'has' : 'have'} been reconned for social
                feasibility of removal
              </li>
              {removedDams > 0 ? (
                <li>
                  <b>{formatNumber(removedDams, 0)}</b> that{' '}
                  {removedDams === 1 ? 'has' : 'have'} been removed or
                  mitigated, gaining{' '}
                  <b>{formatNumber(removedDamsGainMiles)} miles</b> of
                  reconnected rivers and streams
                </li>
              ) : null}
            </Box>
            <Text sx={{ mt: '2rem' }}>
              <b>
                {formatNumber(totalSmallBarriers + unsurveyedRoadCrossings, 0)}
              </b>{' '}
              or more road/stream crossings (potential barriers), including:
            </Text>
            <Box as="ul" sx={{ ml: '1rem', mt: '0.5rem' }}>
              <li>
                <b>{formatNumber(totalSmallBarriers, 0)}</b> that{' '}
                {totalSmallBarriers === 1 ? 'has' : 'have'} been assessed for
                impacts to aquatic organisms
              </li>

              <li>
                <b>{formatNumber(smallBarriers, 0)}</b> that{' '}
                {smallBarriers === 1 ? 'is' : 'are'} likely to impact aquatic
                organisms
              </li>
              <li>
                <b>{formatNumber(rankedSmallBarriers, 0)}</b> that{' '}
                {rankedSmallBarriers === 1 ? 'was ' : 'were '} analyzed for
                impacts to aquatic connectivity in this tool
              </li>
              {removedSmallBarriers > 0 ? (
                <li>
                  <b>{formatNumber(removedSmallBarriers, 0)}</b> that{' '}
                  {removedSmallBarriers === 1 ? 'has' : 'have'} been removed or
                  mitigated, gaining{' '}
                  <b>{formatNumber(removedSmallBarriersGainMiles)} miles</b> of
                  reconnected rivers and streams
                </li>
              ) : null}
            </Box>
          </Box>
        </Grid>

        {hasRemovedBarriers ? (
          <Box sx={{ mt: '3rem' }}>
            <Heading as="h3">
              Progress toward restoring aquatic connectivity:
            </Heading>
            <Box sx={{ mt: '1rem' }}>
              <Chart
                barrierType="combined_barriers"
                removedBarriersByYear={removedBarriersByYear}
                metric={metric}
                onChangeMetric={setMetric}
              />
            </Box>
            <Text variant="help" sx={{ mt: '1rem' }}>
              Note: counts above may include both completed as well as active
              barrier removal or mitigation projects.
            </Text>
          </Box>
        ) : null}

        <Grid
          columns={3}
          gap={3}
          sx={{
            mt: '4rem',
            py: '1rem',
            px: '1rem',
            bg: 'grey.1',
            borderTop: '1px solid',
            borderTopColor: 'grey.3',
            borderBottom: '1px solid',
            borderBottomColor: 'grey.3',
          }}
        >
          <Flex
            sx={{
              flexDirection: 'column',
              justifyContent: 'space-between',
              gap: '1rem',
              borderRight: '1px solid',
              borderRightColor: '#FFF',
              px: '1rem',
              width: '100%',
              height: '100%',
            }}
          >
            <Text sx={{ flex: '0 0 auto' }}>
              Explore how many dams or road-related barriers there are in a
              state, county, or watershed.
            </Text>
            <Flex
              sx={{
                flex: '1 1 auto',
                justifyContent: 'center',
                alignItems: 'flex-end',
              }}
            >
              <Link to={`/explore?fishhabitatpartnership=${id}`}>
                <Button variant="primary">
                  <ChartBar size="1em" />
                  &nbsp; Start exploring
                </Button>
              </Link>
            </Flex>
          </Flex>

          <Flex
            sx={{
              flexDirection: 'column',
              justifyContent: 'space-between',
              gap: '1rem',
              borderRight: '1px solid',
              borderRightColor: '#FFF',
              px: '1rem',
              width: '100%',
              height: '100%',
            }}
          >
            <Text sx={{ flex: '0 0 auto' }}>
              Explore dams and road-related barriers that have been removed or
              mitigated by state, county, or watershed.
            </Text>
            <Flex
              sx={{
                flex: '1 1 auto',
                justifyContent: 'center',
                alignItems: 'flex-end',
              }}
            >
              <Link to={`/restoration?fishhabitatpartnership=${id}`}>
                <Button variant="primary">
                  <Fish size="1em" />
                  &nbsp; See restoration progress
                </Button>
              </Link>
            </Flex>
          </Flex>

          <Flex
            sx={{
              flexDirection: 'column',
              justifyContent: 'space-between',
              gap: '1rem',
              px: '1rem',
              width: '100%',
              height: '100%',
            }}
          >
            <Text sx={{ flex: '0 0 auto' }}>
              Identify and rank dams or road-related barriers that reconnect the
              most high-quality aquatic networks.
            </Text>
            <Flex
              sx={{
                flex: '1 1 auto',
                justifyContent: 'center',
                alignItems: 'flex-end',
              }}
            >
              <Link to="/priority">
                <Button>
                  <SearchLocation size="1em" />
                  &nbsp; Start prioritizing
                </Button>
              </Link>
            </Flex>
          </Flex>
        </Grid>

        <Divider sx={{ my: '4rem' }} />

        <Box variant="boxes.section">
          <Heading as="h2" variant="heading.section">
            You can help!
          </Heading>
          <Flex sx={{ gap: '3rem' }}>
            <Paragraph>
              You can help improve the inventory You can help improve the
              inventory by sharing data, assisting with field reconnaissance to
              evaluate the impact of aquatic barriers, or even by reporting
              issues with the inventory data in this tool. To join an aquatic
              connectivity team click{' '}
              <OutboundLink to="https://www.americanrivers.org/aquatic-connectivity-groups/">
                here
              </OutboundLink>
              .
              <br />
              <br />
              <a href="mailto:kat@southeastaquatics.net">Contact us</a> to learn
              more about how you can help improve aquatic connectivity in {name}
              .
            </Paragraph>
          </Flex>
        </Box>
      </Container>
    </Layout>
  )
}

FHPRoute.propTypes = {
  params: PropTypes.shape({
    id: PropTypes.string,
  }).isRequired,
}

export default FHPRoute

/* eslint-disable-next-line react/prop-types */
export const Head = ({ params: { id } }) => (
  <SEO
    title={
      FISH_HABITAT_PARTNERSHIPS[id] ? FISH_HABITAT_PARTNERSHIPS[id].name : null
    }
  />
)
