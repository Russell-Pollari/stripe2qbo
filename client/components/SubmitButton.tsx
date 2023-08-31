import * as React from 'react';

const SubmitButton = ({
    isSubmitting,
    children,
}: {
    isSubmitting: boolean;
    children: React.ReactNode;
}) => {
    return (
        <button
            type="submit"
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded m-auto"
            disabled={isSubmitting}
        >
            {children}
        </button>
    );
};

export default SubmitButton;
