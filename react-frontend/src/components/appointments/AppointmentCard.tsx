import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Calendar, Clock, User, FileText } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Appointment } from '@/types';
import { Badge } from '@/components/ui/badge';
import { format } from 'date-fns';
import { doctors, patients } from '@/data/mockData';

interface AppointmentCardProps {
  appointment: Appointment;
  onStatusChange?: (id: string, status: 'scheduled' | 'completed' | 'cancelled') => void;
}

const AppointmentCard = ({ appointment, onStatusChange }: AppointmentCardProps) => {
  const doctor = doctors.find(d => d.id === appointment.doctorId);
  const patient = patients.find(p => p.id === appointment.patientId);

  if (!doctor || !patient) return null;

  const formattedDate = format(new Date(appointment.date), 'EEE, MMM d, yyyy');

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
    <Card className="h-full">
      <CardHeader className="pb-2">
        <div className="flex justify-between items-start">
          <CardTitle className="text-lg">Appointment</CardTitle>
          {getStatusBadge()}
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="flex items-start space-x-2 text-sm">
          <User className="h-4 w-4 mt-0.5 text-gray-500" />
          <div>
            <div className="font-medium">Patient</div>
            <span className="text-gray-700">{patient.firstName} {patient.lastName}</span>
          </div>
        </div>
        <div className="flex items-start space-x-2 text-sm">
          <User className="h-4 w-4 mt-0.5 text-gray-500" />
          <div>
            <div className="font-medium">Doctor</div>
            <span className="text-gray-700">Dr. {doctor.firstName} {doctor.lastName}</span>
            <div className="text-xs text-gray-500">{doctor.specialization}</div>
          </div>
        </div>
        <div className="flex items-start space-x-2 text-sm">
          <Calendar className="h-4 w-4 mt-0.5 text-gray-500" />
          <div>
            <div className="font-medium">Date</div>
            <span className="text-gray-700">{formattedDate}</span>
          </div>
        </div>
        <div className="flex items-start space-x-2 text-sm">
          <Clock className="h-4 w-4 mt-0.5 text-gray-500" />
          <div>
            <div className="font-medium">Time</div>
            <span className="text-gray-700">{appointment.startTime} - {appointment.endTime}</span>
          </div>
        </div>
        {appointment.notes && (
          <div className="flex items-start space-x-2 text-sm">
            <FileText className="h-4 w-4 mt-0.5 text-gray-500" />
            <div>
              <div className="font-medium">Notes</div>
              <span className="text-gray-700">{appointment.notes}</span>
            </div>
          </div>
        )}
      </CardContent>
      <CardFooter className="flex flex-col space-y-2">
        <Button variant="outline" size="sm" asChild className="w-full">
          <Link to={`/appointments/${appointment.id}`}>View Details</Link>
        </Button>

        {appointment.status === 'scheduled' && onStatusChange && (
          <div className="flex space-x-2 w-full">
            <Button
              variant="default"
              size="sm"
              className="flex-1 bg-green-500 hover:bg-green-600"
              onClick={() => onStatusChange(appointment.id, 'completed')}
            >
              Mark Completed
            </Button>
            <Button
              variant="destructive"
              size="sm"
              className="flex-1"
              onClick={() => onStatusChange(appointment.id, 'cancelled')}
            >
              Cancel
            </Button>
          </div>
        )}
      </CardFooter>
    </Card>
  );
};

export default AppointmentCard;
