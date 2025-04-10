import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Link } from 'react-router-dom';
import { patients } from '@/data/mockData';
import PatientCard from '@/components/patients/PatientCard';
import PageLayout from '@/components/layout/PageLayout';
import { Plus, Search } from 'lucide-react';

const PatientsPage = () => {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredPatients = patients.filter(patient => {
    const fullName = `${patient.firstName} ${patient.lastName}`.toLowerCase();
    return fullName.includes(searchQuery.toLowerCase()) ||
      patient.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      patient.phone.includes(searchQuery);
  });

  return (
    <PageLayout>
      <div className="flex flex-col md:flex-row justify-between items-center mb-6">
        <h1 className="text-2xl font-bold mb-4 md:mb-0">Patients</h1>
        <Button asChild>
          <Link to="/patients/new">
            <Plus className="mr-2 h-4 w-4" /> Add New Patient
          </Link>
        </Button>
      </div>

      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
        <Input
          placeholder="Search patients by name, email, or phone..."
          className="pl-10"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {filteredPatients.length === 0 ? (
        <div className="text-center py-10">
          <h2 className="text-xl font-semibold mb-2">No patients found</h2>
          <p className="text-gray-500 mb-4">
            {searchQuery ? 'Try a different search term' : 'Start by adding a new patient'}
          </p>
          <Button asChild>
            <Link to="/patients/new">
              <Plus className="mr-2 h-4 w-4" /> Add New Patient
            </Link>
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPatients.map((patient) => (
            <PatientCard key={patient.id} patient={patient} />
          ))}
        </div>
      )}
    </PageLayout>
  );
};

export default PatientsPage;