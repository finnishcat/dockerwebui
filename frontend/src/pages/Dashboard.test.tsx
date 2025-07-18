import { render, screen } from "@testing-library/react";
import Dashboard from "./Dashboard";
import { BrowserRouter } from "react-router-dom";

test("renders dashboard title", () => {
  render(<BrowserRouter><Dashboard /></BrowserRouter>);
  expect(screen.getByText(/Active Containers/i)).toBeInTheDocument();
});