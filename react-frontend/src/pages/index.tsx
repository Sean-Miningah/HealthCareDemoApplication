import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';
import PageLayout from '@/components/layout/PageLayout';
import { Calendar, Users, User } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

const Index = () => {
  return (
    <PageLayout>
      <section className="py-10">
        <div className="max-w-5xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4 text-primary">
            HealSync Healthcare
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            A comprehensive appointment scheduling system for healthcare providers
            that efficiently manages patient data and appointments.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Button size="lg" asChild>
              <Link to="/appointments/new">Schedule Appointment</Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link to="/patients">View Patients</Link>
            </Button>
          </div>
        </div>
      </section>

      <section className="py-12 bg-accent rounded-lg my-12">
        <div className="container">
          <h2 className="text-2xl md:text-3xl font-bold mb-8 text-center">
            Our Services
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Card>
              <CardHeader className="pb-2">
                <Calendar className="h-8 w-8 text-primary mb-2" />
                <CardTitle>Appointment Scheduling</CardTitle>
                <CardDescription>
                  Easily schedule, reschedule and manage appointments
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Our intuitive scheduling system prevents double-bookings and scheduling conflicts,
                  ensuring efficient use of time for both patients and healthcare providers.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <User className="h-8 w-8 text-primary mb-2" />
                <CardTitle>Patient Management</CardTitle>
                <CardDescription>
                  Comprehensive patient profiles and histories
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Securely store and manage patient information, including contact details,
                  medical history, and insurance information in one centralized location.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <Users className="h-8 w-8 text-primary mb-2" />
                <CardTitle>Doctor Management</CardTitle>
                <CardDescription>
                  Track availability and specializations
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Maintain detailed profiles for healthcare providers, including specializations,
                  qualifications, and availability schedules to streamline appointment booking.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      <section className="py-10">
        <div className="container">
          <h2 className="text-2xl md:text-3xl font-bold mb-8 text-center">
            Getting Started
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-xl font-semibold mb-4 flex items-center">
                <span className="bg-primary text-white rounded-full w-8 h-8 inline-flex items-center justify-center mr-3">1</span>
                Register Patients
              </h3>
              <p className="text-gray-600 mb-4">
                Start by adding patient profiles with their essential information, including
                contact details and insurance information.
              </p>
              <Button variant="outline" asChild>
                <Link to="/patients/new">Add New Patient</Link>
              </Button>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-xl font-semibold mb-4 flex items-center">
                <span className="bg-primary text-white rounded-full w-8 h-8 inline-flex items-center justify-center mr-3">2</span>
                Register Doctors
              </h3>
              <p className="text-gray-600 mb-4">
                Add doctor profiles with their specializations and set their availability
                schedules for appointment booking.
              </p>
              <Button variant="outline" asChild>
                <Link to="/doctors/new">Add New Doctor</Link>
              </Button>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-xl font-semibold mb-4 flex items-center">
                <span className="bg-primary text-white rounded-full w-8 h-8 inline-flex items-center justify-center mr-3">3</span>
                Set Availability
              </h3>
              <p className="text-gray-600 mb-4">
                Define when healthcare providers are available for appointments,
                ensuring accurate scheduling options for patients.
              </p>
              <Button variant="outline" asChild>
                <Link to="/doctors">Manage Doctors</Link>
              </Button>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-xl font-semibold mb-4 flex items-center">
                <span className="bg-primary text-white rounded-full w-8 h-8 inline-flex items-center justify-center mr-3">4</span>
                Schedule Appointments
              </h3>
              <p className="text-gray-600 mb-4">
                Book appointments between patients and doctors with automatic
                availability checking to prevent scheduling conflicts.
              </p>
              <Button variant="outline" asChild>
                <Link to="/appointments/new">New Appointment</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>
    </PageLayout>
  );
};

export default Index;
