import { render, screen } from "@testing-library/react";
import Login from "./Login";
import { BrowserRouter } from "react-router-dom";

test("renders login form", () => {
  render(<BrowserRouter><Login /></BrowserRouter>);
  // search title
  expect(screen.getByRole('heading', { name: /sign in to dockerwebui/i })).toBeInTheDocument();
  // search username label
  expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
  // search password label
  expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  // search login button
  expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
});