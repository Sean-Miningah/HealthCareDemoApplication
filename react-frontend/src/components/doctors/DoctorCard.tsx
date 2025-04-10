import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Phone, Mail, Briefcase, Award } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Doctor } from '@/types';
import { Badge } from '@/components/ui/badge';

interface DoctorCardProps {
  doctor: Doctor;
}

const DoctorCard = ({ doctor }: DoctorCardProps) => {
  return (
    <Card className="h-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">
          Dr. {doctor.firstName} {doctor.lastName}
        </CardTitle>
        <Badge variant="secondary">{doctor.specialization}</Badge>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="flex items-start space-x-2 text-sm">
          <Award className="h-4 w-4 mt-0.5 text-gray-500" />
          <span className="text-gray-700">{doctor.qualifications}</span>
        </div>
        <div className="flex items-start space-x-2 text-sm">
          <Phone className="h-4 w-4 mt-0.5 text-gray-500" />
          <span className="text-gray-700">{doctor.phone}</span>
        </div>
        <div className="flex items-start space-x-2 text-sm">
          <Mail className="h-4 w-4 mt-0.5 text-gray-500" />
          <span className="text-gray-700 truncate">{doctor.email}</span>
        </div>
        <div>
          <h4 className="text-sm font-medium mb-1 flex items-center">
            <Briefcase className="h-4 w-4 mr-1 text-gray-500" />
            Availability
          </h4>
          <div className="flex flex-wrap gap-1">
            {doctor.availability.map((a, idx) => (
              <Badge key={idx} variant="outline" className="text-xs">
                {a.day} ({a.startTime}-{a.endTime})
              </Badge>
            ))}
          </div>
        </div>
        <div className="pt-3">
          <Button variant="outline" size="sm" asChild className="w-full">
            <Link to={`/doctors/${doctor.id}`}>View Profile</Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default DoctorCard;