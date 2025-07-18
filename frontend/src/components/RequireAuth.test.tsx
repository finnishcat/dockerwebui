import { render, screen } from "@testing-library/react";
import RequireAuth from "./RequireAuth";
import { MemoryRouter } from "react-router-dom";

test("redirects if no token", () => {
  localStorage.removeItem("token");
  render(
    <MemoryRouter initialEntries={["/dashboard"]}>
      <RequireAuth><div>Protected</div></RequireAuth>
    </MemoryRouter>
  );
  expect(screen.queryByText("Protected")).not.toBeInTheDocument();
});