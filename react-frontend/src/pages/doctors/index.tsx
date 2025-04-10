import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Link } from 'react-router-dom';
import { doctors } from '@/data/mockData';
import DoctorCard from '@/components/doctors/DoctorCard';
import PageLayout from '@/components/layout/PageLayout';
import { Plus, Search } from 'lucide-react';

const DoctorsPage = () => {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredDoctors = doctors.filter(doctor => {
    const fullName = `${doctor.firstName} ${doctor.lastName}`.toLowerCase();
    return fullName.includes(searchQuery.toLowerCase()) ||
      doctor.specialization.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doctor.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doctor.phone.includes(searchQuery);
  });

  return (
    <PageLayout>
      <div className="flex flex-col md:flex-row justify-between items-center mb-6">
        <h1 className="text-2xl font-bold mb-4 md:mb-0">Doctors</h1>
        <Button asChild>
          <Link to="/doctors/new">
            <Plus className="mr-2 h-4 w-4" /> Add New Doctor
          </Link>
        </Button>
      </div>

      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
        <Input
          placeholder="Search doctors by name, specialization, or contact info..."
          className="pl-10"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {filteredDoctors.length === 0 ? (
        <div className="text-center py-10">
          <h2 className="text-xl font-semibold mb-2">No doctors found</h2>
          <p className="text-gray-500 mb-4">
            {searchQuery ? 'Try a different search term' : 'Start by adding a new doctor'}
          </p>
          <Button asChild>
            <Link to="/doctors/new">
              <Plus className="mr-2 h-4 w-4" /> Add New Doctor
            </Link>
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredDoctors.map((doctor) => (
            <DoctorCard key={doctor.id} doctor={doctor} />
          ))}
        </div>
      )}
    </PageLayout>
  );
};

export default DoctorsPage;