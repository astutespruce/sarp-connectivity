import { HUC8_COA } from 'constants'

const getIntKeys = (obj) =>
  Object.keys(obj)
    .map((k) => parseInt(k, 10))
    .sort()

/**
 * Get sorted integer keys and labels for each entry in a keyed object
 * @param {Object} obj
 */
export const getEntries = (obj) => {
  const values = getIntKeys(obj)
  return {
    values,
    labels: values.map((key) => obj[key]),
  }
}

export const priorityAreaFilters = [
  {
    id: 'priorityAreas',
    title: 'Priority watersheds',
    filters: [
      {
        field: 'huc8_coa',
        title: 'SARP conservation opportunity areas',
        sort: false,
        // hideEmpty: true,
        help: "These areas were designated by each state and approved by SARP's steering committee for funding through SARP-NFHP-USFWS each year.",
        url: 'https://southeastaquatics.net/sarps-programs/usfws-nfhap-aquatic-habitat-restoration-program/conservation-opportunity-areas',
        ...getEntries(HUC8_COA),
      },
    ],
  },
]
