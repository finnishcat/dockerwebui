/**
 * Comprehensive tests for the Dashboard component
 */
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Dashboard from "./Dashboard";
import { BrowserRouter } from "react-router-dom";

// Mock useNavigate
const mockedNavigate = jest.fn();
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockedNavigate,
}));

// Mock fetch
global.fetch = jest.fn();

describe("Dashboard Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.setItem("token", "test-token");
    (global.fetch as jest.Mock).mockClear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  test("renders dashboard title", () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    });

    render(<BrowserRouter><Dashboard /></BrowserRouter>);
    expect(screen.getByText(/Active Containers/i)).toBeInTheDocument();
  });

  test("shows loading state initially", () => {
    (global.fetch as jest.Mock).mockImplementation(() => new Promise(() => {}));

    render(<BrowserRouter><Dashboard /></BrowserRouter>);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test("displays containers when fetch succeeds", async () => {
    const mockContainers = [
      { id: "abc123", name: "test-container-1", image: ["nginx:latest"], status: "running" },
      { id: "def456", name: "test-container-2", image: ["redis:alpine"], status: "stopped" },
    ];

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockContainers,
    });

    render(<BrowserRouter><Dashboard /></BrowserRouter>);

    await waitFor(() => {
      expect(screen.getByText("test-container-1")).toBeInTheDocument();
      expect(screen.getByText("test-container-2")).toBeInTheDocument();
    });
  });

  test("displays error message when fetch fails", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: "Unauthorized" }),
    });

    render(<BrowserRouter><Dashboard /></BrowserRouter>);

    await waitFor(() => {
      expect(screen.getByText(/error loading containers/i)).toBeInTheDocument();
    });
  });

  test("navigates to container details when container is clicked", async () => {
    const user = userEvent.setup();
    const mockContainers = [
      { id: "abc123", name: "test-container", image: ["nginx:latest"], status: "running" },
    ];

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockContainers,
    });

    render(<BrowserRouter><Dashboard /></BrowserRouter>);

    await waitFor(() => {
      expect(screen.getByText("test-container")).toBeInTheDocument();
    });

    const containerCard = screen.getByText("test-container").closest("div");
    if (containerCard) {
      await user.click(containerCard);
      expect(mockedNavigate).toHaveBeenCalledWith("/container/abc123");
    }
  });

  test("fetches containers with correct authorization header", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    });

    render(<BrowserRouter><Dashboard /></BrowserRouter>);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/docker/containers/local"),
        expect.objectContaining({
          headers: { Authorization: "Bearer test-token" },
        })
      );
    });
  });

  test("shows empty state when no containers exist", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    });

    render(<BrowserRouter><Dashboard /></BrowserRouter>);

    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
  });
});