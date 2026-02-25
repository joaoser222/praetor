import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useNavigate } from 'react-router-dom';
import { Lock, Mail, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { authService } from '../service';
import { loginSchema, type LoginFormValues } from '../schema';
import { authMessages } from '../../i18n';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../../components/ui/card';

const LoginPage: React.FC = () => {
    const navigate = useNavigate();
    const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<LoginFormValues>({
        resolver: zodResolver(loginSchema),
    });

    const onSubmit = async (data: LoginFormValues) => {
        try {
            await authService.login(data);
            toast.success(authMessages.loginSuccess);
            navigate('/');
        } catch (error: any) {
            toast.error(error.response?.data?.detail || authMessages.loginFailed);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-muted/30 py-12 px-4 sm:px-6 lg:px-8">
            <Card className="max-w-md w-full shadow-xl border-border">
                <CardHeader className="text-center space-y-2">
                    <div className="mx-auto h-12 w-12 bg-primary/10 rounded-xl flex items-center justify-center text-primary mb-2">
                        <Lock size={24} />
                    </div>
                    <CardTitle className="text-3xl font-bold tracking-tight">{authMessages.loginTitle}</CardTitle>
                    <CardDescription>{authMessages.loginSubtitle}</CardDescription>
                </CardHeader>

                <CardContent>
                    <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
                        <div className="space-y-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                    {authMessages.emailLabel}
                                </label>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-muted-foreground">
                                        <Mail size={18} />
                                    </div>
                                    <Input
                                        {...register('email')}
                                        type="email"
                                        className="pl-10"
                                        placeholder="admin@example.com"
                                    />
                                </div>
                                {errors.email && <p className="text-xs font-medium text-destructive">{errors.email.message}</p>}
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                    {authMessages.passwordLabel}
                                </label>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-muted-foreground">
                                        <Lock size={18} />
                                    </div>
                                    <Input
                                        {...register('password')}
                                        type="password"
                                        className="pl-10"
                                        placeholder="••••••••"
                                    />
                                </div>
                                {errors.password && <p className="text-xs font-medium text-destructive">{errors.password.message}</p>}
                            </div>
                        </div>

                        <Button
                            type="submit"
                            className="w-full"
                            disabled={isSubmitting}
                        >
                            {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                            {authMessages.signInButton}
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
};

export default LoginPage;
