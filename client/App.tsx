import * as React from 'react';
import { useState, useEffect } from 'react';
import { Outlet, Link } from 'react-router-dom';
import { useMediaQuery } from 'react-responsive';

import AccountMenu from './components/AccountMenu';
import { useGetCurrentUserQuery, useGetCompanyInfoQuery } from './services/api';
import LoadingSpinner from './components/LoadingSpinner';
import NavMenu from './components/NavMenu';

const login = () => {
    fetch('/api/qbo/oauth2')
        .then((response) => response.json())
        .then((data: string) => {
            location.href = data;
        })
        .catch((error) => {
            console.error(error);
        });
};

const App = () => {
    const { data: user_id, isLoading } = useGetCurrentUserQuery();
    const { data: companyInfo } = useGetCompanyInfoQuery('', {
        skip: !user_id,
    });

    const isBigScreen = useMediaQuery({ minWidth: 1040 });

    const [staticMenu, setStaticMenu] = useState<boolean>(isBigScreen);

    useEffect(() => {
        setStaticMenu(isBigScreen);
    }, [isBigScreen]);

    return (
        <div className="bg-gray-50 text-gray-900 oveflow-hidden">
            <div className="fixed z-40 w-full flex justify-start items-center bg-green-300 py-2 px-4 h-16 border-b border-solid border-gray-500">
                <NavMenu staticMode={staticMenu} />
                <h1 className="font-semibold">
                    <Link to="/">Stripe2QBO</Link>
                </h1>
                {companyInfo && (
                    <div className="absolute top-0 right-0 mt-4 mr-4">
                        <AccountMenu companyInfo={companyInfo} />
                    </div>
                )}
            </div>

            {isLoading && (
                <div className="grid h-1/2 place-items-center">
                    <LoadingSpinner className="inline-block w-8 h-8" />
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

            {user_id && (
                <div className="py-2 px-6 flex h-full w-full top-16 absolute overflow-y-auto">
                    {staticMenu && <div className="w-56 mr-8" />}
                    <Outlet />
                </div>
            )}
        </div>
    );
};

export default App;
