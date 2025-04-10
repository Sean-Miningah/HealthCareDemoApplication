import { useState } from 'react';
// import { useNavigate } from 'react-router-dom';
import PatientForm from '@/components/patients/PatientForm';
import PageLayout from '@/components/layout/PageLayout';
import { toast } from "sonner";

const NewPatientPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  // const navigate = useNavigate();

  const handleSubmit = (formData: unknown) => {
    setIsLoading(true);

    try {
      console.log(formData)
    } catch (error) {
      console.error("Registration failed:", error);
      toast.error("Failed to register patient. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <PageLayout>
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">Register New Patient</h1>
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <PatientForm onSubmit={handleSubmit} isLoading={isLoading} />
        </div>
      </div>
    </PageLayout>
  );
};

export default NewPatientPage;
