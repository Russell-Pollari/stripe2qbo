import * as React from 'react';
import { Formik, Form, Field } from 'formik';
import SubmitButton from './SubmitButton';

import { useLoginMutation } from '../services/api';

const Login = () => {
    const [login] = useLoginMutation();

    return (
        <div className="absolute flex h-full w-full justify-center top-16">
            <div className="p-8 my-16 rounded-lg bg-green-100 border border-solid border-green-300 shadow-lg h-max text-center relative">
                <a href="https://github.com/Russell-Pollari/stripe2qbo">
                    <img
                        decoding="async"
                        width="149"
                        height="149"
                        src="https://github.blog/wp-content/uploads/2008/12/forkme_right_gray_6d6d6d.png?resize=149%2C149"
                        alt="Fork me on GitHub"
                        loading="lazy"
                        className="absolute top-0 right-0 border-0"
                        data-recalc-dims="1"
                    />
                </a>
                <h1 className="text-2xl text-green-800 font-semibold mb-8 mt-16">
                    Stripe2QBO
                </h1>
                <p className="mb-8 w-64 text-left inline-block">
                    <span className="text-green-700">Stripe2QBO</span> is an
                    open source tool to help you import your Stripe transactions
                    into QuickBooks Online.
                </p>
                <div>
                    <Formik
                        initialValues={{ email: '', password: '' }}
                        onSubmit={async (values, { setSubmitting }) => {
                            await login(values);
                            setSubmitting(false);
                        }}
                    >
                        {({ isSubmitting }) => (
                            <Form>
                                <div>
                                    <Field
                                        type="email"
                                        name="email"
                                        placeholder="email"
                                    />
                                </div>
                                <div className="my-4">
                                    <Field
                                        type="password"
                                        name="password"
                                        placeholder="password"
                                    />
                                </div>
                                <SubmitButton isSubmitting={isSubmitting}>
                                    Login
                                </SubmitButton>
                            </Form>
                        )}
                    </Formik>
                </div>
            </div>
        </div>
    );
};

export default Login;
