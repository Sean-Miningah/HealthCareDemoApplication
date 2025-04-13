import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Appointment } from '@/types';
// import { toast } from 'sonner';
import { doctors, patients } from '@/data/mockData';
import { addDays, format } from 'date-fns';

const appointmentSchema = z.object({
  patientId: z.string().min(1, { message: 'Please select a patient' }),
  doctorId: z.string().min(1, { message: 'Please select a doctor' }),
  date: z.string().min(1, { message: 'Please select a date' }),
  startTime: z.string().min(1, { message: 'Please select a start time' }),
  notes: z.string().optional(),
});

type AppointmentFormValues = z.infer<typeof appointmentSchema>;

interface AppointmentFormProps {
  initialData?: Omit<Appointment, 'id' | 'status'>;
  onSubmit: (data: AppointmentFormValues & { endTime: string }) => void;
  isLoading?: boolean;
}

// Helper function to get available days for a doctor
const getAvailableDays = (doctorId: string) => {
  const doctor = doctors.find(d => d.id === doctorId);
  if (!doctor) return [];

  const today = new Date();
  const availableDays = [];

  // Check next 14 days
  for (let i = 0; i < 14; i++) {
    const date = addDays(today, i);
    const dayName = format(date, 'EEEE'); // Get day name (Monday, Tuesday, etc)

    if (doctor.availability.some(a => a.day === dayName)) {
      availableDays.push({
        date: format(date, 'yyyy-MM-dd'),
        dayName
      });
    }
  }

  return availableDays;
};

// Helper function to get available time slots for a doctor on a specific day
const getAvailableTimeSlots = (doctorId: string, date: string) => {
  const doctor = doctors.find(d => d.id === doctorId);
  if (!doctor) return [];

  const dayName = format(new Date(date), 'EEEE');
  const dayAvailability = doctor.availability.find(a => a.day === dayName);

  if (!dayAvailability) return [];

  // Create 30-minute time slots
  const slots = [];
  let currentTime = dayAvailability.startTime;

  while (currentTime < dayAvailability.endTime) {
    // Parse hours and minutes
    const [hours, minutes] = currentTime.split(':').map(Number);

    // Current slot
    slots.push(currentTime);

    // Calculate next slot (add 30 minutes)
    let newMinutes = minutes + 30;
    let newHours = hours;

    if (newMinutes >= 60) {
      newMinutes -= 60;
      newHours += 1;
    }

    // Format new time
    currentTime = `${newHours.toString().padStart(2, '0')}:${newMinutes.toString().padStart(2, '0')}`;
  }

  return slots;
};

// Helper function to calculate end time (30 min appointments)
const calculateEndTime = (startTime: string) => {
  const [hours, minutes] = startTime.split(':').map(Number);

  let newMinutes = minutes + 30;
  let newHours = hours;

  if (newMinutes >= 60) {
    newMinutes -= 60;
    newHours += 1;
  }

  return `${newHours.toString().padStart(2, '0')}:${newMinutes.toString().padStart(2, '0')}`;
};

const AppointmentForm = ({ initialData, onSubmit, isLoading = false }: AppointmentFormProps) => {
  const [availableDays, setAvailableDays] = useState<Array<{ date: string; dayName: string }>>([]);
  const [availableTimeSlots, setAvailableTimeSlots] = useState<string[]>([]);

  const form = useForm<AppointmentFormValues>({
    resolver: zodResolver(appointmentSchema),
    defaultValues: initialData || {
      patientId: '',
      doctorId: '',
      date: '',
      startTime: '',
      notes: '',
    },
  });

  const watchDoctorId = form.watch('doctorId');
  const watchDate = form.watch('date');

  // Update available days when doctor changes
  useEffect(() => {
    if (watchDoctorId) {
      const days = getAvailableDays(watchDoctorId);
      setAvailableDays(days);

      if (!days.some(d => d.date === watchDate)) {
        form.setValue('date', '');
        form.setValue('startTime', '');
      }
    } else {
      setAvailableDays([]);
      form.setValue('date', '');
      form.setValue('startTime', '');
    }
  }, [watchDoctorId, form, watchDate]);

  // Update available time slots when date changes
  useEffect(() => {
    if (watchDoctorId && watchDate) {
      const timeSlots = getAvailableTimeSlots(watchDoctorId, watchDate);
      setAvailableTimeSlots(timeSlots);

      if (!timeSlots.includes(form.getValues('startTime'))) {
        form.setValue('startTime', '');
      }
    } else {
      setAvailableTimeSlots([]);
      form.setValue('startTime', '');
    }
  }, [watchDoctorId, watchDate, form]);

  const handleSubmit = (values: AppointmentFormValues) => {
    const endTime = calculateEndTime(values.startTime);
    onSubmit({ ...values, endTime });
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="patientId"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Patient *</FormLabel>
              <Select
                onValueChange={field.onChange}
                defaultValue={field.value}
              >
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select patient" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {patients.map((patient) => (
                    <SelectItem key={patient.id} value={patient.id}>
                      {patient.firstName} {patient.lastName}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="doctorId"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Doctor *</FormLabel>
              <Select
                onValueChange={field.onChange}
                defaultValue={field.value}
              >
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select doctor" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {doctors.map((doctor) => (
                    <SelectItem key={doctor.id} value={doctor.id}>
                      Dr. {doctor.firstName} {doctor.lastName} ({doctor.specialization})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="date"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Date *</FormLabel>
              <Select
                onValueChange={field.onChange}
                defaultValue={field.value}
                disabled={!watchDoctorId}
              >
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder={
                      !watchDoctorId
                        ? "Select a doctor first"
                        : availableDays.length === 0
                          ? "No available days"
                          : "Select date"
                    } />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {availableDays.map((day) => (
                    <SelectItem key={day.date} value={day.date}>
                      {format(new Date(day.date), 'EEE, MMM d, yyyy')}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="startTime"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Time *</FormLabel>
              <Select
                onValueChange={field.onChange}
                defaultValue={field.value}
                disabled={!watchDate}
              >
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder={
                      !watchDoctorId
                        ? "Select a doctor first"
                        : !watchDate
                          ? "Select a date first"
                          : availableTimeSlots.length === 0
                            ? "No available times"
                            : "Select time"
                    } />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {availableTimeSlots.map((time) => (
                    <SelectItem key={time} value={time}>
                      {time} - {calculateEndTime(time)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="notes"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Notes</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Any important details about the appointment"
                  className="resize-none min-h-[100px]"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" className="w-full" disabled={isLoading}>
          {isLoading ? 'Processing...' : 'Schedule Appointment'}
        </Button>
      </form>
    </Form>
  );
};

export default AppointmentForm;