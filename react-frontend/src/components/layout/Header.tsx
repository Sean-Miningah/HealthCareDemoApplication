import { Heart } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';

const Header = () => {
  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-3 flex items-center justify-between">
        <Link to="/" className="flex items-center space-x-2">
          <Heart className="h-6 w-6 text-primary" />
          <span className="text-xl font-bold text-primary">HealSync</span>
        </Link>

        <nav className="hidden md:flex items-center space-x-6">
          <Link to="/patients" className="text-gray-600 hover:text-primary transition-colors">
            Patients
          </Link>
          <Link to="/doctors" className="text-gray-600 hover:text-primary transition-colors">
            Doctors
          </Link>
          <Link to="/appointments" className="text-gray-600 hover:text-primary transition-colors">
            Appointments
          </Link>
        </nav>

        <div className="flex items-center space-x-4">
          <Button variant="outline" asChild>
            <Link to="/login">Login</Link>
          </Button>
          <Button asChild>
            <Link to="/register">Register</Link>
          </Button>
        </div>
      </div>

      {/* Mobile Navigation - Shows up as a bottom bar on mobile */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50">
        <div className="flex justify-around items-center py-2">
          <Link to="/patients" className="flex flex-col items-center p-2">
            <span className="text-xs">Patients</span>
          </Link>
          <Link to="/doctors" className="flex flex-col items-center p-2">
            <span className="text-xs">Doctors</span>
          </Link>
          <Link to="/appointments" className="flex flex-col items-center p-2">
            <span className="text-xs">Appointments</span>
          </Link>
        </div>
      </div>
    </header>
  );
};

export default Header;
