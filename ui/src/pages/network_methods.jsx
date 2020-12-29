import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { FaExclamationTriangle } from 'react-icons/fa'

import { HelpText } from 'components/Text'
import Layout from 'components/Layout'
import { HeaderImage } from 'components/Image'
import { Link, OutboundLink } from 'components/Link'
import {
  PageTitle,
  PageContainer,
  Section as BaseSection,
  Title,
  LargeText,
  Divider,
} from 'content/styles'
import styled, { themeGet } from 'style'

const Section = styled(BaseSection)`
  &:not(:first-child) {
    margin-top: 3rem;
  }
`

const WarningIcon = styled(FaExclamationTriangle)`
  width: 1.5em;
  height: 1em;
  color: ${themeGet('colors.highlight.500')};
  display: inline-block;
  margin-right: 0.25em;
`

const Note = styled(HelpText).attrs({ mt: '1rem' })``

const LengthPage = ({ data: { headerImage } }) => (
  <Layout>
    <HeaderImage
      image={headerImage.childImageSharp.fluid}
      height="30vh"
      minHeight="18rem"
      position="center"
      credits={{
        author:
          'Biologists collect and move fish from a de-watered river reach as part of Cane River Dam removal, 2016 | U.S. Fish & Wildlife Service Southeast Region',
        url: 'https://www.flickr.com/photos/usfwssoutheast/30557776285/',
      }}
    />

    <PageContainer>
      <PageTitle>Network Analysis - Southeastern States</PageTitle>
      <LargeText>
        Barriers in all states in the Southeast U.S. were analyzed using the{' '}
        <OutboundLink to="https://www.usgs.gov/core-science-systems/ngp/national-hydrography/nhdplus-high-resolution">
          National Hydrography Dataset - High Resolution Plus
        </OutboundLink>{' '}
        (NHDPlusHR) dataset from the U.S. Geological Survey. These data are
        defined at a 1:24,000 scale or better.
        <br />
        <br />
        The following methods represent our best attempt to correctly snap and
        analyze dams and road-related barriers. If you see errors in the dam,
        road-related barrier, or waterfall locations used in the analysis, or
        would like additional help interpreting the results of the analysis,
        please <a href="mailto:Kat@southeastaquatics.net">contact us</a>.
      </LargeText>

      <Section>
        <Title>Aquatic Network Preparation</Title>
        <ol>
          <li>
            All coastline and underground conduit segments were first removed
            from the NHDPlusHR flowlines dataset. &quot;Loops&quot; were
            retained for purposes of snapping waterfalls and barriers below, but
            barriers that snapped to these loops were excluded from the network
            connectivity analysis.
          </li>
          <li>
            All isolated pipelines or pipelines &gt;250 meters were removed from
            the flowlines dataset. Short pipelines through dams were retained,
            in order to ensure that these dams could be evaluated for network
            connectivity.
          </li>
          <li>
            All waterbodies &gt;0.02 square kilometers were extracted from the
            NHDPlusHR waterbody dataset and intersected with the flowlines to
            determine flowlines that are within waterbodies. Flowlines outside
            these waterbodies were considered free-flowing for the network
            connectivity analysis.
          </li>
          <li>
            In some regions, network segments were manually removed from the
            analysis (e.g., Chesapeake Bay).
          </li>
        </ol>
      </Section>

      <Section>
        <Title>Methods for Waterfalls</Title>
        <p>
          Waterfalls are used to define natural breaks within the aquatic
          network. All waterfalls included in this analysis were considered
          &quot;hard&quot; breaks to the aquatic network, which prevent upstream
          or downstream movement of aquatic species.
          <br />
          <br />
        </p>
        <ol>
          <li>
            Waterfalls were obtained from U.S. Geological Survey (data
            publication in prep.).
          </li>
          <li>
            Waterfalls were automatically snapped to the nearest flowline within
            a 100 meter tolerance.
          </li>
          <li>
            Waterfalls were de-duplicated within a 10 meter tolerance: those
            that occurred closer together than 10 meters were considered
            duplicates, and only the first instance of each set of duplicates
            was retained.
          </li>
          <li>
            Waterfalls that were successfully snapped to the aquatic network
            were used to cut the aquatic network. These networks formed the
            basis of aquatic networks that were further subdivided by dams and
            road-related barriers below.
          </li>
        </ol>
      </Section>

      <Section>
        <Title>Methods for Dams</Title>
        <p>
          The location of dams across the Southeast were compiled by SARP from a
          variety of data providers, including the{' '}
          <OutboundLink to="http://nid.usace.army.mil/cm_apex/f?p=838:12">
            National Inventory of Dams
          </OutboundLink>
          ,{' '}
          <OutboundLink to="https://www.sciencebase.gov/catalog/item/56a7f9dce4b0b28f1184dabd">
            National Anthropogenic Barrier Database
          </OutboundLink>
          , and state agencies. Due to variations in the vintage and accuracy of
          these datasets, not all dam points are located correctly, and some
          dams are duplicated between these data providers. Some of these dams
          were supplemented with input from partners with on the ground
          knowledge of specific structures.
          <br />
          <br />
        </p>
        <ol>
          <li>
            Dams that are known to have been removed for conservation purposes
            or that were determined to not otherwise exist were removed from the
            analysis.
          </li>
          <li>
            Invasive species barriers or dams that were determined not to be
            significant barriers based on field reconnaissance or manual review
            of aerial imagery were excluded from the analysis, but are displayed
            on the map for reference.
          </li>
          <li>
            The location of dams and dam-related features (e.g., spillways) were
            extracted from NHDPlusHR dataset. These were buffered by 5-10 meters
            and adjacent / overlapping features were dissolved in to a single
            feature. The intersection points between the flowlines and these dam
            features were used as reference points for snapping dams in the SARP
            inventory.
          </li>
          <li>
            For each waterbody extracted above, the downstream-most point(s) on
            any intersecting flowlines were extracted and used as reference
            points for snapping dams. These are called &quot;drain points&quot;
            below.
          </li>
          <li>
            Dams were snapped to the above dam-related features if they fell
            within 50 meters. They were snapped to the nearest intersection
            point between the dam-related feature and the flowlines. For very
            large dams, this could be up to 1km or more away from the unsnapped
            location.
          </li>
          <li>
            Remaining dams were snapped to the above dam-related features if
            they fell within 150 meters of an intersection point between that
            feature and the flowlines. This distance was reduced to 50 meters
            for dams determined to be likely off-network based on manual review.
          </li>
          <li>
            Remaining dams that occur within the waterbodies extracted above
            were snapped to the nearest drain point of that waterbody if they
            were within 150 meters (50 for those likely off-network). Any that
            were closer to the drain point of another waterbody were snapped to
            that other waterbody&apos;s drain point instead (these occur where
            there are chains of waterbodies), otherwise those that were within
            250 meters of the drain point of the waterbody that contains them
            were snapped to that point.
          </li>
          <li>
            Remaining dams not in waterbodies were snapped to the nearest
            waterbody drain point within a tolerance of 150 meters (50 for those
            likely off-network).
          </li>
          <li>
            Remaining dams were snapped to the nearest flowline within a
            tolerance of 150 meters (50 for those likely off-network).
          </li>
          <li>
            Remaining dams that were within 50 meters of a large waterbody
            (&gt;0.25 square kilometers and &gt;1 km flowlines within waterbody)
            were snapped to the nearest drain point for that waterbody within a
            tolerance of 250 meters.
          </li>
          <li>
            Dams were de-duplicated within a tolerance of 10 meters (50 meters
            for those likely to be duplicates based on manual review). The dam
            with the most information available in the inventory was retained
            from each set of duplicates.
          </li>
          <li>
            Only dams that were successfully snapped to the aquatic network and
            were not otherwise excluded from the analysis were analyzed for
            their impacts to network connectivity.
          </li>
          <li>
            Aquatic networks were cut at each dam. The network topology was used
            to determine the upstream functional network.
          </li>
          <li>
            Metrics for <Link to="/metrics/length">network length</Link>,{' '}
            <Link to="/metrics/complexity">network complexity</Link>,{' '}
            <Link to="/metrics/sinuosity">sinuosity</Link>, and{' '}
            <Link to="/metrics/landcover">natural landcover</Link> were
            calculated based on these functional networks.
          </li>
        </ol>
        <Note>
          <WarningIcon /> Note: not all dams could be snapped properly. Dams
          that were closer to loops in the aquatic network or the intersection
          points between loops and NHD dam-related features or waterbodies were
          snapped to those loops instead of the primary aquatic network. This
          was done to prevent snapping dams incorrectly. In many cases where
          these were manually reviewed, these dams are in the correct location,
          but limitations of the network analysis methods prevent including
          loops within the analysis. Thus, these dams were not included in the
          analysis.
        </Note>
      </Section>

      <Section>
        <Title>Methods for Road-Related Barriers</Title>
        <p>
          Only road-related barriers that have been formally assessed for
          impacts to aquatic organisms using a defined protocol and were
          determined to be a likely barrier to those organisms were included in
          the network connectivity analysis. These represent a small subset of
          the potential road-related barriers within the region. These barriers
          were analyzed within the aquatic networks already subdivided by dams
          and waterfalls above.
          <br />
          <br />
        </p>
        <ol>
          <li>
            Barriers were snapped to the nearest flowline within a tolerance of
            50 meters.
          </li>
          <li>
            Barriers were de-duplicated within a tolerance of 10 meters. The
            barrier with the greatest impact to aquatic organisms was retained
            from each set of duplicates.
          </li>
          <li>
            Barriers within 10 meters of dams were dropped as being likely
            duplicates of those dams.
          </li>
          <li>
            Only barriers that were successfully snapped to the aquatic network
            and were not otherwise excluded from the analysis were analyzed for
            their impacts to network connectivity.
          </li>
          <li>
            Aquatic networks were cut at each barrier. The network topology was
            used to determine the upstream functional network.
          </li>
          <li>
            Metrics for <Link to="/metrics/length">network length</Link>,{' '}
            <Link to="/metrics/complexity">network complexity</Link>,{' '}
            <Link to="/metrics/sinuosity">sinuosity</Link>, and{' '}
            <Link to="/metrics/landcover">natural landcover</Link> were
            calculated based on these functional networks.
          </li>
        </ol>
        <Note>
          <WarningIcon /> Note: not all barriers could be snapped properly. The
          snapping methods above do not include the locations of road / stream
          crossings, which means that the snapped location of the barrier may
          not be precisely located on the nearest road.
        </Note>
      </Section>

      <Section>
        <Divider />
        <LargeText>
          For more detailed information about the analysis methods, please see
          the{' '}
          <OutboundLink to="https://github.com/astutespruce/sarp-connectivity/tree/master/analysis">
            source code repository
          </OutboundLink>{' '}
          for this project.
        </LargeText>
      </Section>
    </PageContainer>
  </Layout>
)

LengthPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query NetworkMethodsPageQuery {
    headerImage: file(relativePath: { eq: "30557776285_90ce5f6683_6k.jpg" }) {
      childImageSharp {
        fluid(maxWidth: 3200, quality: 90) {
          ...GatsbyImageSharpFluid_withWebp
        }
      }
    }
  }
`

export default LengthPage
