import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Calendar, Phone, Mail, FileText } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Patient } from '@/types';

interface PatientCardProps {
  patient: Patient;
}

const PatientCard = ({ patient }: PatientCardProps) => {
  return (
    <Card className="h-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">
          {patient.firstName} {patient.lastName}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="flex items-start space-x-2 text-sm">
          <Calendar className="h-4 w-4 mt-0.5 text-gray-500" />
          <span className="text-gray-700">{new Date(patient.dateOfBirth).toLocaleDateString()}</span>
        </div>
        <div className="flex items-start space-x-2 text-sm">
          <Phone className="h-4 w-4 mt-0.5 text-gray-500" />
          <span className="text-gray-700">{patient.phone}</span>
        </div>
        <div className="flex items-start space-x-2 text-sm">
          <Mail className="h-4 w-4 mt-0.5 text-gray-500" />
          <span className="text-gray-700 truncate">{patient.email}</span>
        </div>
        {patient.insuranceProvider && (
          <div className="flex items-start space-x-2 text-sm">
            <FileText className="h-4 w-4 mt-0.5 text-gray-500" />
            <span className="text-gray-700">{patient.insuranceProvider} (ID: {patient.insuranceId})</span>
          </div>
        )}
        <div className="pt-2">
          <Button variant="outline" size="sm" asChild className="w-full">
            <Link to={`/patients/${patient.id}`}>View Profile</Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default PatientCard;