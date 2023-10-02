import * as React from 'react';

import { useGetCurrentUserQuery } from '../services/api';
import { SignupContainer } from '../components/Login';
import Header from '../components/Header';

const SignupPage = () => {
    const { data: isLoggedIn } = useGetCurrentUserQuery();
    if (isLoggedIn) {
        location.href = '/';
    }

    return (
        <div className="bg-green-100">
            <Header staticMenu={false} />
            <SignupContainer />
        </div>
    );
};

export default SignupPage;
