import assert from 'node:assert/strict'
import { describe, it } from 'node:test'

import {
  clearCustomerListFilterAndSort,
  createDefaultCustomerListState,
  loadCustomerListState,
  saveCustomerListState
} from '../src/utils/customerListState.js'

const createMemoryStorage = () => {
  const values = new Map()

  return {
    getItem(key) {
      return values.has(key) ? values.get(key) : null
    },
    setItem(key, value) {
      values.set(key, String(value))
    },
    removeItem(key) {
      values.delete(key)
    }
  }
}

describe('customer list state persistence', () => {
  it('restores saved pagination, filters, search, and sorting', () => {
    const storage = createMemoryStorage()
    const savedState = {
      searchParams: {
        search: 'Acme',
        page: 3,
        page_size: 24
      },
      filterConditions: [
        {
          id: 'filter-1',
          field: 'level',
          operator: 'eq',
          value: 'A'
        }
      ],
      sortState: {
        field: 'last_year_revenue',
        direction: 'desc'
      }
    }

    saveCustomerListState(storage, savedState)

    assert.deepEqual(loadCustomerListState(storage), savedState)
  })

  it('clears filters and sorting while preserving search and page size', () => {
    const storage = createMemoryStorage()
    saveCustomerListState(storage, {
      searchParams: {
        search: 'Acme',
        page: 4,
        page_size: 48
      },
      filterConditions: [
        {
          id: 'filter-1',
          field: 'level',
          operator: 'eq',
          value: 'A'
        }
      ],
      sortState: {
        field: 'created_at',
        direction: 'asc'
      }
    })

    const clearedState = clearCustomerListFilterAndSort(loadCustomerListState(storage))

    assert.deepEqual(clearedState, {
      searchParams: {
        search: 'Acme',
        page: 1,
        page_size: 48
      },
      filterConditions: [],
      sortState: {
        field: '',
        direction: 'desc'
      }
    })
  })

  it('falls back to defaults when stored state is malformed', () => {
    const storage = createMemoryStorage()
    storage.setItem('fishpool.customerListState', '{bad json')

    assert.deepEqual(loadCustomerListState(storage), createDefaultCustomerListState())
  })
})
