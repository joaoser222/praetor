import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LogOut } from 'lucide-react';
import { Button, Flex, NavLink, Stack, Text } from '@mantine/core';
import type { RouteConfig } from '@/lib/routes';

interface SidebarProps {
    routes: RouteConfig[];
    onLogout: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ routes, onLogout }) => {
    const location = useLocation();
    const appName = import.meta.env.VITE_APP_NAME || 'Praetor';

    return (
        <Flex direction="column" h="100%" justify="space-between">
            <div>
                <Text fw={700} size="xl" c="blue" px="sm" py="md">{appName}</Text>

                <Stack gap={4}>
                    {routes.filter(r => r.showInSidebar).map((route) => {
                        const isActive = location.pathname === route.path;
                        const Icon = route.icon;
                        return (
                            <NavLink
                                key={route.path}
                                component={Link}
                                to={route.path}
                                active={isActive}
                                label={route.label}
                                leftSection={<Icon size={18} />}
                            />
                        );
                    })}
                </Stack>
            </div>

            <Button
                variant="subtle"
                color="red"
                justify="flex-start"
                leftSection={<LogOut size={18} />}
                onClick={onLogout}
            >
                Sair
            </Button>
        </Flex>
    );
};
