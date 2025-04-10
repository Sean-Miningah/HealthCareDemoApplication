import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import PageLayout from '@/components/layout/PageLayout';
import { doctors, getDoctorAppointments } from '@/data/mockData';
import { Doctor, Appointment } from '@/types';
import { Award, Briefcase, Calendar, Mail, Phone, User } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import AppointmentCard from '@/components/appointments/AppointmentCard';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';

const DoctorDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [doctor, setDoctor] = useState<Doctor | null>(null);
  const [appointments, setAppointments] = useState<Appointment[]>([]);

  useEffect(() => {
    if (id) {
      const foundDoctor = doctors.find(d => d.id === id);
      if (foundDoctor) {
        setDoctor(foundDoctor);

        // Get doctor appointments
        const doctorAppointments = getDoctorAppointments(id);
        setAppointments(doctorAppointments);
      } else {
        toast.error("Doctor not found");
        navigate('/doctors');
      }
    }
  }, [id, navigate]);

  if (!doctor) {
    return (
      <PageLayout>
        <div className="text-center py-10">
          <h2 className="text-xl font-semibold">Loading doctor information...</h2>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <div className="mb-6 flex flex-col sm:flex-row justify-between items-start gap-4">
        <div>
          <h1 className="text-2xl font-bold">
            Dr. {doctor.firstName} {doctor.lastName}
          </h1>
          <p className="text-gray-500">{doctor.specialization}</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" asChild>
            <Link to="/doctors">Back to Doctors</Link>
          </Button>
          <Button asChild>
            <Link to={`/appointments/new?doctorId=${doctor.id}`}>
              Schedule Appointment
            </Link>
          </Button>
        </div>
      </div>

      <Tabs defaultValue="details">
        <TabsList className="mb-6">
          <TabsTrigger value="details">Doctor Details</TabsTrigger>
          <TabsTrigger value="appointments">Appointments</TabsTrigger>
        </TabsList>

        <TabsContent value="details">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Professional Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="flex items-start space-x-3">
                    <User className="h-5 w-5 mt-0.5 text-gray-500" />
                    <div>
                      <div className="font-medium">Full Name</div>
                      <span className="text-gray-700">
                        Dr. {doctor.firstName} {doctor.lastName}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-start space-x-3">
                    <Briefcase className="h-5 w-5 mt-0.5 text-gray-500" />
                    <div>
                      <div className="font-medium">Specialization</div>
                      <span className="text-gray-700">{doctor.specialization}</span>
                    </div>
                  </div>

                  <div className="flex items-start space-x-3">
                    <Phone className="h-5 w-5 mt-0.5 text-gray-500" />
                    <div>
                      <div className="font-medium">Phone</div>
                      <span className="text-gray-700">{doctor.phone}</span>
                    </div>
                  </div>

                  <div className="flex items-start space-x-3">
                    <Mail className="h-5 w-5 mt-0.5 text-gray-500" />
                    <div>
                      <div className="font-medium">Email</div>
                      <span className="text-gray-700">{doctor.email}</span>
                    </div>
                  </div>

                  <div className="flex items-start space-x-3 sm:col-span-2">
                    <Award className="h-5 w-5 mt-0.5 text-gray-500" />
                    <div>
                      <div className="font-medium">Qualifications</div>
                      <span className="text-gray-700">{doctor.qualifications}</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Availability Schedule</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {doctor.availability.length === 0 ? (
                    <p className="text-gray-500">No availability set</p>
                  ) : (
                    doctor.availability.map((slot, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Calendar className="h-4 w-4 text-gray-500" />
                          <span className="font-medium">{slot.day}</span>
                        </div>
                        <Badge variant="outline" className="ml-auto">
                          {slot.startTime} - {slot.endTime}
                        </Badge>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="appointments">
          {appointments.length === 0 ? (
            <div className="text-center py-10">
              <h2 className="text-xl font-semibold mb-2">No appointments found</h2>
              <p className="text-gray-500 mb-4">
                This doctor doesn't have any appointments scheduled
              </p>
              <Button asChild>
                <Link to={`/appointments/new?doctorId=${doctor.id}`}>
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

export default DoctorDetailPage;