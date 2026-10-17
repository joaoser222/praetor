import React from 'react';
import { Avatar, Group, Text } from '@mantine/core';

export const Header: React.FC = () => {
    return (
        <Group h="100%" px="md" justify="flex-end">
            <Group gap="sm">
                <Text size="sm" fw={500}>Administrador</Text>
                <Avatar color="blue" radius="xl">A</Avatar>
            </Group>
        </Group>
    );
};
