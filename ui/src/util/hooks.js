// ideas adapted from: https://github.com/kentcdodds/use-deep-compare-effect/blob/master/src/index.js
import { useRef, useEffect, useMemo, useCallback, useState } from 'react'
import { dequal } from 'dequal/lite'

const isSetEqual = (setA, setB) => {
  if (setA === setB) {
    // same instance or both are null
    return true
  }
  if (setA === null || setB === null) {
    return false
  }
  // if they have the same members but are different instances, equality
  // check above fails
  if (setA.size !== setB.size) {
    return false
  }

  return Array.from(setA).filter((d) => !setB.has(d)).length === 0
}

/**
 * Return the previous instance of the value if the incoming value is equal to it.
 *
 * @param {any} value
 */
export const memoizedIsEqual = (value) => {
  /* eslint-disable-next-line react-hooks/rules-of-hooks */
  const ref = useRef(null)

  if (value instanceof Set) {
    if (!isSetEqual(value, ref.current)) {
      ref.current = value
    }
  } else if (!dequal(value, ref.current)) {
    ref.current = value
  }

  return ref.current
}

/**
 * Same as native useEffect, but compare dependencies on deep rather than shallow equality.
 * @param {function} callback
 * @param {Array} dependencies
 */
export const useIsEqualEffect = (callback, dependencies) => {
  /* eslint-disable-next-line react-hooks/exhaustive-deps */
  useEffect(
    callback,
    dependencies.map((d) => memoizedIsEqual(d))
  )
}

/**
 * Same as native useMemo, but compare dependencies on deep rather than shallow equality.
 * @param {function} callback
 * @param {Array} dependencies
 */
/* eslint-disable-next-line react-hooks/exhaustive-deps */
export const useIsEqualMemo = (callback, dependencies) =>  useMemo(
    callback,
    dependencies.map(d => memoizedIsEqual(d))
  )

  /* eslint-disable-next-line react-hooks/exhaustive-deps */
export const useIsEqualCallback = (callback, dependencies) => useCallback(
    callback,
    dependencies.map((d) => memoizedIsEqual(d))
  )


/**
 * useEffect hook that skips first call during initial rendering of component.
 * Adapted from: https://stackoverflow.com/a/54895884
 * @param {function} fn
 * @param {Array} deps - dependencies for useEffect
 */
export const useEffectSkipFirst = (f, deps) => {
  const isFirst = useRef(true)

  useEffect(() => {
    if (isFirst.current) {
      isFirst.current = false
      return
    }

    f()
  }, deps)
}

/**
 * Function that is triggered on mount of component in UI.  Useful for handling
 * client-only components.
 * From: https://www.joshwcomeau.com/react/the-perils-of-rehydration/
 */
export const useHasMounted = () => {
  const [hasMounted, setHasMounted] = useState(false)
  useEffect(() => {
    setHasMounted(true)
  }, [])
  return hasMounted
}
