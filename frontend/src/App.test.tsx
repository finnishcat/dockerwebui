/**
 * Tests for the main App component
 */
import { render, screen } from "@testing-library/react";
import App from "./App";

// Mock child components to simplify testing
jest.mock("./pages/Login", () => () => <div>Login Page</div>);
jest.mock("./pages/Register", () => () => <div>Register Page</div>);
jest.mock("./pages/Dashboard", () => () => <div>Dashboard Page</div>);
jest.mock("./pages/ContainerDetails", () => () => <div>Container Details Page</div>);
jest.mock("./pages/Images", () => () => <div>Images Page</div>);

describe("App Component", () => {
  test("renders without crashing", () => {
    render(<App />);
    // Should render the root route (Login)
    expect(screen.getByText(/Login Page/i)).toBeInTheDocument();
  });
});
