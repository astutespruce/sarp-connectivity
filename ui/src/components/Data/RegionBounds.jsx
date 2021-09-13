import { graphql, useStaticQuery } from 'gatsby'
import { groupBy } from 'util/data'

export const useRegionBounds = () => {
  const {
    bounds: { nodes: bounds },
  } = useStaticQuery(graphql`
    query regionBoundsQuery {
      bounds: allRegionBoundsJson {
        nodes {
          id
          bbox
        }
      }
    }
  `)

  return { ...groupBy(bounds, 'id') }
}
