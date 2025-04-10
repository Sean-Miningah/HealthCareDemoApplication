import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router";
import Index from "@/pages/index";
import NotFound from "@/pages/NotFound";

const queryClient = new QueryClient();

// Patient routes
import PatientsPage from "@/pages/patients/index";
import NewPatientPage from "@/pages/patients/new";
import PatientDetailPage from "@/pages/patients/[id]";

// Doctor routes
import DoctorsPage from "./pages/doctors/index";
import NewDoctorPage from "./pages/doctors/new";
import DoctorDetailPage from "./pages/doctors/[id]";

// Create router with route definitions
const router = createBrowserRouter([
  {
    path: "/",
    element: <Index />,
  },
  {
    path: "*",
    element: <NotFound />,
  },
  {
    path: "/patients",
    element: <PatientsPage />
  },
  {
    path: "/patients/:id",
    element: <PatientDetailPage />
  },
  {
    path: "/patients/new",
    element: <NewPatientPage />
  },
  {
    path: "/doctors",
    element: <DoctorsPage />
  },
  {
    path: "/doctors/:id",
    element: <DoctorDetailPage />
  },
  {
    path: "doctors/new",
    element: <NewDoctorPage />
  }
]);

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <RouterProvider router={router} />
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;