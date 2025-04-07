import { Heart } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-accent mt-auto py-6 md:py-10">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="flex items-center space-x-2 mb-4 md:mb-0">
            <Heart className="h-5 w-5 text-primary" />
            <span className="text-lg font-bold text-primary">HealSync</span>
          </div>

          <div className="text-center md:text-right">
            <p className="text-sm text-gray-600">
              &copy; {new Date().getFullYear()} HealSync. All rights reserved.
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Healthcare appointment scheduling system
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
