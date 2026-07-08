export const CUSTOMER_LIST_STATE_KEY = 'fishpool.customerListState'

export const createDefaultCustomerListState = () => ({
  searchParams: {
    search: '',
    page: 1,
    page_size: 12
  },
  filterConditions: [],
  sortState: {
    field: '',
    direction: 'desc'
  }
})

export const getCustomerListStorage = () => {
  if (typeof window === 'undefined') {
    return null
  }

  return window.sessionStorage
}

const normalizePositiveInteger = (value, fallback) => {
  const parsedValue = Number(value)
  return Number.isInteger(parsedValue) && parsedValue > 0 ? parsedValue : fallback
}

const normalizeFilterCondition = (condition) => {
  if (!condition || typeof condition !== 'object') {
    return null
  }

  return {
    id: String(condition.id || `${Date.now()}-${Math.random()}`),
    field: String(condition.field || 'client_name'),
    operator: String(condition.operator || 'contains'),
    value: Array.isArray(condition.value) ? [...condition.value] : (condition.value ?? '')
  }
}

const normalizeState = (state) => {
  const defaults = createDefaultCustomerListState()
  const searchParams = state?.searchParams ?? {}
  const sortState = state?.sortState ?? {}

  return {
    searchParams: {
      search: String(searchParams.search ?? defaults.searchParams.search),
      page: normalizePositiveInteger(searchParams.page, defaults.searchParams.page),
      page_size: normalizePositiveInteger(searchParams.page_size, defaults.searchParams.page_size)
    },
    filterConditions: Array.isArray(state?.filterConditions)
      ? state.filterConditions.map(normalizeFilterCondition).filter(Boolean)
      : defaults.filterConditions,
    sortState: {
      field: String(sortState.field ?? defaults.sortState.field),
      direction: sortState.direction === 'asc' ? 'asc' : defaults.sortState.direction
    }
  }
}

export const loadCustomerListState = (storage = getCustomerListStorage()) => {
  if (!storage) {
    return createDefaultCustomerListState()
  }

  try {
    const rawState = storage.getItem(CUSTOMER_LIST_STATE_KEY)
    if (!rawState) {
      return createDefaultCustomerListState()
    }

    return normalizeState(JSON.parse(rawState))
  } catch {
    return createDefaultCustomerListState()
  }
}

export const saveCustomerListState = (storage = getCustomerListStorage(), state) => {
  if (!storage) {
    return
  }

  storage.setItem(CUSTOMER_LIST_STATE_KEY, JSON.stringify(normalizeState(state)))
}

export const clearCustomerListFilterAndSort = (state) => {
  const normalizedState = normalizeState(state)

  return {
    searchParams: {
      ...normalizedState.searchParams,
      page: 1
    },
    filterConditions: [],
    sortState: {
      field: '',
      direction: 'desc'
    }
  }
}
