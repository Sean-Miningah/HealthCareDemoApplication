import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import PageLayout from '@/components/layout/PageLayout';
import { getAppointmentDetails, updateAppointmentStatus } from '@/data/mockData';
import { Appointment, Doctor, Patient, AppointmentStatus } from '@/types';
import { Calendar, Clock, FileText, User } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { format } from 'date-fns';
import { toast } from 'sonner';

const AppointmentDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [appointment, setAppointment] = useState<Appointment | null>(null);
  const [doctor, setDoctor] = useState<Doctor | null>(null);
  const [patient, setPatient] = useState<Patient | null>(null);

  useEffect(() => {
    if (id) {
      const result = getAppointmentDetails(id);

      if ('error' in result) {
        toast.error(result.error)
        navigate('/appointments');
        return;
      }

      setAppointment(result.appointment);
      setDoctor(result.doctor);
      setPatient(result.patient);
    }
  }, [id, navigate]);

  const handleStatusChange = (status: AppointmentStatus) => {
    if (!id) return;

    const result = updateAppointmentStatus(id, status);

    if ('error' in result) {
      toast.error(result.error,);
      return;
    }

    setAppointment(result);

    toast.success(`Appointment status changed to ${status}`);
  };

  if (!appointment || !doctor || !patient) {
    return (
      <PageLayout>
        <div className="text-center py-10">
          <h2 className="text-xl font-semibold">Loading appointment information...</h2>
        </div>
      </PageLayout>
    );
  }

  const formattedDate = format(new Date(appointment.date), 'EEEE, MMMM d, yyyy');

  // Helper function to determine badge color based on status
  const getStatusBadge = () => {
    switch (appointment.status) {
      case 'scheduled':
        return <Badge className="bg-blue-500">Scheduled</Badge>;
      case 'completed':
        return <Badge className="bg-green-500">Completed</Badge>;
      case 'cancelled':
        return <Badge className="bg-red-500">Cancelled</Badge>;
      default:
        return <Badge>Unknown</Badge>;
    }
  };

  return (
    <PageLayout>
      <div className="mb-6 flex flex-col sm:flex-row justify-between items-start gap-4">
        <div>
          <h1 className="text-2xl font-bold">Appointment Details</h1>
          <div className="mt-2">{getStatusBadge()}</div>
        </div>
        <Button variant="outline" asChild>
          <Link to="/appointments">Back to Appointments</Link>
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Appointment Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start space-x-3">
              <Calendar className="h-5 w-5 mt-0.5 text-gray-500" />
              <div>
                <div className="font-medium">Date</div>
                <span className="text-gray-700">{formattedDate}</span>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <Clock className="h-5 w-5 mt-0.5 text-gray-500" />
              <div>
                <div className="font-medium">Time</div>
                <span className="text-gray-700">
                  {appointment.startTime} - {appointment.endTime}
                </span>
              </div>
            </div>

            {appointment.notes && (
              <div className="flex items-start space-x-3">
                <FileText className="h-5 w-5 mt-0.5 text-gray-500" />
                <div>
                  <div className="font-medium">Notes</div>
                  <p className="text-gray-700 whitespace-pre-wrap">{appointment.notes}</p>
                </div>
              </div>
            )}

            {appointment.status === 'scheduled' && (
              <div className="flex flex-col sm:flex-row gap-3 mt-6">
                <Button
                  variant="default"
                  className="bg-green-500 hover:bg-green-600"
                  onClick={() => handleStatusChange('completed')}
                >
                  Mark as Completed
                </Button>
                <Button
                  variant="destructive"
                  onClick={() => handleStatusChange('cancelled')}
                >
                  Cancel Appointment
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Patient Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-start space-x-3">
                <User className="h-5 w-5 mt-0.5 text-gray-500" />
                <div>
                  <div className="font-medium">Name</div>
                  <Link
                    to={`/patients/${patient.id}`}
                    className="text-primary hover:underline"
                  >
                    {patient.firstName} {patient.lastName}
                  </Link>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="font-medium">Phone</div>
                  <span className="text-gray-700">{patient.phone}</span>
                </div>

                <div>
                  <div className="font-medium">Email</div>
                  <span className="text-gray-700">{patient.email}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Doctor Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-start space-x-3">
                <User className="h-5 w-5 mt-0.5 text-gray-500" />
                <div>
                  <div className="font-medium">Name</div>
                  <Link
                    to={`/doctors/${doctor.id}`}
                    className="text-primary hover:underline"
                  >
                    Dr. {doctor.firstName} {doctor.lastName}
                  </Link>
                  <div className="text-sm text-gray-500">{doctor.specialization}</div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="font-medium">Phone</div>
                  <span className="text-gray-700">{doctor.phone}</span>
                </div>

                <div>
                  <div className="font-medium">Email</div>
                  <span className="text-gray-700">{doctor.email}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </PageLayout>
  );
};

export default AppointmentDetailPage;