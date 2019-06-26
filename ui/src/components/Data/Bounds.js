import { useMemo } from 'react'
import { graphql, useStaticQuery } from 'gatsby'

import { SYSTEM_UNITS, STATE_FIPS } from '../../../config/constants'

export const useBoundsData = () => {
  const data = useStaticQuery(graphql`
    query boundsQuery {
      unitBoundsJson {
        State {
          id
          bbox
        }
        County {
          id
          bbox
          name
          state
        }
        HUC6 {
          id
          bbox
          name
          state
        }
        HUC8 {
          id
          bbox
          name
          state
        }
        HUC12 {
          id
          bbox
          name
          state
        }
        ECO3 {
          id
          bbox
          name
          state
        }
        ECO4 {
          id
          bbox
          name
          state
        }
      }
    }
  `).unitBoundsJson

  // postprocess the data within a memoized function so that we don't
  // repeat the calculation
  return useMemo(() => {
    window.data = data

    // merge state name in
    data.State = data.State.map(({ id, ...rest }) => ({
      ...rest,
      name: STATE_FIPS[id],
      id: STATE_FIPS[id],
      layer: 'State',
    }))

    // expand county name to include " County"
    data.County = data.County.map(({ name, ...rest }) => ({
      ...rest,
      name: `${name} County`,
      layer: 'County',
    }))

    // // for HUC and ECO units, add prefix for ID
    SYSTEM_UNITS.HUC.forEach(layer => {
      data[layer].forEach(item => {
        item.layer = layer
      })
    })
    SYSTEM_UNITS.ECO.forEach(layer => {
      data[layer].forEach(item => {
        item.layer = layer
      })
    })
    return data
  }, [])
}
