/**
 * Tests for the RequireAuth component
 */
import { render, screen } from "@testing-library/react";
import RequireAuth from "./RequireAuth";
import { MemoryRouter, Route, Routes } from "react-router-dom";

describe("RequireAuth Component", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  test("redirects to login if no token is present", () => {
    localStorage.removeItem("token");
    
    render(
      <MemoryRouter initialEntries={["/dashboard"]}>
        <Routes>
          <Route path="/dashboard" element={<RequireAuth><div>Protected Content</div></RequireAuth>} />
          <Route path="/" element={<div>Login Page</div>} />
        </Routes>
      </MemoryRouter>
    );
    
    expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
  });

  test("renders children if token is present", () => {
    localStorage.setItem("token", "test-token");
    
    render(
      <MemoryRouter initialEntries={["/dashboard"]}>
        <Routes>
          <Route path="/dashboard" element={<RequireAuth><div>Protected Content</div></RequireAuth>} />
          <Route path="/" element={<div>Login Page</div>} />
        </Routes>
      </MemoryRouter>
    );
    
    expect(screen.getByText("Protected Content")).toBeInTheDocument();
  });

  test("protects multiple routes", () => {
    localStorage.setItem("token", "test-token");
    
    render(
      <MemoryRouter initialEntries={["/protected-route"]}>
        <Routes>
          <Route path="/protected-route" element={<RequireAuth><div>Protected Page</div></RequireAuth>} />
          <Route path="/" element={<div>Login Page</div>} />
        </Routes>
      </MemoryRouter>
    );
    
    expect(screen.getByText("Protected Page")).toBeInTheDocument();
  });
});