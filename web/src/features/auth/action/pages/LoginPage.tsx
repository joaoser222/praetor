import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useNavigate } from 'react-router-dom';
import { isAxiosError } from 'axios';
import { Lock, Mail } from 'lucide-react';
import { notifications } from '@mantine/notifications';
import {
    Button,
    Card,
    Center,
    PasswordInput,
    Stack,
    Text,
    TextInput,
    ThemeIcon,
    Title,
} from '@mantine/core';
import { authService } from '@/features/auth/action/service';
import { loginSchema, type LoginFormValues } from '@/features/auth/action/schema';
import { authMessages } from '@/features/auth/i18n';

const LoginPage: React.FC = () => {
    const navigate = useNavigate();
    const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<LoginFormValues>({
        resolver: zodResolver(loginSchema),
    });

    const onSubmit = async (data: LoginFormValues) => {
        try {
            await authService.login(data);
            notifications.show({ message: authMessages.loginSuccess, color: 'green' });
            navigate('/');
        } catch (error: unknown) {
            const detail = isAxiosError(error)
                ? (error.response?.data as { detail?: string } | undefined)?.detail
                : undefined;
            notifications.show({
                message: detail || authMessages.loginFailed,
                color: 'red',
            });
        }
    };

    return (
        <Center mih="100vh" bg="var(--mantine-color-gray-0)" px="md">
            <Card withBorder shadow="md" radius="lg" padding="xl" w="100%" maw={420}>
                <Stack gap="xs" align="center" mb="lg">
                    <ThemeIcon size={48} radius="md" variant="light">
                        <Lock size={24} />
                    </ThemeIcon>
                    <Title order={1} size="h2">{authMessages.loginTitle}</Title>
                    <Text c="dimmed" size="sm" ta="center">{authMessages.loginSubtitle}</Text>
                </Stack>

                <form onSubmit={handleSubmit(onSubmit)}>
                    <Stack>
                        <TextInput
                            label={authMessages.emailLabel}
                            placeholder="admin@example.com"
                            leftSection={<Mail size={16} />}
                            error={errors.email?.message}
                            {...register('email')}
                        />

                        <PasswordInput
                            label={authMessages.passwordLabel}
                            placeholder="••••••••"
                            leftSection={<Lock size={16} />}
                            error={errors.password?.message}
                            {...register('password')}
                        />

                        <Button type="submit" fullWidth mt="sm" loading={isSubmitting}>
                            {authMessages.signInButton}
                        </Button>
                    </Stack>
                </form>
            </Card>
        </Center>
    );
};

export default LoginPage;
