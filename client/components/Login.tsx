import * as React from 'react';
import { Formik, Form, Field } from 'formik';
import type { FieldProps } from 'formik';
import { object, string } from 'yup';

import SubmitButton from './SubmitButton';
import { useLoginMutation, useSignupMutation } from '../services/api';
import { Link } from 'react-router-dom';

const schema = object().shape({
    email: string().email().required(),
    password: string().required(),
});

const Input = ({
    field,
    placeholder,
    type,
}: {
    field: FieldProps;
    placeholder: string;
    type: string;
}) => {
    return (
        <input
            className="w-full p-2 border border-solid border-green-500 rounded-lg mb-4"
            type={type}
            placeholder={placeholder}
            {...field}
        />
    );
};

const Login = ({
    handleSubmit,
    isSignupForm,
}: {
    handleSubmit: (values: {
        email: string;
        password: string;
    }) => Promise<void>;
    isSignupForm: boolean;
}) => {
    return (
        <div className="absolute flex h-full w-full justify-center top-16">
            <div className="p-8 my-16 rounded-lg bg-green-100 border border-solid border-green-300 shadow-lg h-max text-center relative">
                {isSignupForm && (
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
                )}
                <h1 className="text-2xl text-green-800 font-semibold mb-8 mt-16">
                    Stripe2QBO
                </h1>
                {isSignupForm && (
                    <p className="mb-8 w-64 text-left inline-block">
                        <span className="text-green-700">Stripe2QBO</span> is an
                        open source tool to help you import your Stripe
                        transactions into QuickBooks Online.
                    </p>
                )}
                <div>
                    <Formik
                        initialValues={{ email: '', password: '' }}
                        validationSchema={schema}
                        onSubmit={async (values, { setSubmitting }) => {
                            await handleSubmit(values);
                            setSubmitting(false);
                        }}
                    >
                        {({ isSubmitting }) => (
                            <Form>
                                <div>
                                    <Field
                                        component={Input}
                                        type="email"
                                        name="email"
                                        placeholder="email"
                                    />
                                </div>
                                <div className="my-4">
                                    <Field
                                        component={Input}
                                        type="password"
                                        name="password"
                                        placeholder="password"
                                    />
                                </div>
                                <SubmitButton isSubmitting={isSubmitting}>
                                    {isSignupForm ? 'Signup' : 'Login'}
                                </SubmitButton>
                            </Form>
                        )}
                    </Formik>
                </div>
                <div>
                    <p>
                        {isSignupForm
                            ? 'Already have an account?'
                            : 'No account?'}
                    </p>
                    {isSignupForm ? (
                        <Link to="/" className="text-green-700 text-sm">
                            Login
                        </Link>
                    ) : (
                        <Link to="/signup" className="text-green-700 text-sm">
                            Sign up
                        </Link>
                    )}
                </div>
            </div>
        </div>
    );
};

export const LoginContainer = () => {
    const [login] = useLoginMutation();

    return (
        <Login
            handleSubmit={async (values) => {
                await login(values);
            }}
            isSignupForm={false}
        />
    );
};

export const SignupContainer = () => {
    const [signup] = useSignupMutation();

    return (
        <Login
            handleSubmit={async (values) => {
                await signup(values);
            }}
            isSignupForm={true}
        />
    );
};
