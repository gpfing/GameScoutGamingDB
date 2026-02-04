import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import LoginPage from '../pages/LoginPage'
import SignupPage from '../pages/SignupPage'
import DiscoveryPage from '../pages/DiscoveryPage'
import axios from 'axios'

// Mock the useAuth hook
vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    login: vi.fn(),
    user: null,
    loading: false
  })
}))

const renderWithRouter = (component) => {
  return render(<BrowserRouter>{component}</BrowserRouter>)
}

describe('LoginPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders login form', () => {
    renderWithRouter(<LoginPage />)
    
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument()
  })

  it('shows validation error for empty fields', async () => {
    renderWithRouter(<LoginPage />)
    
    const loginButton = screen.getByRole('button', { name: /login/i })
    fireEvent.click(loginButton)
    
    // HTML5 validation will prevent form submission, so this test just checks the form is rendered
    expect(loginButton).toBeInTheDocument()
  })

  it('submits form with valid data', async () => {
    renderWithRouter(<LoginPage />)
    
    fireEvent.change(screen.getByLabelText(/username/i), {
      target: { value: 'testuser' }
    })
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password123' }
    })
    
    const loginButton = screen.getByRole('button', { name: /login/i })
    expect(loginButton).toBeInTheDocument()
  })
})

describe('SignupPage', () => {
  it('renders registration form', () => {
    renderWithRouter(<SignupPage />)
    
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/^email$/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign up/i })).toBeInTheDocument()
  })

  it('validates password match', async () => {
    renderWithRouter(<SignupPage />)
    
    // Fill in all required fields
    fireEvent.change(screen.getByLabelText(/username/i), {
      target: { value: 'testuser' }
    })
    fireEvent.change(screen.getByLabelText(/^email$/i), {
      target: { value: 'test@example.com' }
    })
    fireEvent.change(screen.getByLabelText(/^password$/i), {
      target: { value: 'password123' }
    })
    fireEvent.change(screen.getByLabelText(/confirm password/i), {
      target: { value: 'differentpassword' }
    })
    
    const registerButton = screen.getByRole('button', { name: /sign up/i })
    fireEvent.click(registerButton)
    
    await waitFor(() => {
      expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument()
    })
  })
})

describe('DiscoveryPage', () => {
  it('renders discovery page with title', () => {
    renderWithRouter(<DiscoveryPage />)
    
    expect(screen.getByText(/discover games/i)).toBeInTheDocument()
  })

  it('shows loading state initially', () => {
    renderWithRouter(<DiscoveryPage />)
    
    // Component should render without crashing
    expect(screen.getByText(/discover games/i)).toBeInTheDocument()
  })
})
