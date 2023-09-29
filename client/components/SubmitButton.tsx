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
            className={`
                ${
                    isSubmitting
                        ? 'bg-green-100 cursor-not-allowed text-gray-500'
                        : 'bg-green-500 hover:bg-green-700 shadow-lg text-white'
                }
                font-semibold py-2 px-4 rounded-full text-sm
            `}
            disabled={isSubmitting}
        >
            {children}
        </button>
    );
};

export default SubmitButton;
