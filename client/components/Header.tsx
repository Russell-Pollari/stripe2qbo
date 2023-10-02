import * as React from 'react';
import { Link } from 'react-router-dom';

import { useGetCurrentUserQuery } from '../services/api';
import AccountMenu from './AccountMenu';
import NavMenu from './NavMenu';

const Header = ({ staticMenu }: { staticMenu: boolean }) => {
    const { data: user } = useGetCurrentUserQuery();

    return (
        <div className="fixed z-50 w-full flex justify-start items-center bg-green-300 py-2 px-4 h-16 border-b border-solid border-gray-500">
            {!!user && <NavMenu staticMode={staticMenu} />}
            <h1 className="font-semibold">
                <Link to="/">Stripe2QBO</Link>
            </h1>
            {user && (
                <div className="absolute top-0 right-0 mt-4 mr-4">
                    <AccountMenu user={user} />
                </div>
            )}
        </div>
    );
};

export default Header;
