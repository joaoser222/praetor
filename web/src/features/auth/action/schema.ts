import * as z from 'zod';
import { zodMessages } from '../../../lib/i18n';

export const loginSchema = z.object({
    email: z.string().email(zodMessages.invalidEmail),
    password: z.string().min(6, zodMessages.tooShort('Password', 6)),
});

export type LoginFormValues = z.infer<typeof loginSchema>;
