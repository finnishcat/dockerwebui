import { render, screen } from "@testing-library/react";
import Login from "./Login";
import { BrowserRouter } from "react-router-dom";

test("renders login form", () => {
  render(<BrowserRouter><Login /></BrowserRouter>);
  // search title
  expect(screen.getByRole('heading', { name: /login/i })).toBeInTheDocument();
  // search username
  expect(screen.getByPlaceholderText(/Username/i)).toBeInTheDocument();
  // search password
  expect(screen.getByPlaceholderText(/Password/i)).toBeInTheDocument();
  // serch login button
  expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
});