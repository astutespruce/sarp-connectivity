import React from 'react'
import PropTypes from 'prop-types'
import {
  Document,
  Image,
  Page,
  View,
  Text,
  StyleSheet,
} from '@react-pdf/renderer'

const styles = StyleSheet.create({
  page: {
    fontFamily: 'Helvetica',
    paddingTop: '0.5in',
    paddingBottom: '1in',
    paddingHorizontal: '0.5in',
  },
  header: { marginBottom: 24 },
  title: { fontWeight: 'bold', fontFamily: 'Helvetica-Bold', fontSize: 24 },
  subtitle: {
    fontStyle: 'italic',
    fontFamily: 'Helvetica-Oblique',
    fontSize: 12,
  },
  map: {
    border: '1pt solid #AAA',
  },
  locatorMap: {
    marginTop: 24,
    border: '1pt solid #AAA',
    width: 200,
    height: 200,
  },
  pageNumber: {
    position: 'absolute',
    fontSize: 12,
    bottom: 30,
    left: 0,
    right: 0,
    textAlign: 'center',
    color: 'grey',
  },
})

const BarrierReport = ({ name, county, state, map, locatorMap }) => (
  <Document
    author="generated by the Southeast Aquatic Barrier Prioritization Tool"
    creator="Southeast Aquatic Barrier Prioritization Tool"
    language="en-us"
  >
    <Page style={styles.page}>
      <View style={styles.header}>
        <Text style={styles.title}>{name}</Text>
        <Text style={styles.subtitle}>
          {county}, {state}
        </Text>
      </View>

      <Image src={map} style={styles.map} />

      <Image src={locatorMap} style={styles.locatorMap} />

      <Text
        style={styles.pageNumber}
        render={({ pageNumber, totalPages }) => `${pageNumber} / ${totalPages}`}
        fixed
      />
    </Page>
  </Document>
)

BarrierReport.propTypes = {
  name: PropTypes.string.isRequired,
  county: PropTypes.string.isRequired,
  state: PropTypes.string.isRequired,
}

export default BarrierReport
