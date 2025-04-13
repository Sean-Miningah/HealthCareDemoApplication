import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Link } from 'react-router-dom';
import { appointments, doctors, patients, updateAppointmentStatus } from '@/data/mockData';
import { Appointment, AppointmentStatus } from '@/types';
import AppointmentCard from '@/components/appointments/AppointmentCard';
import PageLayout from '@/components/layout/PageLayout';
import { Plus, Search } from 'lucide-react';
import { toast } from 'sonner';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

const AppointmentsPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<AppointmentStatus | 'all'>('all');
  const [localAppointments, setLocalAppointments] = useState<Appointment[]>(appointments);

  const filteredAppointments = localAppointments.filter(appointment => {
    // Filter by status
    if (statusFilter !== 'all' && appointment.status !== statusFilter) {
      return false;
    }

    // Get patient and doctor for this appointment
    const patient = patients.find(p => p.id === appointment.patientId);
    const doctor = doctors.find(d => d.id === appointment.doctorId);

    if (!patient || !doctor) return false;

    const patientName = `${patient.firstName} ${patient.lastName}`.toLowerCase();
    const doctorName = `${doctor.firstName} ${doctor.lastName}`.toLowerCase();

    // Search in patient name, doctor name, or date
    return patientName.includes(searchQuery.toLowerCase()) ||
      doctorName.includes(searchQuery.toLowerCase()) ||
      appointment.date.includes(searchQuery) ||
      appointment.startTime.includes(searchQuery);
  });

  const handleStatusChange = (id: string, status: AppointmentStatus) => {
    const result = updateAppointmentStatus(id, status);

    if ('error' in result) {
      toast.error(result.error);
    } else {
      setLocalAppointments(prevAppointments =>
        prevAppointments.map(a => a.id === id ? { ...a, status } : a)
      );

      toast.error(`Appointment status changed to ${status}`);
    }
  };

  return (
    <PageLayout>
      <div className="flex flex-col md:flex-row justify-between items-center mb-6">
        <h1 className="text-2xl font-bold mb-4 md:mb-0">Appointments</h1>
        <Button asChild>
          <Link to="/appointments/new">
            <Plus className="mr-2 h-4 w-4" /> New Appointment
          </Link>
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="md:col-span-3 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
          <Input
            placeholder="Search by patient, doctor or date..."
            className="pl-10"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Select
          value={statusFilter}
          onValueChange={(value) => setStatusFilter(value as AppointmentStatus | 'all')}
        >
          <SelectTrigger>
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="scheduled">Scheduled</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="cancelled">Cancelled</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {filteredAppointments.length === 0 ? (
        <div className="text-center py-10">
          <h2 className="text-xl font-semibold mb-2">No appointments found</h2>
          <p className="text-gray-500 mb-4">
            {searchQuery || statusFilter !== 'all'
              ? 'Try different filters or search terms'
              : 'Start by creating a new appointment'}
          </p>
          <Button asChild>
            <Link to="/appointments/new">
              <Plus className="mr-2 h-4 w-4" /> New Appointment
            </Link>
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredAppointments.map((appointment) => (
            <AppointmentCard
              key={appointment.id}
              appointment={appointment}
              onStatusChange={handleStatusChange}
            />
          ))}
        </div>
      )}
    </PageLayout>
  );
};

export default AppointmentsPage;