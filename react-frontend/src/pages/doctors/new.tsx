import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import DoctorForm from '@/components/doctors/DoctorForm';
import PageLayout from '@/components/layout/PageLayout';
// import { addDoctor } from '@/data/mockData';
import { toast } from 'sonner';

const NewDoctorPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = (formData: unknown) => {
    console.log("The form data submitted is", formData)
    setIsLoading(true);

    try {
      // Add a small delay to simulate API call
      setTimeout(() => {

        // toast.success({`Dr. ${formData.firstName} ${formData.lastName} has been registered`);

        navigate('/doctors');
      }, 1000);
    } catch (error) {
      console.error("Error creating doctor account", error)
      toast.error("Failed to register doctor. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <PageLayout>
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">Register New Doctor</h1>
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <DoctorForm onSubmit={handleSubmit} isLoading={isLoading} />
        </div>
      </div>
    </PageLayout>
  );
};

export default NewDoctorPage;