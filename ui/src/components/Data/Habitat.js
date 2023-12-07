import { SPECIES_HABITAT_FIELDS } from 'config'

export const extractHabitat = (habitatFields) =>
  Object.entries(SPECIES_HABITAT_FIELDS)
    .map(([key, { label, source, limit }]) => ({
      key,
      label,
      source,
      limit,
      upstreammiles: habitatFields[`${key}upstreammiles`] || 0,
      downstreammiles: habitatFields[`free${key}downstreammiles`] || 0,
    }))
    .filter(
      ({ upstreammiles, downstreammiles }) =>
        upstreammiles + downstreammiles > 0
    )
