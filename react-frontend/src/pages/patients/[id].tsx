import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import PageLayout from '@/components/layout/PageLayout';
import { patients, getPatientAppointments } from '@/data/mockData';
import { Patient, Appointment } from '@/types';
import { Calendar, FileText, Mail, MapPin, Phone, User } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import AppointmentCard from '@/components/appointments/AppointmentCard';
import { toast } from 'sonner';

const PatientDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [patient, setPatient] = useState<Patient | null>(null);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  // const { toast } = useToast();

  useEffect(() => {
    if (id) {
      const foundPatient = patients.find(p => p.id === id);
      if (foundPatient) {
        setPatient(foundPatient);

        // Get patient appointments
        const patientAppointments = getPatientAppointments(id);
        setAppointments(patientAppointments);
      } else {
        toast.error("Error", {
          description: "Patient not found",
        });
        navigate('/patients');
      }
    }
  }, [id, navigate]);

  if (!patient) {
    return (
      <PageLayout>
        <div className="text-center py-10">
          <h2 className="text-xl font-semibold">Loading patient information...</h2>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <div className="mb-6 flex flex-col sm:flex-row justify-between items-start gap-4">
        <div>
          <h1 className="text-2xl font-bold">
            {patient.firstName} {patient.lastName}
          </h1>
          <p className="text-gray-500">Patient ID: {patient.id}</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" asChild>
            <Link to="/patients">Back to Patients</Link>
          </Button>
          <Button asChild>
            <Link to={`/appointments/new?patientId=${patient.id}`}>
              Schedule Appointment
            </Link>
          </Button>
        </div>
      </div>

      <Tabs defaultValue="details">
        <TabsList className="mb-6">
          <TabsTrigger value="details">Patient Details</TabsTrigger>
          <TabsTrigger value="appointments">Appointments</TabsTrigger>
        </TabsList>

        <TabsContent value="details">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Personal Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="flex items-start space-x-3">
                    <User className="h-5 w-5 mt-0.5 text-gray-500" />
                    <div>
                      <div className="font-medium">Full Name</div>
                      <span className="text-gray-700">
                        {patient.firstName} {patient.lastName}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-start space-x-3">
                    <Calendar className="h-5 w-5 mt-0.5 text-gray-500" />
                    <div>
                      <div className="font-medium">Date of Birth</div>
                      <span className="text-gray-700">
                        {new Date(patient.dateOfBirth).toLocaleDateString()}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-start space-x-3">
                    <Phone className="h-5 w-5 mt-0.5 text-gray-500" />
                    <div>
                      <div className="font-medium">Phone</div>
                      <span className="text-gray-700">{patient.phone}</span>
                    </div>
                  </div>

                  <div className="flex items-start space-x-3">
                    <Mail className="h-5 w-5 mt-0.5 text-gray-500" />
                    <div>
                      <div className="font-medium">Email</div>
                      <span className="text-gray-700">{patient.email}</span>
                    </div>
                  </div>

                  <div className="flex items-start space-x-3 sm:col-span-2">
                    <MapPin className="h-5 w-5 mt-0.5 text-gray-500" />
                    <div>
                      <div className="font-medium">Address</div>
                      <span className="text-gray-700">{patient.address}</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Insurance Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start space-x-3">
                  <FileText className="h-5 w-5 mt-0.5 text-gray-500" />
                  <div>
                    <div className="font-medium">Insurance Provider</div>
                    <span className="text-gray-700">
                      {patient.insuranceProvider || 'Not provided'}
                    </span>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <FileText className="h-5 w-5 mt-0.5 text-gray-500" />
                  <div>
                    <div className="font-medium">Insurance ID</div>
                    <span className="text-gray-700">
                      {patient.insuranceId || 'Not provided'}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="lg:col-span-3">
              <CardHeader>
                <CardTitle>Medical History</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 whitespace-pre-wrap">
                  {patient.medicalHistory || 'No medical history recorded.'}
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="appointments">
          {appointments.length === 0 ? (
            <div className="text-center py-10">
              <h2 className="text-xl font-semibold mb-2">No appointments found</h2>
              <p className="text-gray-500 mb-4">
                This patient doesn't have any appointments scheduled
              </p>
              <Button asChild>
                <Link to={`/appointments/new?patientId=${patient.id}`}>
                  Schedule New Appointment
                </Link>
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {appointments.map((appointment) => (
                <AppointmentCard key={appointment.id} appointment={appointment} />
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </PageLayout>
  );
};

export default PatientDetailPage;