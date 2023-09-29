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
            className="bg-green-500 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-full shadow-lg text-sm"
            disabled={isSubmitting}
        >
            {children}
        </button>
    );
};

export default SubmitButton;
