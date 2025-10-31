/**
 * Comprehensive tests for the Login component
 */
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Login from "./Login";
import { BrowserRouter } from "react-router-dom";

// Mock useNavigate
const mockedNavigate = jest.fn();
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockedNavigate,
}));

// Mock fetch
global.fetch = jest.fn();

describe("Login Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    (global.fetch as jest.Mock).mockClear();
  });

  test("renders login form with all elements", () => {
    render(<BrowserRouter><Login /></BrowserRouter>);
    
    // Check heading
    expect(screen.getByRole('heading', { name: /sign in to dockerwebui/i })).toBeInTheDocument();
    
    // Check input fields
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    
    // Check login button
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
    
    // Check help link
    expect(screen.getByText(/need help\?/i)).toBeInTheDocument();
  });

  test("allows user to type in username and password fields", async () => {
    const user = userEvent.setup();
    render(<BrowserRouter><Login /></BrowserRouter>);
    
    const usernameInput = screen.getByLabelText(/username/i) as HTMLInputElement;
    const passwordInput = screen.getByLabelText(/password/i) as HTMLInputElement;
    
    await user.type(usernameInput, "testuser");
    await user.type(passwordInput, "testpass");
    
    expect(usernameInput.value).toBe("testuser");
    expect(passwordInput.value).toBe("testpass");
  });

  test("successful login stores token and navigates to dashboard", async () => {
    const user = userEvent.setup();
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      json: async () => ({ access_token: "test-token" }),
      ok: true,
    });

    render(<BrowserRouter><Login /></BrowserRouter>);
    
    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const loginButton = screen.getByRole('button', { name: /login/i });
    
    await user.type(usernameInput, "admin");
    await user.type(passwordInput, "admin");
    await user.click(loginButton);
    
    await waitFor(() => {
      expect(localStorage.getItem("token")).toBe("test-token");
      expect(mockedNavigate).toHaveBeenCalledWith("/dashboard");
    });
  });

  test("failed login shows error message", async () => {
    const user = userEvent.setup();
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      json: async () => ({ detail: "Invalid credentials" }),
      ok: false,
    });

    render(<BrowserRouter><Login /></BrowserRouter>);
    
    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const loginButton = screen.getByRole('button', { name: /login/i });
    
    await user.type(usernameInput, "wronguser");
    await user.type(passwordInput, "wrongpass");
    await user.click(loginButton);
    
    await waitFor(() => {
      expect(screen.getByText(/login failed/i)).toBeInTheDocument();
    });
  });

  test("pressing Enter in password field triggers login", async () => {
    const user = userEvent.setup();
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      json: async () => ({ access_token: "test-token" }),
      ok: true,
    });

    render(<BrowserRouter><Login /></BrowserRouter>);
    
    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    
    await user.type(usernameInput, "admin");
    await user.type(passwordInput, "admin");
    
    // Simulate pressing Enter in password field
    fireEvent.keyDown(passwordInput, { key: 'Enter', code: 'Enter' });
    
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });
  });

  test("password field is of type password", () => {
    render(<BrowserRouter><Login /></BrowserRouter>);
    const passwordInput = screen.getByLabelText(/password/i);
    expect(passwordInput).toHaveAttribute("type", "password");
  });
});