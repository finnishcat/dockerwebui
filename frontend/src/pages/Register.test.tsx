/**
 * Tests for the Register component
 */
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Register from "./Register";
import { BrowserRouter } from "react-router-dom";

// Mock useNavigate
const mockedNavigate = jest.fn();
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockedNavigate,
}));

// Mock fetch
global.fetch = jest.fn();

describe("Register Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockClear();
  });

  test("renders register form", () => {
    render(<BrowserRouter><Register /></BrowserRouter>);
    
    expect(screen.getByRole("heading", { name: /create admin/i })).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/username/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /create admin/i })).toBeInTheDocument();
  });

  test("allows user to type in username and password fields", async () => {
    const user = userEvent.setup();
    render(<BrowserRouter><Register /></BrowserRouter>);
    
    const usernameInput = screen.getByPlaceholderText(/username/i) as HTMLInputElement;
    const passwordInput = screen.getByPlaceholderText(/password/i) as HTMLInputElement;
    
    await user.type(usernameInput, "admin");
    await user.type(passwordInput, "password123");
    
    expect(usernameInput.value).toBe("admin");
    expect(passwordInput.value).toBe("password123");
  });

  test("successful registration shows success message", async () => {
    const user = userEvent.setup();
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ msg: "Admin user created" }),
    });

    const { container } = render(<BrowserRouter><Register /></BrowserRouter>);
    
    const usernameInput = screen.getByPlaceholderText(/username/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const registerButton = screen.getByRole("button", { name: /create admin/i });
    
    await user.type(usernameInput, "admin");
    await user.type(passwordInput, "password123");
    
    // Trigger the click and wait for state update
    await user.click(registerButton);
    
    // Wait for success message to appear
    await waitFor(() => {
      const successElement = screen.queryByText(/admin user created/i);
      expect(successElement).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  test("failed registration shows error message", async () => {
    const user = userEvent.setup();
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: "Registration not allowed: a user already exists." }),
    });

    render(<BrowserRouter><Register /></BrowserRouter>);
    
    const usernameInput = screen.getByPlaceholderText(/username/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const registerButton = screen.getByRole("button", { name: /create admin/i });
    
    await user.type(usernameInput, "admin");
    await user.type(passwordInput, "password123");
    await user.click(registerButton);
    
    await waitFor(() => {
      expect(screen.getByText(/registration not allowed/i)).toBeInTheDocument();
    });
  });

  test("clears previous error/success messages on new submission", async () => {
    const user = userEvent.setup();
    
    // First call fails
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: "Error" }),
    });

    render(<BrowserRouter><Register /></BrowserRouter>);
    
    const usernameInput = screen.getByPlaceholderText(/username/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const registerButton = screen.getByRole("button", { name: /create admin/i });
    
    await user.type(usernameInput, "admin");
    await user.type(passwordInput, "pass");
    await user.click(registerButton);
    
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
    
    // Second call succeeds
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ msg: "Success" }),
    });
    
    await user.clear(passwordInput);
    await user.type(passwordInput, "newpassword");
    await user.click(registerButton);
    
    await waitFor(() => {
      expect(screen.queryByText(/error/i)).not.toBeInTheDocument();
      expect(screen.getByText(/admin user created/i)).toBeInTheDocument();
    });
  });
});
