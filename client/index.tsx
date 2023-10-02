import * as React from 'react';
import { createRoot } from 'react-dom/client';
import { Provider } from 'react-redux';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';

import { store } from './store/store';
import App from './App';
import SettingsPage from './pages/SettingsPage';
import SignupPage from './pages/SignupPage';
import TransactionsPage from './pages/TransactionsPage';
import QBOCallback from './pages/QBOCallback';
import StripeCallback from './pages/StripeCallback';

const router = createBrowserRouter([
    {
        path: '/',
        element: <App />,
        children: [
            {
                path: '/',
                element: <TransactionsPage />,
            },
            {
                path: '/settings',
                element: <SettingsPage />,
            },
            {
                path: '/qbo/oauth2/callback',
                element: <QBOCallback />,
            },
            {
                path: '/stripe/oauth2/callback',
                element: <StripeCallback />,
            },
        ],
    },
    {
        path: '/signup',
        element: <SignupPage />,
    },
]);

// eslint-disable-next-line @typescript-eslint/no-non-null-assertion
const root = createRoot(document.getElementById('root')!);

root.render(
    <Provider store={store}>
        <RouterProvider router={router} />
    </Provider>
);
