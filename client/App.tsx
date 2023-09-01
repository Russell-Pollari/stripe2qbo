import * as React from 'react';

import StripeConnection from './components/StripeConnection';
import SyncSettings from './components/settings/SyncSettings';
import ImportTransactions from './components/ImportTransactions';
import TransactionTable from './components/TransactionTable';
import {
    useGetCurrentUserQuery,
    useGetCompanyInfoQuery,
    useLogoutMutation,
} from './services/api';
import { Menu } from '@headlessui/react';
import { ChevronDownIcon } from '@heroicons/react/24/solid';

const login = () => {
    fetch('/qbo/oauth2')
        .then((response) => response.json())
        .then((data: string) => {
            location.href = data;
        });
};

const AcountMenu = ({ companyInfo, logout }) => {
    return (
        <Menu as="div" className="relative text-left">
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
                                onClick={logout}
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

const App = () => {
    const { data: user_id, isLoading } = useGetCurrentUserQuery();
    const { data: companyInfo } = useGetCompanyInfoQuery('', {
        skip: !user_id,
    });
    const [logout] = useLogoutMutation();

    return (
        <div>
            <div className="flex items-center justify-between bg-green-300 p-4">
                <h1 className="font-semibold text-xl">Stripe 2 QBO</h1>
                {companyInfo && (
                    <AcountMenu companyInfo={companyInfo} logout={logout} />
                )}
            </div>
            {isLoading && <div>Loading...</div>}
            {user_id && (
                <div className="p-6">
                    <div className="flex justify-around">
                        <div className="basis-3/4">
                            <ImportTransactions />
                            <TransactionTable />
                        </div>
                        <div>
                            <StripeConnection />
                            <SyncSettings />
                        </div>
                    </div>
                </div>
            )}
            {!user_id && !isLoading && (
                <div className="grid h-1/2 place-items-center">
                    <button
                        className="inline-block hover:bg-slate-100 text-gray-500 font-bold p-2 rounded-full"
                        onClick={login}
                    >
                        Login with QBO
                    </button>
                </div>
            )}
        </div>
    );
};

export default App;
