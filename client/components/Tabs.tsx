import * as React from 'react';
import { NavLink } from 'react-router-dom';

import { Tab } from '@headlessui/react';

const NavTab = ({ to, label }: { to: string; label }) => {
    return (
        <Tab>
            <NavLink
                to={to}
                className={({ isActive }) =>
                    `${!!isActive && 'text-black border-green-400'}
                            mr-2 inline-block p-4 border-b-2 rounded-t-lg hover:text-gray-600 hover:border-green-300`
                }
            >
                {label}
            </NavLink>
        </Tab>
    );
};

const Tabs = () => {
    return (
        <Tab.Group
            as="div"
            className="text-sm font-medium text-center text-gray-500 border-b border-gray-200 mb-2"
        >
            <Tab.List className="flex flex-wrap -mb-px">
                <NavTab to="/" label="Transactions" />
                <NavTab to="/settings" label="Settings" />
            </Tab.List>
        </Tab.Group>
    );
};

export default Tabs;
