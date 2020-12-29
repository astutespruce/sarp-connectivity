import { hasWindow } from 'util/dom'

// since some functions below may be called many times in rapid succession, we
// use this cache to throttle tracking events sent to Google.
const cache = {
  prioritize: {},
}

export const trackPrioritize = ({ barrierType, unitType, details }) => {
  if (!(hasWindow && window.gtag)) return

  if (
    cache.prioritize &&
    cache.prioritize.barrierType === barrierType &&
    cache.prioritize.unitType === unitType &&
    cache.prioritize.details === details
  ) {
    // no change in values
    return
  }

  cache.prioritize = {
    barrierType,
    unitType,
    details,
  }

  window.gtag('event', `prioritize ${barrierType} by ${unitType}`, {
    eventLabel: details,
  })
}

export const trackDownload = ({ barrierType, unitType, details }) => {
  if (!(hasWindow && window.gtag)) return

  window.gtag('event', `download ${barrierType} by ${unitType}`, {
    eventLabel: details,
  })
}
