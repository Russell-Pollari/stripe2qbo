import * as React from 'react';
import { NavLink } from 'react-router-dom';
import { Menu } from '@headlessui/react';
import { Bars3Icon, HomeIcon, CogIcon } from '@heroicons/react/24/solid';

const Item = ({
    label,
    to,
    icon,
}: {
    label: string;
    to: string;
    icon: React.ReactNode;
}) => {
    return (
        <Menu.Item>
            {({ active: hover }) => (
                <NavLink
                    to={to}
                    className={({ isActive }) => `
                        ${isActive ? 'text-green-600' : 'text-gray-700'}
                        ${hover ? 'bg-green-100' : ''}
                        block px-4 py-2
                    `}
                >
                    {icon}
                    {label}
                </NavLink>
            )}
        </Menu.Item>
    );
};

const iconClassName = 'w-6 h-6 inline mr-2 -mt-px';

const NavMenu = ({ staticMode }: { staticMode: boolean }) => {
    return (
        <Menu>
            {!staticMode && (
                <Menu.Button className="text-gray-700 hover:text-gray-900">
                    <Bars3Icon className="w-6 h-6 mr-2" />
                </Menu.Button>
            )}
            <Menu.Items
                static={staticMode}
                as="div"
                className="fixed left-0 top-16 z-50 h-screen w-56 py-4 bg-gray-50 border-r border-solid border-gray-500"
            >
                <Item
                    label="Dashboard"
                    to="/"
                    icon={<HomeIcon className={iconClassName} />}
                />
                <Item
                    label="Settings"
                    to="/settings"
                    icon={<CogIcon className={iconClassName} />}
                />
            </Menu.Items>
        </Menu>
    );
};

export default NavMenu;
