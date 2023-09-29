import * as React from 'react';
import { Menu } from '@headlessui/react';
import { ChevronDownIcon } from '@heroicons/react/24/solid';

import { useLogoutMutation } from '../services/api';

const AccountMenu = ({ companyInfo }) => {
    const [logout] = useLogoutMutation();

    return (
        <Menu as="div" className="relative text-left z-50">
            <Menu.Button className="inline-flex w-full justify-center rounded-md bg-black bg-opacity-20 px-4 py-2 text-sm font-medium text-white hover:bg-opacity-30 focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75">
                {companyInfo.CompanyName} ({companyInfo.Country})
                <ChevronDownIcon
                    className="ml-2 -mr-1 h-5 w-5 text-violet-200 hover:text-violet-100"
                    aria-hidden="true"
                />
            </Menu.Button>
            <Menu.Items className="absolute right-0 mt-2 w-56 origin-top-right divide-y divide-gray-100 rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                <div className="px-1 py-1">
                    <Menu.Item>
                        {({ active }) => (
                            <button
                                onClick={async () =>
                                    logout().then(() => {
                                        location.reload();
                                    })
                                }
                                className={`${
                                    active
                                        ? 'bg-gray-500 text-white'
                                        : 'text-gray-900'
                                } group flex w-full items-center rounded-md px-2 py-2 text-sm`}
                            >
                                Logout
                            </button>
                        )}
                    </Menu.Item>
                </div>
            </Menu.Items>
        </Menu>
    );
};

export default AccountMenu;
