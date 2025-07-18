import { render, screen, fireEvent } from "@testing-library/react";
import Login from "./Login";
import { BrowserRouter } from "react-router-dom";

test("renders login form", () => {
  render(<BrowserRouter><Login /></BrowserRouter>);
  expect(screen.getByText(/Login/i)).toBeInTheDocument();
  expect(screen.getByPlaceholderText(/Username/i)).toBeInTheDocument();
  expect(screen.getByPlaceholderText(/Password/i)).toBeInTheDocument();
});