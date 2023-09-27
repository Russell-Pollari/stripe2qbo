import * as React from 'react';
import { Outlet } from 'react-router-dom';

import AccountMenu from './components/AccountMenu';
import { useGetCurrentUserQuery, useGetCompanyInfoQuery } from './services/api';
import Tabs from './components/Tabs';

const login = () => {
    fetch('/api/qbo/oauth2')
        .then((response) => response.json())
        .then((data: string) => {
            location.href = data;
        });
};

const App = () => {
    const { data: user_id, isLoading } = useGetCurrentUserQuery();
    const { data: companyInfo } = useGetCompanyInfoQuery('', {
        skip: !user_id,
    });

    return (
        <div className="bg-gray-50 text-gray-900">
            <div className="flex items-center justify-between bg-green-300 py-2 px-6 h-16">
                <h1 className="font-semibold text-xl">Stripe 2 QBO</h1>
                {companyInfo && <AccountMenu companyInfo={companyInfo} />}
            </div>
            {isLoading && <div>Loading...</div>}
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
            {user_id && (
                <div className="py-2 px-6">
                    <Tabs />
                    <Outlet />
                </div>
            )}
        </div>
    );
};

export default App;
