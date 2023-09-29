import * as React from 'react';
import { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { useMediaQuery } from 'react-responsive';

import { useGetCurrentUserQuery } from './services/api';
import LoadingSpinner from './components/LoadingSpinner';
import Login from './components/Login';
import Header from './components/Header';

const App = () => {
    const { data: isLoggedIn, isLoading } = useGetCurrentUserQuery();

    const isBigScreen = useMediaQuery({ minWidth: 1040 });
    const [staticMenu, setStaticMenu] = useState<boolean>(isBigScreen);

    useEffect(() => {
        setStaticMenu(isBigScreen);
    }, [isBigScreen]);

    return (
        <div className="bg-gray-50 text-gray-900">
            <Header staticMenu={staticMenu} />

            {isLoading && (
                <div className="grid h-1/2 place-items-center">
                    <LoadingSpinner className="inline-block w-8 h-8" />
                </div>
            )}

            {!isLoggedIn && !isLoading && <Login />}

            {isLoggedIn && (
                <div className="px-6 flex w-full h-full pt-16">
                    {staticMenu && <div className="w-56 mr-8" />}
                    <Outlet />
                </div>
            )}
        </div>
    );
};

export default App;
