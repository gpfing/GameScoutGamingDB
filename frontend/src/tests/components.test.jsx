import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import GameCard from '../components/GameCard'
import GameModal from '../components/GameModal'
import FilterBar from '../components/FilterBar'

// Helper to wrap components with Router
const renderWithRouter = (component) => {
  return render(<BrowserRouter>{component}</BrowserRouter>)
}

describe('GameCard Component', () => {
  const mockGame = {
    id: 1,
    name: 'Test Game',
    background_image: 'https://example.com/image.jpg',
    rating: 4.5,
    released: '2024-01-01',
    genres: [{ id: 1, name: 'Action' }]
  }

  it('renders game information correctly', () => {
    renderWithRouter(<GameCard game={mockGame} onClick={() => {}} />)
    
    expect(screen.getByText('Test Game')).toBeInTheDocument()
    expect(screen.getByText(/4.5/)).toBeInTheDocument()
  })

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn()
    renderWithRouter(<GameCard game={mockGame} onClick={handleClick} />)
    
    const card = screen.getByText('Test Game').closest('.game-card')
    fireEvent.click(card)
    
    expect(handleClick).toHaveBeenCalled()
  })

  it('displays genre tags', () => {
    renderWithRouter(<GameCard game={mockGame} onClick={() => {}} />)
    
    expect(screen.getByText('Action')).toBeInTheDocument()
  })
})

describe('FilterBar Component', () => {
  const mockFilters = {
    search: '',
    genres: '',
    platforms: '',
    release_filter: 'both'
  }

  it('renders all filter inputs', () => {
    render(<FilterBar filters={mockFilters} onFilterChange={() => {}} />)
    
    expect(screen.getByPlaceholderText(/search games/i)).toBeInTheDocument()
    expect(screen.getByText(/all games/i)).toBeInTheDocument()
  })

  it('calls onFilterChange when search is clicked', () => {
    const handleFilterChange = vi.fn()
    render(<FilterBar filters={mockFilters} onFilterChange={handleFilterChange} />)
    
    const searchButton = screen.getByText(/search/i)
    fireEvent.click(searchButton)
    
    expect(handleFilterChange).toHaveBeenCalled()
  })

  it('updates local filter state on input change', () => {
    render(<FilterBar filters={mockFilters} onFilterChange={() => {}} />)
    
    const searchInput = screen.getByPlaceholderText(/search games/i)
    fireEvent.change(searchInput, { target: { value: 'test query' } })
    
    expect(searchInput.value).toBe('test query')
  })

  it('resets filters when reset is clicked', () => {
    const handleFilterChange = vi.fn()
    render(<FilterBar filters={{ ...mockFilters, search: 'test' }} onFilterChange={handleFilterChange} />)
    
    const resetButton = screen.getByText(/reset/i)
    fireEvent.click(resetButton)
    
    expect(handleFilterChange).toHaveBeenCalledWith({
      search: '',
      genres: '',
      platforms: '',
      release_filter: 'both'
    })
  })
})

describe('GameModal Component', () => {
  const mockGame = {
    id: 1,
    name: 'Modal Test Game',
    background_image: 'https://example.com/image.jpg',
    rating: 4.5,
    released: '2024-01-01',
    genres: [{ id: 1, name: 'Action' }],
    platforms: [{ platform: { id: 1, name: 'PC' } }]
  }

  it('renders game modal with details', async () => {
    const handleClose = vi.fn()
    renderWithRouter(<GameModal game={mockGame} onClose={handleClose} />)
    
    await waitFor(() => {
      expect(screen.getByText('Modal Test Game')).toBeInTheDocument()
    })
  })

  it('closes modal when close button is clicked', async () => {
    const handleClose = vi.fn()
    renderWithRouter(<GameModal game={mockGame} onClose={handleClose} />)
    
    await waitFor(() => {
      const closeButton = screen.getByText('✕')
      fireEvent.click(closeButton)
      expect(handleClose).toHaveBeenCalled()
    })
  })

  it('displays wishlist and played buttons', async () => {
    renderWithRouter(<GameModal game={mockGame} onClose={() => {}} />)
    
    await waitFor(() => {
      expect(screen.getByText(/add to wishlist/i)).toBeInTheDocument()
      expect(screen.getByText(/mark as played/i)).toBeInTheDocument()
    })
  })
})
